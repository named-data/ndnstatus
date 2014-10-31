import re
import subprocess
import iso8601
from xml.dom.minidom import parse, parseString

class Nentry:
	def __init__(self, name, api, start, machine_time, node_time, stat):
		self.name = name
		self.api = api
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
	def get_api(self):
		return self.api
	def get_start(self):
                #print "get_start() returning self.start: " + self.start
		return self.start
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

def get_node_info(xml_string, uni_name):
        standard_ucla_time=""
        #print "get_node_info() uni_name " + uni_name
	api = ""
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
                #print "get_node_info() marking " + uni_name + " OFFLINE because of empty xml_string"
		return Nentry(uni_name, "", "",  machine_time, "", "OFFLINE")
	try:
		xml = parseString(xml_string)
	except Exception as e:
                #print "get_node_info() marking " + uni_name + " OFFLINE because of exception"
                #print "  xml_string: " + xml_string
		return Nentry(uni_name, "", "",  machine_time, "", "OFFLINE")

        #print "found " + uni_name
        #print "xml_string: " + xml_string
	if(re.search(">[^<]*<", xml.getElementsByTagName("version")[0].toxml()) != None):
	        api = re.search(">[^<]*<", xml.getElementsByTagName("version")[0].toxml()).group(0)[1:-1]
                #print  uni_name + " api: " + api
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

	return Nentry(uni_name, api, start, machine_time, node_time, "ONLINE")
