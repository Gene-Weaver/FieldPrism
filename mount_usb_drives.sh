#!/bin/bash 
echo "***** Trying to Mount USB Drives..."  
echo "***** View USB Devices..."  
echo "***** If USB storage is not in list below, then the USB drive is likely formatted incorrectly." 
lsusb 
echo "***** View Mounting Points..."
ls /media/
echo "***** Clear Mounting Points..."
rm -rfv /media/*
echo "***** Verify Cleared Mounting Points..."
ls -l /media/
echo "***** Mounting USB Drives..."
pmount /dev/sda1 USB1
pmount /dev/sdb1 USB2
echo "***** If below is empty, then no drives were mounted. If non-empty, success."
ls /media/
ls /media/USB1
ls /media/USB1
echo "***** Finished"  
