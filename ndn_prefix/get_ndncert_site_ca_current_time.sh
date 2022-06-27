#!/bin/bash

TIME=`grep "Current Time" /home/jdd/WU-ARL/ndnstatus/ndn_prefix/versions/${1}  | awk '{print $3}' `
#echo "$1 TIME $TIME" >> /tmp/version
echo $TIME
