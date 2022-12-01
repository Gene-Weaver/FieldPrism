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
echo "***** Granting xhost privileges..."
xhost +si:localuser:pi
xhost +si:localuser:root


echo ""
echo "***** Un-Mounting USB Drives..."
#pumount /dev/sda1
#pumount /dev/sdb1
#pumount /dev/sdc1
#pumount /dev/sdd1
#pumount /dev/sde1
#pumount /dev/sdf1
######### USB 1 ############
if [ -e /dev/sda1 ] ; then
echo "USB1 UN-mounted"
pumount /dev/sda1
else
echo "USB1 not connected"
fi
######### USB 2 ############
if [ -e /dev/sdb1 ]; then
echo "USB2 UN-mounted"
pumount /dev/sdb1
else
echo "USB2 not connected"
fi
######### USB 3 ############
if [ -e /dev/sdc1 ]; then
echo "USB3 UN-mounted"
pumount /dev/sdc1
else
echo "USB3 not connected"
fi
######### USB 4 ############
if [ -e /dev/sdd1 ]; then
echo "USB4 UN-mounted"
pumount /dev/sdd1
else
echo "USB4 not connected"
fi
######### USB 5 ############
if [ -e /dev/sde1 ]; then
echo "USB5 UN-mounted"
pumount /dev/sde1
else
echo "USB5 not connected"
fi
######### USB 6 ############
if [ -e /dev/sdf1 ]; then
echo "USB6 UN-mounted"
pumount /dev/sdf1
else
echo "USB6 not connected"
fi


echo ""
echo "***** Removing Prior Mount Locations..."
rm -rf /media/USB1
rm -rf /media/USB2
rm -rf /media/USB3
rm -rf /media/USB4
rm -rf /media/USB5
rm -rf /media/USB6


echo ""
echo "***** View EMPTY Mounting Points, should only see 'pi'..."
ls /media/
echo ""
echo "***** Mounting USB Drives..."
#pmount -w /dev/sda1 USB1
#pmount -w /dev/sdb1 USB2
#pmount -w /dev/sdc1 USB3
#pmount -w /dev/sdd1 USB4
#pmount -w /dev/sde1 USB5
#pmount -w /dev/sdf1 USB6
######### USB 1 ############
if [ -e /dev/sda1 ] ; then
echo "USB1 mounted"
pmount -w /dev/sda1 /media/USB1
# sudo e2label /dev/sda1 USB1
# sudo dosfslabel /dev/sda1 USB1
else
echo "USB1 not connected"
fi
######### USB 2 ############
if [ -e /dev/sdb1 ] ; then
echo "USB2 mounted"
pmount -w /dev/sdb1 /media/USB2
# sudo e2label /dev/sdb1 USB2
# sudo dosfslabel /dev/sdb1 USB2
else
echo "USB2 not connected"
fi
######### USB 3 ############
if [ -e /dev/sdc1 ] ; then
echo "USB3 mounted"
pmount -w /dev/sdc1 /media/USB3
# sudo e2label /dev/sdc1 USB3
# sudo dosfslabel /dev/sdc1 USB3
else
echo "USB3 not connected"
fi
######### USB 4 ############
if [ -e /dev/sdd1 ] ; then
echo "USB4 mounted"
pmount -w /dev/sdd1 /media/USB4
# sudo e2label /dev/sdd1 USB4
# sudo dosfslabel /dev/sdd1 USB4
else
echo "USB4 not connected"
fi
######### USB 5 ############
if [ -e /dev/sde1 ] ; then
echo "USB5 mounted"
pmount -w /dev/sde1 /media/USB5
# sudo e2label /dev/sde1 USB5
# sudo dosfslabel /dev/sde1 USB5
else
echo "USB5 not connected"
fi
######### USB 6 ############
if [ -e /dev/sdf1 ] ; then
echo "USB6 mounted"
pmount -w /dev/sdf1 /media/USB6
# sudo e2label /dev/sdf1 USB6
# sudo dosfslabel /dev/sdf1 USB6
else
echo "USB6 not connected"
fi


echo ""
echo "***** If below is empty, then no drives were mounted. If non-empty, success!"
echo "+++ ls /media/"
ls /media/
echo ""

######### USB 1 ############
if [ -d /media/USB1 ] ; then
echo "+++ ls /media/USB1..."
ls /media/USB1
else
echo "--- USB1 not connected"
fi
######### USB 2 ############
if [ -d /media/USB2 ] ; then
echo "+++ ls /media/USB2..."
ls /media/USB2
else
echo "--- USB2 not connected"
fi
######### USB 3 ############
if [ -d /media/USB3 ] ; then
echo "+++ ls /media/USB3..."
ls /media/USB3
else
echo "--- USB3 not connected"
fi
######### USB 4 ############
if [ -d /media/USB4 ] ; then
echo "+++ ls /media/USB4..."
ls /media/USB4
else
echo "--- USB4 not connected"
fi
######### USB 5 ############
if [ -d /media/USB5 ] ; then
echo "+++ ls /media/USB5..."
ls /media/USB5
else
echo "--- USB5 not connected"
fi
######### USB 6 ############
if [ -d /media/USB6 ] ; then
echo "+++ ls /media/USB6..."
ls /media/USB6
else
echo "--- USB6 not connected"
fi


echo ""
echo "***** Granting xhost privileges..."
xhost +si:localuser:pi
xhost +si:localuser:root


echo ""
echo "***** Possible Errors..."
echo "      Expected errors if not all USB drives are present (not a problem):"  
echo "            --> Error: device /dev/sdb1 is not mounted"
echo "            --> Error: device /dev/sdb1 does not exist"
echo "      Expected errors if not using a USB hub (not a problem):"  
echo "            --> ls: cannot access '/media/USB3': No such file or directory"
echo ""
echo "      Input/output error (IS A PROBLEM)"
echo "            --> This means that your R Pi cannot provide enough power!"
echo "            --> Connect the camera to another power source!"
echo ""
echo "***** Errors Thrown Below..."
echo ""
echo ""
echo "This window will automatically close in 10 seconds..."
sleep 10