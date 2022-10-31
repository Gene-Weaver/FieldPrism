#!/bin/bash
if [ -d "/home/pi/FieldPrism" ] 
then
	echo "FieldPrism main directory /home/pi/FieldPrism exists. Updating FieldPrism, pulling from GitHub Repo..."
	cd /home/pi/FieldPrism/
	git pull
	echo "FieldPrism is up to date!"
else
	echo "FieldPrism main directory /home/pi/FieldPrism does NOT exist. Cloning GitHub Repo..."
	cd /home/pi/
	git clone https://github.com/Gene-Weaver/FieldPrism.git
	cd /home/pi/FieldPrism/
	git pull
	echo "FieldPrism is freshly installed and to date!"
fi
echo ""
echo "This window will automatically close in 10 seconds..."
sleep 10