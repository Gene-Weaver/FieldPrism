#!/bin/bash
echo "You are about to delete the old FieldPrism installation." 
echo "To reinstall, you MUST be connected to an internet router using an ethernet cable."
echo ""
echo "Type <DELETE> to continue...""
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
	cp git_clone_or_update.sh /home/pi
	cp reinstall_FieldPrism.sh /home/pi
	echo "FieldPrism is freshly installed and up to date!"
else
	echo "Cancelled. Nothing has been removed or changed."
fi
echo ""
echo "This window will automatically close in 10 seconds..."
sleep 10