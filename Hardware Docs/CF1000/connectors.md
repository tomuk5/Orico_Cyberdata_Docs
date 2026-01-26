***Connectors***
-

**Fans**

Fan connectors on the board are 4pin JST XH (2.5mm pitch between pins) connectors in the same pinout orientation as normal 4 pin pc fan - (WIP)

Both rear case fans share the same PWM (CTL) drive pin and only SYS_FAN1 has the tacho pin connected for fan speed feedback.

**SAS connectors**
- Bays 6-10 connected to board SAS port 1 (shorter cable to the foremost port)
- Bays 1-5 connected to board SAS port 2 (longer cable to the backmost port)

This aligns with the front-panel LED mappings from the OEM config file in OricoOS.

**Front USB header**

There is a JST SH (1.0mm pitch between pins) 4 pin header at the front of the board for a USB 2.0 header (untested)

**Debug serial**

There is a 4pin JST XH (2.5mm pitch between pins) towards the front right of the board for Serial Debug (pinout shown on the PCB silk screen). (signalling voltage and function as yet untested)