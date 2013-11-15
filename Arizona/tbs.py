import re
import math
import config
import subprocess
import time
from ns import *
from dls import *
from wp import *
from fentry import Fentry
from xml.dom.minidom import parse, parseString
from datetime import datetime

#list of ccndstatus pages' xml. After a webpage's xml
#is retrieved, it will be placed here so there will
#no need to retrieve xml multiple times from the same
#website.
#xml_list = []

#This function is used to read from configuration file
#it will populate the lists in config.py. These lists
#will be used later in the program.
#PARAMETERS:
#	filename: configuration file's file name, e.g. config_file.txt
#RETURN: NONE
def setup(filename):
	config_file = open(filename, 'r')
	node_list = []
	link_list = []
	#read in and save everything from config file
	for line in config_file:
		line_len = len(line)
		#nothing on this line, go to the next line
		if(line_len <= 0):
			continue
		#for adding new nodes in the topology. format: n(xml_link, domain, name abbr)
		#e.g. n(http://hobo.cs.arizona.edu:9695/?f=xml, arizona.edu, UA)
		#note some domains are not actual domains, since many nodes have the
		#same domains. For example, SPP* nodes are all washu.edu, but in the config file
		#fake domains are inserted for the purpose of sorting and having unqiue identifiers.
		if(line[0] == "n"):
			#split elements separated by a comma + space after removing .( and )\n
			node_tuple = line[2:-2].split(", ")
			#place the elements in a tuple and insert into (local) node_list
			node_list.append((node_tuple[0], node_tuple[1], node_tuple[2]))
		#for adding new planned topology links. 
		#format: l(node1 name, node1 ip, node2 name, node2 ip)
		#e.g. l(UA, 10.0.1.29:9695, UCSD, 10.0.1.30:9695) represent
		#UA (10.0.1.29:9695) ------------ (10.0.1.30:9695) UCSD
		#Thus UA will forward to 10.0.1.30:9695 to get to UCSD
		#node names are equivalent of name abbr in node_list/n(...)'s
		elif(line[0] == "l"):
			link_tuple = line[2:-2].split(", ")
			#format: (ip used by node1 to forward to node 2, node1, node2)
			#consult testbed topology image for more details
			link_list.append((link_tuple[3], link_tuple[0], link_tuple[2]))
			#format: (dictionary[node1>>node2] = ip used by node1 to forward to node 2)
			#consult testbed topology image for more details
			config.valid_link[link_tuple[0]+">>"+link_tuple[2]] = link_tuple[3]
			#format = dic[ip] = node
			#ip is an ip used by a member of the topology to forward to node
			config.ip_for_node[link_tuple[3]] = link_tuple[2]
			#ip used by node2 to forward to node 1
			link_list.append((link_tuple[1], link_tuple[2], link_tuple[0]))
			#from node2 to forward to node1, this up is used
			config.valid_link[link_tuple[2]+">>"+link_tuple[0]] = link_tuple[1]
			config.ip_for_node[link_tuple[1]] = link_tuple[0]
		#new prefix...
		#since ccnx allows pretty much anything, there isn't a sure fire way
		#filter the wanted prefixes. Currently, the program has a general filter,
		#but if it blocks some useful prefixes, use this to explicitly add it.
		elif(line[0] == "p"):
			name_tuple = line[2:-2].split(", ")
			#p(ccnx:/ndn/prefix)
			#config.names.append((name_tuple[0], "ccnx:/"+name_tuple[0][10:]))

			#each node can advertise 2 kinds of prefixes, ccnx:/ndn/prefix, or ccnx:/prefix
			#key is ccnx:/ndn/prefix, value is ccnx:/prefix
			#this is a list of prefixes that should always be present in the table for
			#debugging purposes
			config.names[name_tuple[0]] = "ccnx:/"+name_tuple[0][10:]
			config.valid_prefix[name_tuple[0]] = get_domain(name_tuple[0])
			
		#invalid prefix, must be exact match
		elif(line[0] == "i"):
			invalid_p = line[2:-2]
			config.invalid_prefix.append(invalid_p)
	config_file.close()
	#sort the nodes of topology by domain
	node_list.sort(key = lambda tup: tup[1])
	#find the sorted index of each node in the list of links
	for element in link_list:
		src_index, dest_index = -1, -1
		for i in range(0, len(node_list)):
			#if name abbr of node matches node1 name,
			#then the index of the tuple containing
			#the name abbr will be node1's index. This
			#is used to directly access the nodes in
			#node_list through link_list/llist
			if(node_list[i][2] == element[1]):
				src_index = i
			#if name abbr == node2 name, then i
			#is node2's index 
			if(node_list[i][2] == element[2]):
				dest_index = i
		if(src_index != -1 and dest_index != -1):
			#save to config.py
			config.llist.append((element[0],element[1],element[2],src_index,dest_index))
		else:
			#!!!need a better way to alert for errors since this script is most likely not run by a human 
			print("error detected in setup, link:", element, "src:", src_index, "dest:", dest_index)
	for node in node_list:
		#save to config.py
		config.node_url.append(node)
	#0 everything in adjacency matrix and matrix that reflects current links
	for i in range(0, len(node_list)):
		new_row_planned = []
		new_row_current = []
		for j in range(0, len(node_list)):
			new_row_planned.append(0)
			new_row_current.append(0)
		config.planned_links.append(new_row_planned)
		config.current_links.append(new_row_current)
	#init adj matrix of topology
	for i in config.llist:
		config.planned_links[i[3]][i[4]] = 1

#This function checks if a prefix is valid, ie not anything internal
#or unneed etc. This may need more/different checks when more prefixes
#are registered.
#PARAMETERS:
#	prefix: any ccnx URI, e.g. ccnx:/ndn/arizona.edu
#RETURN: 
#	True: if the function considers prefix to be testbed valid
#	False: if the function considers prefix to be invalid
def is_testbed_prefix(prefix):
	#if in list of invalid prefixes, return false.
	#may change to hash table later.
	if(prefix in config.invalid_prefix):
		return False
	#more special cases, added before the invalid list is implemented
	if(re.search("(ccnx:/trace)|(ping)|(C1\.M\.K)|(parc\.com/host/ccngw)|(metwi)|(uiuc\.edu/test)|(apps/..*)", prefix) != None):
		return False
	#more special cases (at least 1 char following the /)
	if(re.search("(sppatla1/..*)|(spphous1/..*)|(sppkans1/..*)|(sppsalt1/..*)|(sppwash1/..*)", prefix) != None):
		return False
	#ucla special cases
	if(re.search("(ccnx:/ndn/ucla.edu/%C1\.S\.*)", prefix) != None):
		return False
	if(re.search("(\.edu)|(\.org)|(\.com)|(\.cn)|(\.uk)", prefix) != None):
		config.valid_prefix[prefix] = get_domain(prefix)
		return True
	if(re.search("(sppatla1)|(spphous1)|(sppkans1)|(sppsalt1)|(sppwash1)", prefix) != None):
		config.valid_prefix[prefix] = get_domain(prefix)
		return True
	return False 
#get domain name from prefix
#args: prefix (any prefix)
#returns: "" if cannot find proper domain, "ucla/metwi" for REMAP, domain of prefix, eg "website.com" for "ccnx:/ndn/website.com"
def get_domain(prefix):
	#special cases for prefixes that share the same domain
	#give them unique fake domains
	if(re.search("ccnx:/ndn/sppatla1", prefix) != None):
		return "wustl.edu/sppatla1"
	if(re.search("ccnx:/ndn/spphous1", prefix) != None):
		return "wustl.edu/spphous1"
	if(re.search("ccnx:/ndn/sppkans1", prefix) != None):
		return "wustl.edu/sppkans1"
	if(re.search("ccnx:/ndn/sppsalt1", prefix) != None):
		return "wustl.edu/sppsalt1"
	if(re.search("ccnx:/ndn/sppwash1", prefix) != None):
		return "wustl.edu/sppwash1"
	if(re.search("ccnx:/.*((\.edu)|(\.org)|(\.com)|(\.cn)|(\.uk))", prefix) == None):
		return "" #eval to false
	#checks if prefix is prefix for special case like REMAP
	if(re.search("ucla\.edu/apps", prefix) != None or re.search("remap\.ucla\.edu", prefix) != None):
		return "ucla.edu/remap" #matches domain for remap/special case in node_url list
	#removes ccnx:/
	prime = re.search("ccnx:/.*((\.edu)|(\.org)|(\.com)|(\.cn)|(\.uk))", prefix).group(0)[6:]
	#removes ndn/
	dprime = re.search("ndn/.*", prime)
	if(dprime != None):
		return dprime.group(0)[4:]
	return prime
#sort by domain, then by prefix if domains are the same
#args: fentry_list (a list of fentry objects--see fentry.py)
#retuns: a sorted version of fentry
def fentry_domain_sort(fentry_list):
	fentry_list.sort(key = lambda fentry: (fentry.get_domain(), fentry.get_prefix()))
	return fentry_list
#get all xml, run wget in background, output to file, then get from file to memory
#args: source_url--(a list containing tuples of following format: (xml url, domain of node, abbreviation of node)
#      the domain of the node can be an actual domain, or a fake one, it is made unique for sorting.
#      output_folder--output directory for all xml files received from wget
#      master_xml_list--a list to append the xml strings as you receive them
def get_all_xml(source_url, output_folder, master_xml_list, wait):
	p = subprocess.call(["rm", "-rf", output_folder])
	p = subprocess.call(["mkdir", output_folder])
	for node_tuple in source_url:
		#wget try once, time out after 5 seconds, quite(no output), background, specify output file
		#use n(xml_link, domain, name abbr)'s name abbr as temp file name.
		temp_filename = node_tuple[2]
		p = subprocess.Popen(["wget","-t 1","-T 2","-q","-b","-O",output_folder+temp_filename,node_tuple[0]], stdout=subprocess.PIPE)
	#wait for 3 seconds for xml to come back
	time.sleep(wait)
	for node_tuple in source_url:
		out = ""
		try:
			#open and read xml in temp files, may return error asynchronous access
			xml_file = open(output_folder+node_tuple[2],'r')
			for line in xml_file:
				out += line
			master_xml_list.append(out)
		except IOError as e:
			#if error occurs, append empty string as substitute for xml
			master_xml_list.append(out)
			continue
#returns list of valid forwarding entries for one node.
def get_fentry(xml_string):
	#???global xml_list
	fentry_list = []
	#p = subprocess.Popen(["wget","-t 1","-T 5","-q","-O", "-",xml_link], stdout=subprocess.PIPE)
	#exec shell command and puts it to out
	#out, err = p.communicate()
	#append the xml obtained for future uses.
	#this assumes wget will only be called once per status page
	#xml_list.append(out)
	#if nothing is in out, then return
	if(len(xml_string) == 0):
		return fentry_list
	try:
		xml = parseString(xml_string)
	except Exception as e:
		#there may be error from the asynchronous access, e.g. incomplete xml file was read.
		return fentry_list
	#look for testbed valid prefixes
	for pfx in xml.getElementsByTagName("prefix"):
		#get prefix form in between the tags
		prefix = re.search(">[^<]*<", pfx.toxml()).group(0)[1:-1]
		#any prefix that's local, internal, ping or black listed will be skipped
		if(not(is_testbed_prefix(prefix))):
			continue
		#is_testbed_prefix will add valid prefixes in hash table of valid prefixes (config.valid_prefix)
		#get domain from prefix

#compares stardard's time and comparison's time, gives color depending on the threshold given.
#eg: 1 and 5 are being compared, with thres_yellow = 5. the diff b/n the 2 times is 4 which 
#is < thre_yellow, therefore the result should be green. If the result is > thres_yellow and < thres_red, 
#then it's yellow. return results: 1 is green, 2 is yellow, 3 is red.
#delta is there to massage the results more towards the actual result. For example, the time
#given for the comparison will be the time displayed in the xml (when the xml was retrieved). The
#get_all_xml functios waits for 3 seconds when getting prefix status. When this function is called
#it will be at least 3 seconds later + calculation time for the lines of code appear before this
#function call. Therefore, we pass in a delta for additional subtraction.
def time_loe(standard, comparison, threshold_yellow, threshold_red, delta):
	if(standard == "" or comparison == ""):
		return 3
	std_day, std_time = standard.split(" ")[0].split("/"), standard.split(" ")[1].split(":")
	cmp_day, cmp_time = comparison.split(" ")[0].split("/"), comparison.split(" ")[1].split(":")
	for i in range(0, 3):
		std_day[i] = int(std_day[i])
		std_time[i] = int(std_time[i])
		cmp_day[i] = int(cmp_day[i])
		cmp_time[i] = int(cmp_time[i])
	std = (((std_day[0]*365)+(std_day[1]*30)+std_day[2])*86400)+((std_time[0]*3600)+(std_time[1]*60)+std_time[2])
	comp = (((cmp_day[0]*365)+(cmp_day[1]*30)+cmp_day[2])*86400)+((cmp_time[0]*3600)+(cmp_time[1]*60)+cmp_time[2])
	skew = (std - comp) - delta
	if(skew < 0): #abs val
		skew = skew * -1
	if(skew < threshold_yellow):
		return 1
	#green < skew <= yellow
	if(skew <= threshold_red):
		return 2
	#yellow < skew
	return 3

#returns valid prefixes. A prefix is valid if it identifies 
#a member of the topology and is forwarded by a face (of the
#current node) that uses a link in topology UNLESS
#the prefix is within the very same node it represents
#(e.g. finding prefix ccnx:/ndn/arizona.edu in node with domain
#arizona.edu will be considered valid)
def get_valid_prefixes(domain_name, xml_string):
	#a list of valid prefixes
	valid_list = []
	#if there's no xml, then return empty list
	if(xml_string == None or len(xml_string)==0):
		return valid_list
	try:
		#xml may be incomplete due to asynchronous
		#xml fetch. i.e. may be parsing before the
		#finish writing the entire xml
		pxml = parseString(xml_string)
	except Exception as e:
		return valid_list

	#create a hash table for all faces in the node and their
	#forwarding ip's for fast look up
	node_faces = dict()
	#all info for faces are embedded in face tag of XML
	for f in pxml.getElementsByTagName("face"):
		#this function returns a list, but each face
		#should have 1 and only 1 face id and ip
		if(len(f.getElementsByTagName("faceid")) == 0):
			continue
		#begin to extract the face number/face id
		if(re.search(">[^<]*<", f.getElementsByTagName("faceid")[0].toxml()) == None):
			continue
		#remove brackets
		fid = re.search(">[^<]*<", f.getElementsByTagName("faceid")[0].toxml()).group(0)[1:-1]
		#find ip of forwarding face via the same way for face id
		if(len(f.getElementsByTagName("ip"))==0):
			continue
		#try to extract the ip
		if(re.search(">[^<]*<", f.getElementsByTagName("ip")[0].toxml()) == None):
			continue
		#remove the brackets
		ip = re.search(">[^<]*<", f.getElementsByTagName("ip")[0].toxml()).group(0)[1:-1]
		#check to see if the topology uses such ip to forward
		dest_of_ip = config.ip_for_node.get(ip)
		if(not(dest_of_ip)):
			continue
		node_faces[fid] = ip

	#get all prefixes, which are embedded in the fentry tag
	for fentry in pxml.getElementsByTagName("fentry"):
		#this method always returns a list, even if there's
		#only 1 prefix
		plist = fentry.getElementsByTagName("prefix")
		#there should be 1 and only 1 prefix in the fentry
		if(len(plist) == 0):
			continue
		#try to extract the 1 prefix via regex
		if(re.search(">[^<]*<", plist[0].toxml()) == None):
			continue
		#remove brackets > <
		fprefix = re.search(">[^<]*<", plist[0].toxml()).group(0)[1:-1]
		#dictionary returns None if fprefix is not in it, which
		#counts as false. Anything else coutns as true
		if(not(config.valid_prefix.get(fprefix))):	
			continue
		#if the prefix represents the current node, i.e
		#it has the domain of domain_name, then it's valid
		if(get_domain(fprefix) == domain_name):
			valid_list.append(fprefix)
			continue
		#try to get the list forwarding face used for fprefix
		flist = fentry.getElementsByTagName("faceid")
		if(len(flist)==0):
			continue
		#Go through the list of faces and see 
		#if a link in the topology is used
		for i in range(0, len(flist)):
			#try to extract face number
			if(re.search(">[^<]*<", flist[i].toxml()) == None):
				continue
			#remove brackets
			face = re.search(">[^<]*<", flist[i].toxml()).group(0)[1:-1]
			#the node forwards the prefix through a face that uses a topology link
			#that's good enough, move on to the next prefix in the node
			if(node_faces.get(face)):
				valid_list.append(fprefix)
				break
	return valid_list
#html for header & start of body
def gen_html_start():
	html_start = """
<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<title>NDN Testbed Debug</title>
<link rel="stylesheet" type="text/css" href="style.css" />
<script type='text/javascript' src='http://ajax.googleapis.com/ajax/libs/jquery/1.6.4/jquery.min.js'></script>
<script type="text/JavaScript" src="mjs.js"></script>
</head>
"""
	return html_start

def gen_prefix_status_description():
	tbd = """
<br/>
<font size="4" face="arial"><p>Site Prefix Status:<br /></p></font>
<input id="b1" type="button" value="Show Site Prefix Status" style="width: 250px" onclick="changeTableStatus(this)"/>

<div id="table1" class="hidden">
<div class="td">
<ul>
<li class="l1">For each entry in the first row:
<ul>
		<li class="l2">
			<span class="c1"><table border ="1";><tr><td width = 100px; bgcolor ="#7CFC00";>&nbsp;</td></tr></table></span>
			<span class="c1f1">means the node is currently online.</span>
		</li> 
		<li class="l2">
			<span class="c1"><table border ="1";><tr><td width = 100px; bgcolor ="#FF0000";>&nbsp;</td></tr></table></span>
			<span class="c1f1">means the node is currently offline.</span>
		</li>
</ul></li>

<li class="l1">For the second row: each entry signifies the CCNX version used.</li>

<li class="l1">For the third row: each entry signifies start time of the node.</li>

<li class="l1">For the fourth row: each entry signifies clock skew between the entry and the machine for this script.
<ul>
<li class="l2">
	<span class="c1"><table border ="1";><tr><td width = 100px; bgcolor ="#7CFC00";>&nbsp;</td></tr></table></span>
	<span class="c1f1">means the clock skew is less than 5 seconds.</span>
</li>
<li class="l2">
	<span class="c1"><table border ="1";><tr><td width = 100px; bgcolor ="#FFFF00";>&nbsp;</td></tr></table></span>
	<span class="c1f1">means the clock skew is greater than 5 and less than or equal to 30 seconds.</span>
</li>
<li class="l2">
	<span class="c1"><table border ="1";><tr><td width = 100px; bgcolor ="#FF0000";>&nbsp;</td></tr></table></span>
	<span class="c1f1">means the clock skew is greater than 30 seconds.</span>
</li>
</ul></li>

<li class="l1">For everything below the fourth row:
<ul>
<li class="l2">
	<span class="c1"><table border ="1";><tr><td width = 100px; bgcolor ="#7CFC00";>&nbsp;</td></tr></table></span>
	<span class="c1f1">means the prefix appears on the ccndstatus page via an OSPFN route.</span>
</li>
<li class="l2">
	<span class="c1"><table border ="1";><tr><td width = 100px; bgcolor ="#FF0000";>&nbsp;</td></tr></table></span>
	<span class="c1f1">means the prefix does not appear.</span>
</li>
<li class="l2">
	<span class="c1"><table border ="1";><tr><td width = 100px; bgcolor ="#FFFF00";>&nbsp;</td></tr></table></span>
	<span class="c1f1">means the prefix does not appear, but the node may solely rely on AUTOREG to forward packets to internal hosts.</span>
</li>
<li class="l2">
	<span class="c1"><table border ="1";><tr><td width = 100px; bgcolor ="#C0C0C0";>&nbsp;</td></tr></table></span>
	<span class="c1f1">the prefix does not appear because the node is down.</span>
</li>
</ul></li>
</ul>
</div>
"""
	return tbd

#generates html to display forwarding entry status
#list of unique prefix, list of lists, each list represents list of prefixes for a node
def fes_html_gen(all_prefix):
	#a matrix that represents the table, html generation will be based on this matrix
	table_skeleton = []
	#list of node objects
	node_list = []
	#index (of config.node_url) for all offline nodes
	offline_nodes = []
	#used for the loop generating rows 2,3 and 4
	info_list = ["API", "Start Time (MST)", "Clock Skew"]
	#red, green, yellow, gray, empty space
	cell_content = ["#FF0000", "#7CFC00", "#FFFF00", "#C0C0C0", "&nbsp;"]
	#get time of this script generation
	p =subprocess.Popen(["date","+%Y/%m/%d %H:%M:%S"], stdout=subprocess.PIPE)
	out, err = p.communicate()
	#remove [2:-3] here and in ns.py for python, don't remove for python3
	out = str(out)[2:-3] + " (MST)"
	#generate description and beginning of the table
	html_code = gen_html_start()
	html_code += "<body><font size=\"5\" face=\"arial\">NDN Testbed Snapshot:"+out+"</font>"
	html_code += "<br />(Only the main site prefixes are shown)<br />"
	html_code += gen_prefix_status_description()
	
	#html_code += "<br />\n<form action=\"http://cgi.cs.arizona.edu/~yifengl/tbs.cgi\">\n"
	#html_code += "<input type=\"submit\" value=\"Refresh\"></form>\n<br>\n"
	table_width = str(300+len(config.node_url)*100)
	html_code += "<table border =\"1\"; width=\""+table_width+"px\";>\n<tr><td>&nbsp;</td>\n"

	#Build skeleton for table representation
	#+4 is for the first 4 rows.
	for i in range(0, len(all_prefix)+4):
		table_skeleton.append([])

	#gather reqired info for the first 4 rows
	for i in range(0, len(config.node_url)):
		#get_node_info is defined in ns.py
		node_list.append(get_node_info(config.xml_list[i], config.node_url[i][2]))

	#generates the first row (ONLINE or OFFLINE). Done in row major order (horizontally).
	for i in range(0, len(config.node_url)):
		if(node_list[i].get_stat() == "ONLINE"):
			table_skeleton[0].append(1) #online
		else:
			table_skeleton[0].append(0) #offline
			offline_nodes.append(i)

	#generate rows 2,3,4: API number, start time, and clock skew respectively. Done in row major order (horizontally).
	for i in range(0, len(info_list)):
		for j in node_list:
			#row 2
			if(i == 0):
				if(j.get_stat()== "ONLINE"):
					table_skeleton[1].append(j.get_api())
				else:
					table_skeleton[1].append(4) #&nbsp;
			#row 3
			if(i == 1):
				if(j.get_stat()== "ONLINE"):
					table_skeleton[2].append(j.get_start())
				else:	
					table_skeleton[2].append(4) #&nbsp;
			#row 4
			if(i == 2):
				if(j.get_stat() == "ONLINE"):
					skew = time_loe(j.get_machine_time(), j.get_node_time(), 5, 30, 3)
					if(skew == 1):
						table_skeleton[3].append(1) #green
					elif(skew == 2):
						table_skeleton[3].append(2) #yellow
					else:
						table_skeleton[3].append(0) #red
				else:
					table_skeleton[3].append(0) #red

	#generate the rest of the rows (5 and beyond). 
	#Done in column major order for optimization (veritcally/per node basis).
	#config.node_url is a list of tuples in format: n(xml_link, domain, name abbr).
	#Goto setup function for more in-depth description.

	#list containing lists of valid prefixes for each node
	all_prefixes_available = []
	for i in range(0, len(config.node_url)):
		#pass in the node's unique domain and xml
		prefixes_available = get_valid_prefixes(config.node_url[i][1], config.xml_list[i])
		all_prefixes_available.append(prefixes_available)

	#node_url is sorted via domain. XML for xml_list is obtained via this order 
	#as well. Therefore, the nodes and their correspond xml have the same indexing
	#for each prefix, check whether or not a node has the prefix
	#starting at the 5th row of table skeleton and beyond
	for j in range(4, len(table_skeleton)):
		for i in range(0, len(config.node_url)):
			#if the current node has this prefix, then color is green
			if(all_prefix[j-4].get_prefix() in all_prefixes_available[i]):
				table_skeleton[j].append(1) #green
			#if the current node is offline, then color is gray
			elif(i in offline_nodes):
				table_skeleton[j].append(3) #gray
			#if the current node does not have the prefix, but the
			#prefix is the prefix of the current node, then color is
			#yellow
			elif(not(all_prefix[j-4].get_prefix() in all_prefixes_available[i])
			and (all_prefix[j-4].get_domain() == config.node_url[i][1])):
				table_skeleton[j].append(2) #yellow
			#the current node do not have this prefix, color is red
			else:
				table_skeleton[j].append(0) #red

	all_url_links = dict()
	for i in range(0, len(config.node_url)):
		all_url_links[config.node_url[i][1]] = config.node_url[i][0][:-7]
	for i in range(0, len(table_skeleton)):
		if(i == 1):
			html_code += "<tr>\n<td width = 300px;>"+info_list[i-1]+"</td>\n"
		elif(i == 2):
			html_code += "<tr>\n<td width = 300px;>"+info_list[i-1]+"</td>\n"
		elif(i == 3):
			html_code += "<tr>\n<td width = 300px;>"+info_list[i-1]+"</td>\n"
		elif(i >= 4):
			link = all_url_links.get(get_domain(all_prefix[i-4].get_prefix()))
			if(link):
				html_code += "<tr>\n<td width = 300px;><a href=\""+link
				html_code += "\" target=\"_blank\">"+all_prefix[i-4].get_prefix()+"</a></td>\n"
			else:
				html_code += "<tr>\n<td width = 300px;><a href=\""
				html_code += "\" target=\"_blank\">"+all_prefix[i-4].get_prefix()+"</a></td>\n"

		#table_skeleton[i] should have the same length as config.node_url
		for j in range(0, len(config.node_url)):
			if(i == 0):
				if(table_skeleton[i][j] == 1):
					html_code += "<td width = 100px; bgcolor =\""+cell_content[1]+"\"><a href = \""
					html_code += config.node_url[j][0][:-7]+"\" target=\"_blank\">"+config.node_url[j][2]+"</td>\n"
				elif(table_skeleton[i][j] == 0):
					html_code += "<td width = 100px; bgcolor =\""+cell_content[0]+"\"><a href = \""
					html_code += config.node_url[j][0][:-7]+"\" target=\"_blank\">"+config.node_url[j][2]+"</td>\n"
			elif(i == 1):
				if(table_skeleton[i][j] == 4):
					html_code += "<td>"+cell_content[4]+"</td>\n"
				else:
					html_code += "<td>"+table_skeleton[i][j]+"</td>\n"
			elif(i == 2):
				if(table_skeleton[i][j] == 4):
					html_code += "<td>"+cell_content[4]+"</td>\n"
				else:
					html_code += "<td>"+table_skeleton[i][j]+"</td>\n"
			elif(i == 3):
				if(table_skeleton[i][j] == 1):
					html_code += "<td bgcolor =\""+cell_content[1]+"\">"+cell_content[4]+"</td>\n"
				elif(table_skeleton[i][j] == 2):
					html_code += "<td bgcolor =\""+cell_content[2]+"\">"+cell_content[4]+"</td>\n"
				elif(table_skeleton[i][j] == 0):
					html_code += "<td bgcolor =\""+cell_content[0]+"\">"+cell_content[4]+"</td>\n"
			else:
				if(table_skeleton[i][j] == 1):
					html_code += "<td bgcolor =\""+cell_content[1]+"\">"+cell_content[4]+"</td>\n"
				elif(table_skeleton[i][j] == 0):
					html_code += "<td bgcolor =\""+cell_content[0]+"\">"+cell_content[4]+"</td>\n"	
				elif(table_skeleton[i][j] == 3):
					html_code += "<td bgcolor =\""+cell_content[3]+"\">"+cell_content[4]+"</td>\n"
				elif(table_skeleton[i][j] == 2):
					html_code += "<td bgcolor =\""+cell_content[2]+"\">"+cell_content[4]+"</td>\n"
		html_code += "</tr>\n"
					
	html_code += "</table></div>\n"
	html_code += wp_table_gen()
	html_code += dl_html_gen()
	html_code += "<div><input id=\"b4\" type=\"button\" value=\"Show Topology\" style=\"width: 250px\" onclick=\"changeTableStatus(this)\"/></div>"
	html_code += "\n<div id=\"topo\" class=\"hidden\">\n"
	html_code += "<img border=\"0\" src=\"topology.png\" alt = \"testbed\" width=\"3500\" height=\"1200\"/></div>\n"
	html_code += "</body>\n</html>\n"
	return html_code

#Each node can advertise 2 kinds of prefixes:
#ccnx:/ndn/prefix and/or ccnx:/prefix
#We want to display only 1 (preferably ccnx:/ndn/prefix).
#Display the other only if the preferred prefix does not
#exist.
#Lists are passed by reference in python
def adjust_prefix_list(all_fentry_prefix):
	prefixes = dict()
	for i in all_fentry_prefix:
		prefixes[i.get_prefix()] = 1
	for prefix_key in config.names:
		#if prefixes has the ccnx:/prefix version of a prefix,
		#remove the ccnx:/prefix version if it exists.
		if(prefixes.get(prefix_key)):
			for j in range(0, len(all_fentry_prefix)):
				if(all_fentry_prefix[j].get_prefix() == config.names[prefix_key]):
					all_fentry_prefix.remove(all_fentry_prefix[j])
					#there are no duplicates, so it's safe
					#to remove just the first occurrence
					break
		#if prefixes does not have ccnx:/prefix version of a prefix,
		#then use ccnx:/prefix version if it exists. There is nothing
		#to do for this case

		#if both versions of the prefix is not in the hashtable
		#then add in the ccnx:/ndn/prefix version to show that
		#no one can see this prefix.

		#config.names[prefix_key] == "" could cause some problems,
		#most likely need to update the extensions in get_domain
		#This might will occur in setup, which means the p(..) node
		#contains a malformed ccnx ospf prefix
		elif(not(prefixes.get(prefix_key) and not(prefixes.get(config.names[prefix_key])))):
			all_fentry_prefix.append(Fentry(prefix_key, config.names[prefix_key]))
	fentry_domain_sort(all_fentry_prefix)

def fentry_status_gen():
	#every valid prefix(prefixes that represent a node in the topology e.g. ccnx:/ndn/some_website.edu)
	all_fentry_prefix = []
	all_nodes_prefix_lists = []
	my_output_file = "/home/yifengl/testbed/e/tbs.html"

	#get and store all xml from ccndstatus webages
	get_all_xml(config.node_url, "/home/yifengl/testbed/e/xmlfiles/", config.xml_list, 3);
	#print(datetime.now())
	for i in range(0, len(config.node_url)):
		#everything will be inserted into a hashtable of valid prefixes
		get_fentry(config.xml_list[i]) 

	for prefix_key in config.valid_prefix:
		#Fentry(prefix, domain)
		all_fentry_prefix.append(Fentry(prefix_key, config.valid_prefix[prefix_key]))

	#sort all prefixes alphabetical order, needed to make the table to look somewhat organized.
	#Also remove (unique) prefixes that represent the same node
	adjust_prefix_list(all_fentry_prefix)

	html_code = fes_html_gen(all_fentry_prefix)
	outFile = open(my_output_file, 'w')
	outFile.writelines(html_code)
	outFile.close()	

def main():
	#print(datetime.now())
	setup("/home/yifengl/testbed/e/config_file")
	fentry_status_gen()
	#print(datetime.now())
if __name__=="__main__":main()
