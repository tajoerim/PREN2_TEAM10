#!/bin/bash

cd /home/pi/Desktop/_PROD/Latest/
export PYTHONPATH="$PYTHONPATH:/home/pi/Desktop/_PROD/:/usr/local/lib/python2.7/dist-packages/:/usr/local/lib/python2.7/site-packages/"
ls /dev/tty*
echo "Enter Freedomboard Port (only last digit)"
read port

python hslu/pren/control/Main.py -b -fp='/dev/ttyACM'$port -wp=0 -d -x -pi