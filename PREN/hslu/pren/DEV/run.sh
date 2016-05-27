#!/bin/bash

cd /home/pi/Desktop/_PROD/Latest/
export PYTHONPATH="$PYTHONPATH:/home/pi/Desktop/_PROD/:/usr/local/lib/python2.7/dist-packages/:/usr/local/lib/python2.7/site-packages/"
ls /dev/tty*
echo "Enter Freedomboard Port (only last digit)"
read port
echo "Enable X11? (Y/n)"
read xVision

if [ "$xVision" == "Y" ] 
then

	python hslu/pren/control/Main.py -b -fp='/dev/ttyACM'$port -wp=0 -d -x -pi

else

	if [ -z "$xVision" ] 
	then

		python hslu/pren/control/Main.py -b -fp='/dev/ttyACM'$port -wp=0 -d -x -pi
	
	else

		python hslu/pren/control/Main.py -b -fp='/dev/ttyACM'$port -wp=0 -d -pi

	fi
fi