#!/bin/bash

VERSION=`grep "^Description" versions/${1} | awk '{print $2 " " $3}'`
#echo "$1 VERSION $VERSION" >> /tmp/version
echo $VERSION
