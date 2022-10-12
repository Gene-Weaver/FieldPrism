#!/bin/bash 
echo "Trying to Mount USB Drives..."  
echo "     View USB Devices..."  
lsusb
echo "     If USB storage is not in above list, then the USB drive is likely formatted incorrectly." 
echo "     Mounting USB Drives..."
pmount /dev/sda1 pi
pmount /dev/sdb1 pi
echo "     If below is empty, then no drives were mounted. If non-empty, success."
ls /media/pi/
echo "Finished"  
