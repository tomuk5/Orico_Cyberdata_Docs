**Instructions for Truenas SCALE usage**



Create a Dataset on a pool called Orico_Utils and copy the contents of the CF1000 folder in github into that Dataset.

In the Truenas UI go to *System Settings -> Advanced -> Init/Shutdown Scripts*

Add a *Post-Init* script of Type *Command*

Enter the below into the command box:

`bash cp /mnt/YOUR_POOL_NAME/Orico_Utils/scripts/led-daemon.service /etc/systemd/system/ && systemctl daemon-reload && systemctl enable --now led-daemon.service`

This ensures that the service persists beyond a reboot and OS updates.

You can then reboot your Truenas Instance for this to take effect or execute the command from the shell using Sudo for it to take effect without a restart.
