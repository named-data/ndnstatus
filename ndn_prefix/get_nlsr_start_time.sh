#!/bin/bash

TIME=`grep "NLSR_START_TIME_s" /home/jdd/WU-ARL/ndnstatus/ndn_prefix/versions/${1}  | awk '{print $2}' `
#echo "$1 TIME $TIME" >> /tmp/version
echo $TIME
