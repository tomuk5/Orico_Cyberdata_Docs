**Instructions for Truenas SCALE usage**
#
**Please note these LED mappings may be different on your CF56-Pro**
#
Create a Dataset on a pool called Orico_Utils and download the contents of the CF56-Pro folder in github into that Dataset. 
(You can use the command `wget -qO- https://github.com/tomuk5/Orico_Cyberdata_Docs/archive/refs/heads/main.tar.gz | tar -xzv --strip-components=2 "Orico_Cyberdata_Docs-main/CF56-Pro"` if you are in a terminal and already inside the destination folder.)

TrueNAS SCALE does not create /dev/disk/by-bay automatically.
The LED daemon depends on these mappings to associate disks with physical bays.

Edit the systemd/led-daemon.service file to replace `YOUR_POOL_NAME` with your actual pool name.


In the Truenas UI go to *System Settings -> Advanced -> Init/Shutdown Scripts*

Add a *Post-Init* script of Type *Command*

Enter the below into the command box (and replace `YOUR_POOL_NAME` with your actual pool name):

`bash cp /mnt/YOUR_POOL_NAME/Orico_Utils/systemd/led-daemon.service /etc/systemd/system/ && bash cp /mnt/YOUR_POOL_NAME/Orico_Utils/udev/99-orico-bays.rules /etc/udev/rules.d/ && udevadm control --reload-rules && udevadm trigger && systemctl daemon-reload && systemctl enable --now led-daemon.service`

This ensures that the udev rules and service persists beyond a reboot and OS updates.

You can then reboot your Truenas Instance for this to take effect or execute the command `systemctl start led-daemon.service` from the shell using Sudo for it to take effect without a restart.
