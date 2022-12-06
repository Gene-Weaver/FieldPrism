# GPS
ls /dev/ttyUSB*
sudo lsusb
sudo systemctl stop gpsd.socket
sudo systemctl disable gpsd.socket
sudo killall gpsd
sudo gpsd /dev/ttyUSB0 -F /var/run/gpsd.sock
echo "Raw GPS data is about to stream"
echo "Ctrl + C to end the stream"
sleep 5
sudo cat /dev/ttyUSB0