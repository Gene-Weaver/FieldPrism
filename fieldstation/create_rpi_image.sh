#!/bin/sh

# Prompt the user for the directory
echo "To clone the OS, remove all USB storage devices. Select a USB drive that has more capacity than the micro SD card that is currently running the R Pi."
echo "If the R Pi has a 32GB micro SD, then use a 64GB USB drive."
echo "Reformat the USB drive using NTFS (if on Windows) or ext4 (if on Linux)."
echo "Attach the fresh USB drive to the R Pi. Make sure its the only attached storage device."
echo "Run the command to mount USB Drives, like normal."
echo "Take note of the Drive's location. Normally it's '/media/USB1'"
echo "Now you can begin the cloning process."
echo " "
echo "Enter the directory for the USB drive (e.g. /media/USB1):"
read USB_DIR

# Prompt the user for the image name
echo "Enter the name for the image (e.g. FieldStation-Clone.img):"
read IMAGE_NAME

# Prompt the user for the size
echo "To clone the OS, we need to tell the script how large the OS is. We will over estimate:"
echo "    - If your micro SD card is 16GB, then set the following to 17000"
echo "    - If your micro SD card is 32GB, then set the following to 33000"
echo "    - If your micro SD card is 64GB, then set the following to 64000"
echo "The following process will take a long time (~1 hour) to complete and the terminal will not show progress."
echo "Open the USB Drive in the file manager to track the progress."
echo "The new .img file should begin to grow in size (FieldStation-Clone.img)"
echo " "
echo "Enter the size of the image in MB (e.g. 17000):"
read SIZE

# Run the dd command with the user-specified values
sudo dd if=/dev/mmcblk0 of="$USB_DIR/$IMAGE_NAME" bs=1M count="$SIZE"

# Change to the USB drive directory
cd "$USB_DIR"

# Run the pishrink.sh script with the user-specified image name
sudo pishrink.sh -z "$IMAGE_NAME"