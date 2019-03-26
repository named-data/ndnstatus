#!/bin/bash

EXPIRES=`grep TLS_CERT_Expires /home/jdd/WU-ARL/ndnstatus/ndn_prefix/versions/${1}  | awk '{print $2}' `
echo $EXPIRES
