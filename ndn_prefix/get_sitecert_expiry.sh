#!/bin/bash

EXPIRES=`grep SITE_CERT_EXPIRES /home/jdd/WU-ARL/ndnstatus/ndn_prefix/versions/${1}  | awk '{print $2}' `
echo $EXPIRES
