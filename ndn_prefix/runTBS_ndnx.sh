#!/bin/bash

#DIR=/home/research/jdd/Library/HTML/Public/ndnstatus/ndn_prefix
DIR=/home/jdd/WU-ARL/ndnstatus/ndn_prefix

cd $DIR
mv tbs_ndnx.out tbs_ndnx.out.PREV
python tbs_ndnx.py >& tbs_ndnx.out

sudo cp tbs_ndnx.html /var/www/html/ndn.html
# Reproduce the topology image:
#cp -p ../../ndnmap/WebServer/gmap/json/*.json .
./NDN_nx.py
# run the one that uses real coordinates
./NDN_nx_coord.py
sudo cp topology.png /var/www/html/
sudo cp topology2.png /var/www/html/
sudo mkdir -p /var/www/html/json
sudo cp ../../ndnmap/WebServer/gmap/json/*.json /var/www/html/json


#./processGeocodeJson.py geocode.json testbedNodes.json >& processGeocodeJson.log
#chmod 644 testbedNodes.json
#sudo cp testbedNodes.json /var/www/html/
