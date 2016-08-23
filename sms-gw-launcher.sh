#!/bin/bash

# sms-gw-launcher.sh izsauc sms-gw.py, kas nodarbojas ar SMS saņemšanu un sūtīšanu.
# 
# sms-gw-watchdog.sh tiek izsaukts no cron. 
# Tas pārbauda, vai fails "/dev/shm/sms-gw-ping.log" ir pietiekami svaigs. 
# Ja nav, tad nokillo sms-gw.py procesu. 
# sms-gw-launcher.sh to palaidīs no jauna.


while [ 1 -eq 1 ]; do
  echo "---------------------"
  echo "sms-gw.py starting.."
  date

  cd /home/x-f/sw/sms-gw/ && /usr/bin/python ./sms-gw.py
  # ./reset-modem.sh
  
  sleep 30
done
