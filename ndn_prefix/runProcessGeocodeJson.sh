#!/bin/bash

#DIR=/home/research/jdd/Library/HTML/Public/ndnstatus/ndn_prefix
DIR=/home/jdd/WU-ARL/ndnstatus/ndn_prefix

cd $DIR
#cp -p ../../ndnmap/WebServer/gmap/json/geocode.json .
#cp -p ../../ndnmap/WebServer/gmap/json/links.json .

mv testbedNodes.json testbedNodes.json.PREV
mv processGeocodeJson.log  processGeocodeJson.log.PREV
./processGeocodeJson.py geocode.json testbedNodes.json >& processGeocodeJson.log
chmod 644 testbedNodes.json
if [ -s testbedNodes.json ]
then
  sudo cp testbedNodes.json /var/www/html/
  sudo cp links.json /var/www/html/
  sudo rm /var/www/html/testbed-nodes.json
  sudo ln -s /var/www/html/testbedNodes.json /var/www/html/testbed-nodes.json
fi

