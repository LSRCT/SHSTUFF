#!/bin/sh
#echo "started" >> /etc/openhab2/testfile.txt
python3 /etc/openhab2/thermoBlue.py $1 >> /etc/openhab2/testfile.txt
#echo "finished" >> /etc/openhab2/testfile.txt
