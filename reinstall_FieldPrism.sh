#!/bin/bash
echo "You are about to delet the old FieldPrism installation. To reinstall, you MUST be plugged into am internet router using an ethernet cable."
echo ""
echo "Type <DELETE> to continue...""
read ANSWER
if [ "$ANSWER" = "DELETE" ]; 
then
	cd /home/pi/
	sudo rm -rf /FieldPrism
	echo "Old installation has been removed"
	git clone https://github.com/Gene-Weaver/FieldPrism.git
	cd /home/pi/FieldPrism/
	git pull --ff-only
	cp git_clone_or_update.sh /home/pi
	echo "FieldPrism is freshly installed and to date!"
fi
echo ""
echo "This window will automatically close in 10 seconds..."
sleep 10