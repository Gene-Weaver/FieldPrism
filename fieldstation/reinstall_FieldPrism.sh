#!/bin/bash
echo "You are about to delete the old FieldPrism installation." 
echo "To reinstall, you MUST be connected to an internet router using an ethernet cable!"
echo ""
echo "Any local changes that have been made to the /home/pi/FieldPrism. directory will be deleted!"
echo ""
echo "If this fails and causes more problems, re-flash the RPi image to your mSD card."
echo "NOTE:"
echo "     /home/pi/git_clone_or_update.sh"
echo "and"
echo "     /home/pi/reinstall_FieldPrism.sh"
echo "are not removed, so there is a fallback if something goes wrong."
echo ""
echo "Type <DELETE> to continue... (without the < >)"
read ANSWER
if [ "$ANSWER" = "DELETE" ]; 
then
	echo "Deleting /home/pi/FieldPrism"
	cd /home/pi/
	sudo rm -rf /FieldPrism
	echo "Old installation has been removed."
	echo "Cloning GitHub repo..."
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
	echo "FieldPrism is freshly installed and up to date!"
else
	echo "Cancelled. Nothing has been removed or changed."
fi
echo ""
echo "This window will automatically close in 60 seconds..."
sleep 60