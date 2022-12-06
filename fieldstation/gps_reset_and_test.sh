# GPS
ls /dev/ttyUSB*
sudo lsusb
sudo systemctl stop gpsd.socket
sudo systemctl disable gpsd.socket
sudo killall gpsd
sudo gpsd /dev/ttyUSB0 -F /var/run/gpsd.sock
echo "Close this terminal window when done..."
cgps -s