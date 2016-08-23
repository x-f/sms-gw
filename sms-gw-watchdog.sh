#!/bin/bash

file="/dev/shm/sms-gw-ping.log"

current=`date +%s`
last_modified=`stat -c "%Y" $file`

# ja fails vecāks par 1 minūti..
if [ $(($current-$last_modified)) -gt 60 ]; then 
  echo "$file file too old, killing sms-gw.py..";
  kill $(ps aux | grep [s]ms-gw.py | awk '{print $2}')
  
  echo "done"
fi
