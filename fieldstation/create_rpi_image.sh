echo "Type target USB device name. This will be in /media/..."
echo "eg."
echo "     USB1"
read USB
echo ""
echo "Type R Pi image file name"
echo "eg."
echo "     FieldPrism-A_v-1-0"
read FILENAME
echo ""
echo "Type the max size of the image. Default image = 17000"
echo "eg."
echo "     FieldPrism-A_v-1-0"
read SIZE
$dir_target = "/media/"
$dir_target += "${USB}"
$dir_target += "/"
$dir_target += "${FILENAME}"
$dir_target += ".img"
echo "dir_target = "
echo "$dir_target"
sudo dd if=/dev/mmcblk0 of="${dir_target}" bs=1M count="${SIZE}"

cd /media/"${USB}"

sudo pishrink.sh -z ${FILENAME}.img