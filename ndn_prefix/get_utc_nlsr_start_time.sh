#!/bin/bash

TIME=`grep "UTC0_NLSR_START_TIME" /home/jdd/WU-ARL/ndnstatus/ndn_prefix/versions/${1}  | cut -d ' ' -f2-`
#echo "$1 TIME $TIME" >> /tmp/version
echo $TIME
