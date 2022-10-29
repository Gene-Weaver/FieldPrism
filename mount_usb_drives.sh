#!/bin/bash 
echo ""
echo "***** Attempting to Mount USB Drives..."  
echo ""
echo "***** View USB Devices..."  
echo "***** If USB storage is not in list below, then the USB drive is likely formatted incorrectly." 
lsusb 
echo ""
echo "***** View Mounting Points from Previous Use..."
ls /media/
echo ""
echo "***** Un-Mounting USB Drives..."
pumount /dev/sda1
pumount /dev/sdb1
pumount /dev/sdc1
pumount /dev/sdd1
pumount /dev/sde1
pumount /dev/sdf1
echo ""
echo "***** Removing Prior Mount Locations..."
rm -rf /media/pi
rm -rf /media/USB1
rm -rf /media/USB2
rm -rf /media/USB3
rm -rf /media/USB4
rm -rf /media/USB5
rm -rf /media/USB6
echo ""
echo "***** View CURRENT Mounting Points..."
ls /media/
echo ""
echo "***** Mounting USB Drives..."
######### USB 1 ############
if [ -e /dev/sda1 ] ; then
echo "USB1 mounted"
pmount -w /dev/sda1 USB1
else
echo "USB1 not connected"
fi
######### USB 2 ############
if [ -e /dev/sdb1 ] ; then
echo "USB2 mounted"
pmount -w /dev/sdb1 USB2
else
echo "USB2 not connected"
fi
######### USB 3 ############
if [ -e /dev/sdc1 ] ; then
echo "USB3 mounted"
pmount -w /dev/sdc1 USB3
else
echo "USB3 not connected"
fi
######### USB 4 ############
if [ -e /dev/sdd1 ] ; then
echo "USB4 mounted"
pmount -w /dev/sdd1 USB4
else
echo "USB4 not connected"
fi
######### USB 5 ############
if [ -e /dev/sde1 ] ; then
echo "USB5 mounted"
pmount -w /dev/sde1 USB5
else
echo "USB5 not connected"
fi
######### USB 6 ############
if [ -e /dev/sdf1 ] ; then
echo "USB6 mounted"
pmount -w /dev/sdf1 USB6
else
echo "USB6 not connected"
fi
#pmount -w /dev/sda1 USB1
#pmount -w /dev/sdb1 USB2
#pmount -w /dev/sdc1 USB3
#pmount -w /dev/sdd1 USB4
#pmount -w /dev/sde1 USB5
#pmount -w /dev/sdf1 USB6
echo ""
echo "***** If below is empty, then no drives were mounted. If non-empty, success."
echo " ls /media/"
ls /media/
echo " ls /media/USB1..."
ls /media/USB1
echo " ls /media/USB2..."
ls /media/USB2
echo " ls /media/USB3..."
ls /media/USB3
echo " ls /media/USB4..."
ls /media/USB4
echo " ls /media/USB5..."
ls /media/USB5
echo " ls /media/USB6..."
ls /media/USB6
echo ""
echo "***** Granting xhost privileges..."
xhost +si:localuser:pi
xhost +si:localuser:root
echo ""
echo "***** View Mounting Points..."
ls /media/
echo ""
echo "***** Possible Errors..."
echo "      Expected errors if not all USB drives are present (not a problem):"  
echo "            --> Error: device /dev/sdb1 is not mounted"
echo "            --> Error: device /dev/sdb1 does not exist"
echo "      Expected errors if not using a USB hub (not a problem):"  
echo "            --> ls: cannot access '/media/USB3': No such file or directory"
echo ""
echo "***** Errors Thrown Below..."
