#!/bin/bash

VERSION=`grep " libndn-cxx " /home/jdd/WU-ARL/ndnstatus/ndn_prefix/versions/${1}  | awk '{print $3}' | cut -d '-' -f 1-3`
#echo "$1 VERSION $VERSION" >> /tmp/version
echo $VERSION
