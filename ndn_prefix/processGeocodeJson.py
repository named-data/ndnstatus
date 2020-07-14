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
    #exit_code = subprocess.call(["/usr/bin/ndnping", "-i", "500", "-c", "3", v["prefix"]],stdout=devnull, stdin=None, stderr=devnull)
    #exit_code = subprocess.call(["/usr/bin/ndnping", "-c", "1", v["prefix"]],stdout=devnull, stdin=None, stderr=devnull)
    exit_code = subprocess.call(["/usr/bin/ndnping", "-c", "1", v["prefix"]],stdin=None)
    if exit_code == 0:
      #print "exit_code == 0 set ndn-up True"
      v["ndn-up"] = True
    else:
      # try again
      exit_code = subprocess.call(["/usr/bin/ndnping", "-c", "1", v["prefix"]],stdin=None)
      if exit_code == 0:
        v["ndn-up"] = True
      else:
        exit_code = subprocess.call(["/usr/bin/ndnping", "-c", "1", v["prefix"]],stdin=None)
        if exit_code == 0:
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
    neighborFilename = "/home/jdd/WU-ARL/ndnstatus/ndn_prefix/NDN_Ansible/roles/node_link_db_gen/files/json_files/"  + k +"_links.json"
    ndata = open(neighborFilename)
    neighbordata = json.load(ndata)
    for kk,vv in neighbordata.items():
      #v["neighbors"] = vv["neighborlist"]
      print v["neighbors"] 
      #print vv["neighborlist"]
      print str(vv)
      #v["neighbors"] = str(vv)
      v["neighbors"] = eval(json.dumps(vv))
      print v["neighbors"] 
    ndata.close()
    #print neighborFilename
  
  jdata.close()
  #with open("jsondump.json", "w") as outfile:
  #  json.dump(data,outfile,indent=2)
  json.dump(data,jdataout,indent=2)


if __name__ == '__main__':
  process()
