import re
import subprocess
from xml.dom.minidom import parse, parseString

class Nentry:
	def __init__(self, name, api, start, machine_time, node_time, stat):
		self.name = name
		self.api = api
		if(start != ""):
			self.start = self.config_time(start)
		else:
			self.start = ""
		if(node_time != ""):
			self.node_time = self.config_time(node_time)
		else:
			self.node_time = ""
		self.machine_time = machine_time
		self.stat = stat
	def get_name(self):
		return self.name
	def get_api(self):
		return self.api
	def get_start(self):
		return self.start
	def get_node_time(self):
		return self.node_time
	def get_machine_time(self):
		return self.machine_time
	def get_stat(self):
		return self.stat
	def config_time(self, time):
		p =subprocess.Popen(["date","+%Y/%m/%d %H:%M:%S","-d", "@"+str(time)], stdout=subprocess.PIPE)
		out, err = p.communicate()
		out = str(out)[2:-3]
		return str(out)

def get_node_info(xml_string, uni_name):
	api = ""
	start = ""
	node_time = ""
	p = subprocess.Popen(["date","+%Y/%m/%d %H:%M:%S"], stdout=subprocess.PIPE)
	machine_time, err = p.communicate()
	if(len(machine_time) == 0):
		machine_time = ""
	else:
		machine_time = str(machine_time)[2:-3]
	#p = subprocess.Popen(["wget","-t 1","-T 5","-q","-O", "-",xml_link], stdout=subprocess.PIPE)
	#exec shell command and puts it to out
	#out, err = p.communicate()
	#if nothing is in out, then return
	
	if(len(xml_string) == 0):
		return Nentry(uni_name, "", "",  machine_time, "", "OFFLINE")
	try:
		xml = parseString(xml_string)
	except Exception as e:
		return Nentry(uni_name, "", "",  machine_time, "", "OFFLINE")
	if(re.search(">[^<]*<", xml.getElementsByTagName("apiversion")[0].toxml()) != None):
		api = re.search(">[^<]*<", xml.getElementsByTagName("apiversion")[0].toxml()).group(0)[1:-1]
	if(re.search(">[^<]*<", xml.getElementsByTagName("starttime")[0].toxml()) != None):
		start = re.search(">[^<]*<", xml.getElementsByTagName("starttime")[0].toxml()).group(0)[1:-1]
	if(re.search(">[^<]*<", xml.getElementsByTagName("now")[0].toxml()) != None):
		node_time = re.search(">[^<]*<", xml.getElementsByTagName("now")[0].toxml()).group(0)[1:-1]
	return Nentry(uni_name, api, start, machine_time, node_time, "ONLINE")
