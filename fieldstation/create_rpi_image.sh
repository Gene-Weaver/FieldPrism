#!/bin/sh

# Prompt the user for the directory
echo "Enter the directory for the USB drive (e.g. /media/USB1):"
read USB_DIR

# Prompt the user for the image name
echo "Enter the name for the image (e.g. FieldPrism-A_v-1-0.img):"
read IMAGE_NAME

# Prompt the user for the size
echo "Enter the size of the image in MB (e.g. 17000):"
read SIZE

# Run the dd command with the user-specified values
sudo dd if=/dev/mmcblk0 of="$USB_DIR/$IMAGE_NAME" bs=1M count="$SIZE"

# Change to the USB drive directory
cd "$USB_DIR"

# Run the pishrink.sh script with the user-specified image name
sudo pishrink.sh -z "$IMAGE_NAME"