#!/bin/bash 
echo ""
echo "***** Attempting to Mount USB Drives..."  
echo ""
echo "***** View USB Devices..."  
echo "***** If USB storage is not in list below, then the USB drive is likely formatted incorrectly." 
lsusb 
echo ""
echo "***** View Mounting Points..."
ls /media/
echo ""
echo "***** Un-Mounting USB Drives..."
pumount /dev/sda1
pumount /dev/sdb1
pumount /dev/sdc1
pumount /dev/sdd1
echo ""
echo "***** Mounting USB Drives..."
pmount -w /dev/sda1 USB1
pmount -w /dev/sdb1 USB2
pmount -w /dev/sdc1 USB3
pmount -w /dev/sdd1 USB4
echo ""
echo "***** If below is empty, then no drives were mounted. If non-empty, success."
ls /media/
ls /media/USB1
ls /media/USB2
ls /media/USB3
ls /media/USB4
echo ""
echo "***** Granting xhost privileges..."
xhost +si:localuser:pi
xhost +si:localuser:root
#chown -R localuser:pi /media/USB1
#chown -R localuser:pi /media/USB2
#chown -R localuser:root /media/USB1
#chown -R localuser:root /media/USB2
echo ""
echo "***** Finished"  
echo ""
echo ""
echo "***** Possible Errors..."
echo "      Expected errors if not all USB drives are presnet (not a problem):"  
echo "            --> Error: device /dev/sdb1 is not mounted"
echo "            --> Error: device /dev/sdb1 does not exist"
echo ""
echo "***** Errors Thrown Below..."
