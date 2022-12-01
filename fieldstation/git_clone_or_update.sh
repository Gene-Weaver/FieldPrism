#!/bin/bash
if [ -d "/home/pi/FieldPrism" ] 
then
	echo "FieldPrism main directory /home/pi/FieldPrism exists. Updating FieldPrism, pulling from GitHub Repo..."
	cd /home/pi/FieldPrism/
	git pull --ff-only
	cp /home/pi/FieldPrism/fieldstation/git_clone_or_update.sh /home/pi
	cp /home/pi/FieldPrism/fieldstation/reinstall_FieldPrism.sh /home/pi
	sudo cp /home/pi/FieldPrism/img/FieldPrism_Desktop_Black.jpg /usr/share/rpd-wallpaper
	sudo cp /home/pi/FieldPrism/img/FieldPrism_Desktop_Black_Plain.jpg /usr/share/rpd-wallpaper
	pcmanfm --set-wallpaper="/usr/share/rpd-wallpaper/FieldPrism_Desktop_Black.jpg"
	echo "FieldPrism is up to date!"
else
	echo "FieldPrism main directory /home/pi/FieldPrism does NOT exist. Cloning GitHub Repo..."
	cd /home/pi/
	git clone https://github.com/Gene-Weaver/FieldPrism.git
	cd /home/pi/FieldPrism/
	git pull --ff-only
	cp /home/pi/FieldPrism/fieldstation/git_clone_or_update.sh /home/pi
	cp /home/pi/FieldPrism/fieldstation/reinstall_FieldPrism.sh /home/pi
	sudo cp /home/pi/FieldPrism/img/FieldPrism_Desktop_Black.jpg /usr/share/rpd-wallpaper
	sudo cp /home/pi/FieldPrism/img/FieldPrism_Desktop_Black_Plain.jpg /usr/share/rpd-wallpaper
	pcmanfm --set-wallpaper="/usr/share/rpd-wallpaper/FieldPrism_Desktop_Black.jpg"
	echo "FieldPrism is freshly installed and to date!"
fi
echo ""
echo "This window will automatically close in 60 seconds..."
sleep 60