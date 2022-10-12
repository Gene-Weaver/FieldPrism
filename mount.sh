#!/bin/bash 
echo "fieldprism" | sudo udisksctl mount -b /dev/sda1;
if [ $? -eq 0 ]; then
    echo -e '[ ok ] Usb key mounted'
else
    echo -e '[warn] The USB key is not mounted'
fi
echo "fieldprism" | sudo udisksctl mount -b /dev/sdb1;
if [ $? -eq 0 ]; then
    echo -e '[ ok ] Usb key mounted'
else
    echo -e '[warn] The USB key is not mounted'
fi