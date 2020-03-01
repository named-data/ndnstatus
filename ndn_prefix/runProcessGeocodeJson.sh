#!/bin/bash

#DIR=/home/research/jdd/Library/HTML/Public/ndnstatus/ndn_prefix
DIR=/home/jdd/WU-ARL/ndnstatus/ndn_prefix

cd $DIR
cp -p ../../ndnmap/WebServer/gmap/json/geocode.json .

mv testbedNodes.json testbedNodes.json.PREV
./processGeocodeJson.py geocode.json testbedNodes.json >& processGeocodeJson.log
chmod 644 testbedNodes.json
sudo cp testbedNodes.json /var/www/html/
sudo rm /var/www/html/testbed-nodes.json
sudo ln -s /var/www/html/testbedNodes.json /var/www/html/testbed-nodes.json
