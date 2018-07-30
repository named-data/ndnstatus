import re
import subprocess
import iso8601
from xml.dom.minidom import parse, parseString

class Nentry:
	def __init__(self, name, nfd_version, nlsr_version, ndn_cxx_version, chronosync_version, tls_expiry, os_version,start, machine_time, node_time, nlsr_start_time, nlsr_current_time, utc_current_nlsr_time, utc_nlsr_start_time, stat):
		self.name = name
		self.nfd_version = nfd_version
		self.nlsr_version = nlsr_version
		self.nlsr_start_time = nlsr_start_time
		self.nlsr_current_time = nlsr_current_time
		self.ndn_cxx_version = ndn_cxx_version
		self.chronosync_version = chronosync_version
		self.tls_expiry = tls_expiry
		self.utc_nlsr_start_time = utc_nlsr_start_time
		self.utc_current_nlsr_time = utc_current_nlsr_time
		self.os_version = os_version
		if(start != ""):
                        #print "self.config_time(start):" + start
			self.start = self.config_time(start)
                        #print "self.start: " + self.start
		else:
			self.start = ""
		if(node_time != ""):
                        #print "self.config_time(node_time):" + node_time
			self.node_time = self.config_time(node_time)
                        #print "self.node_time: " + self.node_time
		else:
			self.node_time = ""
		self.machine_time = machine_time
		self.stat = stat
	def get_name(self):
		return self.name
	def get_nfd_version(self):
		return self.nfd_version
	def get_nlsr_version(self):
		return self.nlsr_version
	def get_nlsr_version(self):
		return self.nlsr_version
	def get_ndn_cxx_version(self):
		return self.ndn_cxx_version
	def get_chronosync_version(self):
		return self.chronosync_version
	def get_tls_expiry(self):
		return self.tls_expiry
	def get_os_version(self):
		return self.os_version
	def get_start(self):
                #print "get_start() returning self.start: " + self.start
		return self.start
	def get_nlsr_start_time(self):
		return self.nlsr_start_time
	def get_nlsr_current_time(self):
		return self.nlsr_current_time
	def get_utc_current_nlsr_time(self):
		return self.utc_current_nlsr_time
	def get_utc_nlsr_start_time(self):
		return self.utc_nlsr_start_time
	def get_node_time(self):
		return self.node_time
	def get_machine_time(self):
		return self.machine_time
	def get_stat(self):
		return self.stat
	def config_time(self, time):
                ##print "time: " + time
		#p =subprocess.Popen(["date","+%Y/%m/%d %H:%M:%S","-d", "@"+str(time)], stdout=subprocess.PIPE)
		#out, err = p.communicate()
                ##print "out: " + out
		##out = str(out)[2:-3]
                x=iso8601.parse_date(time)
                out=x.strftime('%Y/%m/%d %H:%M:%S') 
		#return str(out)
                #print "config_time returning out = " + out
                return(out)

def get_node_info(xml_string, uni_name, versions_filename):
        standard_ucla_time=""
        #print "get_node_info() uni_name " + uni_name
        print "get_node_info() uni_name " + uni_name + " versions_filename " + versions_filename
	nlsr_version = ""
	ndn_cxx_version = ""
	chronosync_version = ""
	tls_expiry = ""
	os_version = "" 
	nfd_version = ""
	start = ""
	node_time = ""
	p = subprocess.Popen(["date","-u", "+%Y/%m/%d %H:%M:%S"], stdout=subprocess.PIPE)
	machine_time, err = p.communicate()
	if(len(machine_time) == 0):
		machine_time = ""
	#else:
	#	machine_time = str(machine_time)[2:-3]
	#p = subprocess.Popen(["wget","-t 1","-T 5","-q","-O", "-",xml_link], stdout=subprocess.PIPE)
	#exec shell command and puts it to out
	#out, err = p.communicate()
	#if nothing is in out, then return
	
	if(len(xml_string) == 0):
                print "get_node_info() marking " + uni_name + " OFFLINE because of empty xml_string"
		return Nentry(uni_name, "", "", "", "", "", "", "",  machine_time, "", "", "", "", "", "OFFLINE")
	try:
		xml = parseString(xml_string)
	except Exception as e:
                print "get_node_info() marking " + uni_name + " OFFLINE because of exception"
                print "  xml_string: " + xml_string
		return Nentry(uni_name, "", "", "", "", "", "", "",  machine_time, "", "", "","", "",  "OFFLINE")

        #print "found " + uni_name
        #print "xml_string: " + xml_string
	if(re.search(">[^<]*<", xml.getElementsByTagName("version")[0].toxml()) != None):
	        nfd_version = re.search(">[^<]*<", xml.getElementsByTagName("version")[0].toxml()).group(0)[1:-1]
                #print  uni_name + " nfd_version: " + nfd_version
	#return Nentry(uni_name, "", "",  machine_time, "", "OFFLINE")
	if(re.search(">[^<]*<", xml.getElementsByTagName("startTime")[0].toxml()) != None):
		start = re.search(">[^<]*<", xml.getElementsByTagName("startTime")[0].toxml()).group(0)[1:-1]
                #print "start: " + start
	if(re.search(">[^<]*<", xml.getElementsByTagName("currentTime")[0].toxml()) != None):
		node_time = re.search(">[^<]*<", xml.getElementsByTagName("currentTime")[0].toxml()).group(0)[1:-1]
                #print "node_time: " + node_time
                if uni_name == "UCLA":
                     standard_ucla_time = node_time
                     #print "found UCLA setting standard_ucla_time: " + standard_ucla_time
                #print "get_node_time(): " + self.get_node_time()

	p = subprocess.Popen(["/home/jdd/WU-ARL/ndnstatus/ndn_prefix/get_tls_expiry.sh",uni_name], stdout=subprocess.PIPE)
	tls_expiry,err = p.communicate()
	p = subprocess.Popen(["/home/jdd/WU-ARL/ndnstatus/ndn_prefix/get_libchronosync.sh",uni_name], stdout=subprocess.PIPE)
	chronosync_version,err = p.communicate()
	p = subprocess.Popen(["/home/jdd/WU-ARL/ndnstatus/ndn_prefix/get_nlsr.sh",uni_name], stdout=subprocess.PIPE)
	nlsr_version,err = p.communicate()
	p = subprocess.Popen(["/home/jdd/WU-ARL/ndnstatus/ndn_prefix/get_nlsr_start_time.sh",uni_name], stdout=subprocess.PIPE)
	nlsr_start_time,err = p.communicate()
	p = subprocess.Popen(["/home/jdd/WU-ARL/ndnstatus/ndn_prefix/get_nlsr_current_time.sh",uni_name], stdout=subprocess.PIPE)
	nlsr_current_time,err = p.communicate()
	p = subprocess.Popen(["/home/jdd/WU-ARL/ndnstatus/ndn_prefix/get_utc_current_nlsr_time.sh",uni_name], stdout=subprocess.PIPE)
	utc_current_nlsr_time,err = p.communicate()
	p = subprocess.Popen(["/home/jdd/WU-ARL/ndnstatus/ndn_prefix/get_utc_nlsr_start_time.sh",uni_name], stdout=subprocess.PIPE)
	utc_nlsr_start_time,err = p.communicate()

	p = subprocess.Popen(["/home/jdd/WU-ARL/ndnstatus/ndn_prefix/get_ndn-cxx.sh",uni_name], stdout=subprocess.PIPE)
	ndn_cxx_version,err = p.communicate()
	p = subprocess.Popen(["/home/jdd/WU-ARL/ndnstatus/ndn_prefix/get_os.sh",uni_name], stdout=subprocess.PIPE)
	os_version,err = p.communicate()
        #print uni_name + " chronosync_version " + chronosync_version
	return Nentry(uni_name, nfd_version, nlsr_version, ndn_cxx_version, chronosync_version, tls_expiry, os_version, start, machine_time, node_time, nlsr_start_time, nlsr_current_time, utc_current_nlsr_time, utc_nlsr_start_time, "ONLINE")
