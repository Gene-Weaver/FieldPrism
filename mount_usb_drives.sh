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
echo "***** Clear Mounting Points..."
rm -rfv /media/*
echo ""
echo "***** Verify Cleared Mounting Points..."
ls -l /media/
echo ""
echo "***** Mounting USB Drives..."
pmount /dev/sda1 USB1
pmount /dev/sdb1 USB2
echo ""
echo "***** If below is empty, then no drives were mounted. If non-empty, success."
ls /media/
ls /media/USB1
ls /media/USB1
chown -R pi /media/USB1
chown -R pi /media/USB2
echo ""
echo "***** Finished"  
echo ""
