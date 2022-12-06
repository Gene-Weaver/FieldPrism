#!/bin/bash
if [ -d "/home/pi/FieldPrism" ] 
then
	echo "FieldPrism main directory /home/pi/FieldPrism exists. Updating FieldPrism, pulling from GitHub Repo..."
	cd /home/pi/FieldPrism/
	git pull --ff-only
	# Copy update and reinstall files out of the FP dir
	cp /home/pi/FieldPrism/fieldstation/git_clone_or_update.sh /home/pi
	cp /home/pi/FieldPrism/fieldstation/reinstall_FieldPrism.sh /home/pi
	# Copy wallpapers 
	sudo cp /home/pi/FieldPrism/img/FieldPrism_Desktop_Black.jpg /usr/share/rpd-wallpaper
	sudo cp /home/pi/FieldPrism/img/FieldPrism_Desktop_Black_Plain.jpg /usr/share/rpd-wallpaper
	# Copy desktop apps
	sudo cp /home/pi/FieldPrism/fieldstation/desktop_app/* /home/pi/.local/share/applications
	pcmanfm --set-wallpaper="/usr/share/rpd-wallpaper/FieldPrism_Desktop_Black.jpg"
	# GPS
	ls /dev/ttyUSB*
	sudo lsusb
	sudo systemctl stop gpsd.socket
	sudo systemctl disable gpsd.socket
	sudo killall gpsd
	sudo gpsd /dev/ttyUSB0 -F /var/run/gpsd.sock
	sudo lsusb
	sudo systemctl stop gpsd.socket
	sudo systemctl disable gpsd.socket
	echo "FieldPrism is up to date!"
else
	echo "FieldPrism main directory /home/pi/FieldPrism does NOT exist. Cloning GitHub Repo..."
	cd /home/pi/
	git clone https://github.com/Gene-Weaver/FieldPrism.git
	cd /home/pi/FieldPrism/
	git pull --ff-only
	# Copy update and reinstall files out of the FP dir
	cp /home/pi/FieldPrism/fieldstation/git_clone_or_update.sh /home/pi
	cp /home/pi/FieldPrism/fieldstation/reinstall_FieldPrism.sh /home/pi
	# Copy wallpapers 
	sudo cp /home/pi/FieldPrism/img/FieldPrism_Desktop_Black.jpg /usr/share/rpd-wallpaper
	sudo cp /home/pi/FieldPrism/img/FieldPrism_Desktop_Black_Plain.jpg /usr/share/rpd-wallpaper
	# Copy desktop apps
	sudo cp /home/pi/FieldPrism/fieldstation/desktop_app/* /home/pi/.local/share/applications
	pcmanfm --set-wallpaper="/usr/share/rpd-wallpaper/FieldPrism_Desktop_Black.jpg"
	# GPS
	ls /dev/ttyUSB*
	sudo lsusb
	sudo systemctl stop gpsd.socket
	sudo systemctl disable gpsd.socket
	sudo killall gpsd
	sudo gpsd /dev/ttyUSB0 -F /var/run/gpsd.sock
	sudo lsusb
	sudo systemctl stop gpsd.socket
	sudo systemctl disable gpsd.socket
	echo "FieldPrism is freshly installed and to date!"
fi
echo ""
echo "This window will automatically close in 60 seconds..."
sleep 60