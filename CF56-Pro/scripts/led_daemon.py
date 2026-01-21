import time
import os
import struct
import mmap
import subprocess

# mappings [Blue_Reg, Blue_On, Blue_Off, Red_Reg, Red_On, Red_Off]
BAY_CONFIG = {
    "bay1":  [0xFD6D07C0, 0x04000202, 0x04000203, 0xFD6D07D0, 0x04000202, 0x04000203],
    "bay2":  [0xFD6D0930, 0x04000202, 0x04000203, 0xFD6D07F0, 0x04000200, 0x04000201],
    "bay3":  [0xFD6D0900, 0x04000200, 0x04000201, 0xFD6D0910, 0x04000200, 0x04000201],
    "bay4":  [0xFD6D0720, 0x04000200, 0x04000201, 0xFD6D0A30, 0x04000200, 0x04000201],
    "bay5":  [0xFD6D0700, 0x04000200, 0x04000201, 0xFD6D0710, 0x04000200, 0x04000201],
}

class LEDController:
    def __init__(self):
        self.fd = os.open("/dev/mem", os.O_RDWR | os.O_SYNC)
        self.page_size = os.sysconf("SC_PAGE_SIZE")
        self.mm_cache = {}

    def _get_mm(self, addr):
        base_addr = addr & ~(self.page_size - 1)
        if base_addr not in self.mm_cache:
            self.mm_cache[base_addr] = mmap.mmap(self.fd, self.page_size, offset=base_addr)
        return self.mm_cache[base_addr], addr - base_addr

    def write_reg(self, addr, val):
        mm, offset = self._get_mm(addr)
        mm.seek(offset)
        mm.write(struct.pack("<I", val))

    def initialize_leds(self):
        for cfg in BAY_CONFIG.values():
            self.write_reg(cfg[0], cfg[2])
            self.write_reg(cfg[3], cfg[5])

    def close(self):
        self.initialize_leds()
        for mm in self.mm_cache.values(): mm.close()
        os.close(self.fd)

def get_active_pools():
    try: return os.listdir("/proc/spl/kstat/zfs/")
    except: return []

def get_pool_health(pools):
    for pool in pools:
        try:
            with open(f"/proc/spl/kstat/zfs/{pool}/state", "r") as f:
                if f.read().strip() != "ONLINE": return False
        except: continue
    return True

def get_degraded_disks():
    degraded = []
    try:
        output = subprocess.check_output(["zpool", "status", "-L"], stderr=subprocess.STDOUT).decode()
        for line in output.split('\n'):
            if any(state in line for state in ["DEGRADED", "FAULTED", "OFFLINE", "UNAVAIL"]):
                parts = line.split()
                if parts: degraded.append(parts[0])
    except: pass
    return degraded

def main():
    ctrl = LEDController()
    ctrl.initialize_leds()
    last_io, zfs_check_timer, degraded_disks = {}, 0, []
    pools = get_active_pools()

    try:
        while True:
            if time.time() - zfs_check_timer > 3:
                degraded_disks = get_degraded_disks() if not get_pool_health(pools) else []
                zfs_check_timer = time.time()

            bay_to_dev = {}
            for i in range(1, 6):
                bay_id = f"bay{i}"
                path = f"/dev/disk/by-bay/{bay_id}"
                if os.path.exists(path):
                    real_dev = os.path.basename(os.readlink(path))
                    bay_to_dev[bay_id] = real_dev
                    if real_dev in degraded_disks:
                        blink = (int(time.time() * 2) % 2 == 0)
                        ctrl.write_reg(BAY_CONFIG[bay_id][3], BAY_CONFIG[bay_id][4 if blink else 5])
                    else:
                        ctrl.write_reg(BAY_CONFIG[bay_id][3], BAY_CONFIG[bay_id][5])
                else:
                    ctrl.write_reg(BAY_CONFIG[bay_id][0], BAY_CONFIG[bay_id][2])
                    ctrl.write_reg(BAY_CONFIG[bay_id][3], BAY_CONFIG[bay_id][5])

            with open("/proc/diskstats", "r") as f:
                for line in f:
                    parts = line.split()
                    if len(parts) < 13: continue
                    dev_name, io_ticks = parts[2], int(parts[12])
                    for bay_id, mapped_sd in bay_to_dev.items():
                        if dev_name == mapped_sd:
                            if io_ticks > last_io.get(dev_name, 0):
                                ctrl.write_reg(BAY_CONFIG[bay_id][0], BAY_CONFIG[bay_id][1])
                            else:
                                ctrl.write_reg(BAY_CONFIG[bay_id][0], BAY_CONFIG[bay_id][2])
                            last_io[dev_name] = io_ticks
            time.sleep(0.05)
    except KeyboardInterrupt: ctrl.close()

if __name__ == "__main__": main()
