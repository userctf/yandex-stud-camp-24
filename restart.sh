#!/bin/sh

sudo killall python &&
sudo killall node &&


sudo python /home/pi/work/python_src/xr_startmain.py &

sudo node /home/pi/work/XiaoRGeekBle/code/XiaoRGeek/main.js &
exit 0
