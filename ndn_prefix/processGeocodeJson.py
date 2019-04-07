#!/usr/bin/env python
import json
import os
import sys
import subprocess

def process():

  devnull = open (os.devnull, 'w')

  # Check that we can ping the WU node. If we can't do that, we can't do anything.
  exit_code = subprocess.call(["/usr/bin/ndnping", "-c", "3", "/ndn/edu/wustl"],stdout=devnull, stdin=None, stderr=devnull)
  if exit_code != 0:
    # Can't reach WU, exit
    print "ndnping of /ndn/edu/wustl failed. If we can't reach WU then we don't want to change anything. exiting... "
    return

  jdata = open(sys.argv[1])
  jdataout = open(sys.argv[2],'w')
  
  data = json.load(jdata)

  
  #print "shortname", " - ", "site http", " - ", "ndn-up"
  #print data["UA"]["shortname"], " - ", data["UA"]["site"], " - ", data["UA"]["ndn-up"]

  for k,v in data.items():
    # Test for ndn up with ndnping
    #print k
    if v["https"] == "https://0.0.0.0:443/" :
      #print "skipping"
      continue
    exit_code = subprocess.call(["/usr/bin/ndnping", "-i", "500", "-c", "3", v["prefix"]],stdout=devnull, stdin=None, stderr=devnull)
    if exit_code == 0:
      #print "exit_code == 0 set ndn-up True"
      v["ndn-up"] = True
    else:
      v["ndn-up"] = False
      #print "exit_code != 0 set ndn-up False"
    # test for ws-tls update using curl
    # curl --connect-timeout 2 https://wundngw.arl.wustl.edu:443/ws
    exit_code = subprocess.call(["/usr/bin/curl", "--connect-timeout", "2", v["https"]+"/ws"],stdout=devnull, stdin=None, stderr=devnull)
    if exit_code == 0:
      #print "exit_code == 0 set ws-tls True"
      v["ws-tls"] = True
    else:
      v["ws-tls"] = False
      #print "exit_code != 0 set ws-tls False"
    #print "prefix: ", v["prefix"]
    #print "https: ", v["https"]
    #print k , v
    #print node["shortname"], " - ", node["site"], " - ", node["ndn-up"]
  
  jdata.close()
  #with open("jsondump.json", "w") as outfile:
  #  json.dump(data,outfile,indent=2)
  json.dump(data,jdataout,indent=2)


if __name__ == '__main__':
  process()
