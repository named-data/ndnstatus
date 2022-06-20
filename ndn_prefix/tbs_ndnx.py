import re
import math
import config
import subprocess
import time
from ns import *
from dls import *
#from wp import *
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
versions_file_list = []
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
		#same domains. 
		if(line[0] == "n"):
                        # n(http://hobo.cs.arizona.edu:80/?f=xml, edu/arizona, ARIZONA, ndn:/ndn/edu/arizona)
			#split elements separated by a comma + space after removing .( and )\n
			node_tuple = line[2:-2].split(", ")
			#place the elements in a tuple and insert into (local) node_list
			node_list.append((node_tuple[0], node_tuple[1], node_tuple[2]))
                        #print "node_tuple[3]: ", node_tuple[3]
			config.names[node_tuple[3]] = "ndn:/"+node_tuple[3][9:]
			config.valid_prefix[node_tuple[3]] = get_domain(node_tuple[3])

		#for adding new planned topology links. 
		#format: l(node1 name, node1 ip, node2 name, node2 ip)
		#e.g. l(UA, 10.0.1.29:9695, UCSD, 10.0.1.30:9695) represent
		#UA (10.0.1.29:9695) ------------ (10.0.1.30:9695) UCSD
		#Thus UA will forward to 10.0.1.30:9695 to get to UCSD
		#node names are equivalent of name abbr in node_list/n(...)'s
		#elif(line[0] == "l"):
		#	link_tuple = line[2:-2].split(", ")
		#	#format: (ip used by node1 to forward to node 2, node1, node2)
		#	#consult testbed topology image for more details
		#	link_list.append((link_tuple[3], link_tuple[0], link_tuple[2]))
		#	#format: (dictionary[node1>>node2] = ip used by node1 to forward to node 2)
		#	#consult testbed topology image for more details
		#	config.valid_link[link_tuple[0]+">>"+link_tuple[2]] = link_tuple[3]
		#	#format = dic[ip] = node
		#	#ip is an ip used by a member of the topology to forward to node
		#	config.ip_for_node[link_tuple[3]] = link_tuple[2]
		#	#ip used by node2 to forward to node 1
		#	link_list.append((link_tuple[1], link_tuple[2], link_tuple[0]))
		#	#from node2 to forward to node1, this up is used
		#	config.valid_link[link_tuple[2]+">>"+link_tuple[0]] = link_tuple[1]
		#	config.ip_for_node[link_tuple[1]] = link_tuple[0]

		#new prefix...
		#since ndnx allows pretty much anything, there isn't a sure fire way
		#filter the wanted prefixes. Currently, the program has a general filter,
		#but if it blocks some useful prefixes, use this to explicitly add it.
		elif(line[0] == "p"):
			name_tuple = line[2:-2].split(", ")
			config.names[name_tuple[0]] = "ndn:/"+name_tuple[0][9:]
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
#	prefix: any ccnx URI, e.g. ndn:/ndn/arizona.edu
#RETURN: 
#	True: if the function considers prefix to be testbed valid
#	False: if the function considers prefix to be invalid
def is_testbed_prefix(prefix):
	#if in list of invalid prefixes, return false.
	#may change to hash table later.
        print "is_testbed_prefix( " + prefix + " )"
	if(prefix in config.invalid_prefix):
                print "is_testbed_prefix(  FALSE: confg.invalid_prefix  )"
		return False
	#more special cases, added before the invalid list is implemented
	if(re.search("(ndn:/trace)|(ping)|(C1\.M\.K)|(parc\.com/host/ccngw)|(metwi)|(uiuc\.edu/test)|(apps/..*)", prefix) != None):
                print "is_testbed_prefix(  FALSE: trace,ping,parc... )"
		return False
	#more special cases, added before the invalid list is implemented
	if(re.search("(internal)", prefix) != None):
                print "is_testbed_prefix(  FALSE: internal  )"
		return False
	#more special cases (at least 1 char following the /)
	#ucla special cases
	if(re.search("(ndn:/ndn/ucla.edu/%C1\.S\.*)", prefix) != None):
                print "is_testbed_prefix(  FALSE: internal  )"
		return False
	#if(re.search("(ndn:/ndn/ucla.edu/%40GUEST\.*)", prefix) != None):
	#	return False
        #print "is_testbed_prefix( " + prefix + " )"
	if(re.search("(\%40GUEST)", prefix) != None):
                print "is_testbed_prefix(  FALSE: GUEST  )"
		return False
	if(re.search("(KEY)", prefix) != None):
                print "is_testbed_prefix(  FALSE: KEY  )"
		return False
	#if(re.search("(\.%40GUEST)", prefix) != None):
	#	return False
	#if(re.search("(/ndn/edu/\.*/%40GUEST\.*)", prefix) != None):
	#	return False
	#if(re.search("(/ndn/edu/ucla/%40GUEST\.*)", prefix) != None):
	#	return False
	if(re.search("(\.edu)|(\.org)|(\.com)|(\.ca)|(\.cn)|(\.es)|(\.ch)|(\.uk)|(\.de)|(\.in)|(\.fr)|(\.id)|(\.br)|(\.mx)|(\.at)|(\.jp)|(\.ma)|(\.nl)|(\.th)|(\.gov)|(\.no)|(\.kr)|(\.it)|(\.pt)|(\.aws)", prefix) != None):
		config.valid_prefix[prefix] = get_domain(prefix)
                print "is_testbed_prefix( TRUE )"
		return True
        print "is_testbed_prefix( FALSE: bottom )"
	return False 
#get domain name from prefix
#args: prefix (any prefix)
#returns: "" if cannot find proper domain, "ucla/metwi" for REMAP, domain of prefix, eg "website.com" for "ndn:/ndn/website.com"
def get_domain(prefix):
	#special cases for prefixes that share the same domain
	#give them unique fake domains
        #JDD: Looks like this test forces there to be a .something in each prefix.  We are going away from that...

	#if(re.search("ndn:/.*((\.edu)|(\.org)|(\.com)|(\.cn)|(\.uk))", prefix) == None):
        #        print "get_domain(" + prefix + ") returning false: "
	#	return "" #eval to false

	if(re.search("ndn:/.*((edu)|(org)|(com)|(ca)|(cn)|(es)|(ch)|(uk)|(no)|(de)|(kr)|(it)|(id)|(br)|(mx)|(at)|(jp)|(ma)|(nl)|(th)|(gov)|(in)|(fr)|(pt)|(aws))", prefix) == None):
                #print "get_domain(" + prefix + ") returning false: "
		return "" #eval to false

	#checks if prefix is prefix for special case like REMAP
	if(re.search("ucla\.edu/apps", prefix) != None or re.search("remap\.ucla\.edu", prefix) != None):
                #print "get_domain(" + prefix + ") returning false: ucla.edu/remap"
		return "ucla.edu/remap" #matches domain for remap/special case in node_url list
	#removes ndn:/
	#prime = re.search("ndn:/.*((\.edu)|(\.org)|(\.com)|(\.cn)|(\.uk))", prefix).group(0)[6:]
	#prime = re.search("ndn:/.*((\.edu)|(\.org)|(\.com)|(\.cn)|(\.uk))", prefix).group(0)[5:]
	prime = re.search("ndn:/.*((edu)|(org)|(com)|(ca)|(cn)|(es)|(ch)|(uk)|(no)|(kr)|(it)|(de)|(id)|(br)|(mx)|(at)|(jp)|(ma)|(nl)|(th)|(gov)|(in)|(fr)|(pt)|(aws)).*", prefix).group(0)[5:]
        #print "get_domain(" + prefix + ") prime: " + prime
	#removes ndn/
	dprime = re.search("ndn/.*", prime)
	if(dprime != None):
                #print "get_domain(" + prefix + ") returning dprime.group(0)[4:]: " + dprime.group(0)[4:]
		return dprime.group(0)[4:]
        #print "get_domain(" + prefix + ") returning prime: " + prime
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
	versions_folder = output_folder + "../versions/"
	p = subprocess.call(["rm", "-rf", output_folder])
	p = subprocess.call(["mkdir", "-p", output_folder])
	p = subprocess.call(["mkdir", "-p", versions_folder])
	for node_tuple in source_url:
		#wget try once, time out after 5 seconds, quite(no output), background, specify output file
		#use n(xml_link, domain, name abbr)'s name abbr as temp file name.
		temp_filename = node_tuple[2]
		p = subprocess.Popen(["wget","--no-check-certificate", "-t 2","-T 10","-q","-b","-O",output_folder+temp_filename,node_tuple[0]], stdout=subprocess.PIPE)
                print "wget --no-check-certificate -t 2 -T 10 -q -b -O " + output_folder + temp_filename + " " + node_tuple[0] + " "
		#split_node_tuple0 = node_tuple[0].split("?") 
		#versions_file = split_node_tuple0[0] + "/versions.txt"
		#print "attempting to wget " + versions_file + " and put it here " + versions_folder + temp_filename
		#q = subprocess.Popen(["wget","-d","-t 2","-T 10","-q","-O",versions_folder+temp_filename,versions_file], stdout=subprocess.PIPE)
	#wait for wait seconds for xml to come back
	time.sleep(10)
	for node_tuple in source_url:
		out = ""
		try:
			#open and read xml in temp files, may return error asynchronous access
			#print "checking status of xml file for " + temp_filename
			xml_file = open(output_folder+node_tuple[2],'r')
			for line in xml_file:
				out += line
                        if(len(out) == 0):
                                # empty. Try wget again. it must have failed
		                out = ""
                                xml_file.close()
		                temp_filename = node_tuple[2]
                                # wait a few seconds first?
		                p = subprocess.Popen(["wget","-d","-t 2","-T 10","-q","-O",output_folder+temp_filename,node_tuple[0]], stdout=subprocess.PIPE)
                                print "Second Attempt(foreground with debug): wget -d -t 2 -T 10 -q -O " + output_folder + temp_filename + " " + node_tuple[0] + " "
	                        time.sleep(10)
			        xml_file = open(output_folder+node_tuple[2],'r')
			        for line in xml_file:
				        out += line
                                if(len(out) == 0):
                                        print "Second Attempt came up empty also"
                                else:
                                        print "Second Attempt returned data"
                	if(len(out) != 0):
		                temp_filename = node_tuple[2]
				# We got an xml file so we should try for the versions file, but only try once
				split_node_tuple0 = node_tuple[0].split("?") 
				versions_file = split_node_tuple0[0] + "/versions.txt"
				#print "attempting to wget " + versions_file + " and put it here " + versions_folder + temp_filename
				p = subprocess.Popen(["wget","--no-check-certificate","-d","-t 2","-T 10","-q","-O",versions_folder+temp_filename,versions_file], stdout=subprocess.PIPE)
                                print "wget --no-check-certificate -t 2 -T 10 -q -b -O " + versions_folder + temp_filename + " " + versions_file + " "
			master_xml_list.append(out)
			versions_file_list.append(versions_folder+temp_filename)
		except IOError as e:
			#if error occurs, append empty string as substitute for xml
                        print "get_all_xml(): except IOError as e: setting empty xml_list e = " + e
			master_xml_list.append(out)
			continue

#returns list of valid forwarding entries for one node.
def get_fentry(xml_string):
	#???global xml_list
	fentry_list = []
	#p = subprocess.Popen(["wget","-t 1","-T 10","-q","-O", "-",xml_link], stdout=subprocess.PIPE)
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
        #print "standard " + standard
        #print "comparison " + comparison
	if(standard == "" or comparison == ""):
		return 3
	std_day, std_time = standard.split(" ")[0].split("/"), standard.split(" ")[1].split(":")
	cmp_day, cmp_time = comparison.split(" ")[0].split("/"), comparison.split(" ")[1].split(":")
	for i in range(0, 3):
                #print "std_time[i] " + std_time[i]
                #print "std_day[i] " + std_day[i]
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
#(e.g. finding prefix ndn:/ndn/arizona.edu in node with domain
#arizona.edu will be considered valid)
def get_valid_prefixes(domain_name, xml_string):
	#a list of valid prefixes
	valid_list = []
        #print "get_valid_prefixes: domain_name: " + domain_name
        #print "get_valid_prefixes(" + domain_name + ", xml_string: " + xml_string + ")"
        #if (domain_name == "cn/edu/bupt"):
        #  print "get_valid_prefixes(" + domain_name + ", xml_string: " + xml_string + ")"
	#if there's no xml, then return empty list
	if(xml_string == None or len(xml_string)==0):
                #print "get_valid_prefixes() no xml. returning empy list"
		return valid_list
	try:
		#xml may be incomplete due to asynchronous
		#xml fetch. i.e. may be parsing before the
		#finish writing the entire xml
		pxml = parseString(xml_string)
	except Exception as e:
                print "get_valid_prefixes() exception return"
		return valid_list

        #if (domain_name == "cn/edu/bupt"):
        #  print "creating hash table"
	#create a hash table for all faces in the node and their
	#forwarding ip's for fast look up
	node_faces = dict()
	#all info for faces are embedded in face tag of XML
	for f in pxml.getElementsByTagName("face"):
		#this function returns a list, but each face
		#should have 1 and only 1 face id and ip
		if(len(f.getElementsByTagName("faceId")) == 0):
			continue
		#begin to extract the face number/face id
		if(re.search(">[^<]*<", f.getElementsByTagName("faceId")[0].toxml()) == None):
			continue
		#remove brackets
		fid = re.search(">[^<]*<", f.getElementsByTagName("faceId")[0].toxml()).group(0)[1:-1]
		#find ip of forwarding face via the same way for face id
		if(len(f.getElementsByTagName("remoteUri"))==0):
			continue
		#try to extract the ip
		if(re.search(">[^<]*<", f.getElementsByTagName("remoteUri")[0].toxml()) == None):
			continue
		#remove the brackets
		ip = re.search(">[^<]*<", f.getElementsByTagName("remoteUri")[0].toxml()).group(0)[1:-1]
		#check to see if the topology uses such ip to forward
		dest_of_ip = config.ip_for_node.get(ip)
		if(not(dest_of_ip)):
			continue
		node_faces[fid] = ip

        #if (domain_name == "cn/edu/bupt"):
        #  print "getting all prefixes"
	#get all prefixes, which are embedded in the fentry tag
	for fentry in pxml.getElementsByTagName("fibEntry"):
                #if (domain_name == "cn/edu/bupt"):
                #  print "checking fentry: " 
		#this method always returns a list, even if there's
		#only 1 prefix
		plist = fentry.getElementsByTagName("prefix")
		#there should be 1 and only 1 prefix in the fentry
		if(len(plist) == 0):
                        #if (domain_name == "edu/ucla"):
                        #  print "continue len(plist) == 0"
			continue
		#try to extract the 1 prefix via regex
		if(re.search(">[^<]*<", plist[0].toxml()) == None):
                        #if (domain_name == "edu/ucla"):
                        #  print "continue re.search == None"
			continue
		#remove brackets > <
		fprefix = re.search(">[^<]*<", plist[0].toxml()).group(0)[1:-1]
                #if (domain_name == "cn/edu/bupt"):
                #  print "checking fprefix: " + fprefix
		#dictionary returns None if fprefix is not in it, which
		#counts as false. Anything else coutns as true
                ndnfprefix = "ndn:" + fprefix
		#if(not(config.valid_prefix.get(fprefix))):	
		if(not(config.valid_prefix.get(ndnfprefix))):	
                        #print "continue not(config.valid_prefix.get()"
                        #if (domain_name == "edu/ucla"):
                        #  print "continue not config.valid_prefix.get() fprefix: " + fprefix + " ndnfprefix: " + ndnfprefix
			continue
		#if the prefix represents the current node, i.e
		#it has the domain of domain_name, then it's valid
                #print "checking for prefix representing current node. domain_name: " + domain_name + " fprefix: " + fprefix + " get_domain(fprefix): " + get_domain(fprefix)
		if(get_domain(ndnfprefix) == domain_name):
                        #if (domain_name == "edu/ucla"):
                        #print "adding to valid list, fprefix for our domain: " + fprefix
			valid_list.append(ndnfprefix)
                        #print "valid_list.append(fprefix) because in domain. fprefix: " + fprefix
			continue
		#try to get the list forwarding face used for fprefix
		flist = fentry.getElementsByTagName("faceId")
		if(len(flist)==0):
                        #if (domain_name == "edu/ucla"):
                        #  print "continue len(flist) == 0"
			continue
		#Go through the list of faces and see 
		#if a link in the topology is used
		for i in range(0, len(flist)):
			#try to extract face number
			if(re.search(">[^<]*<", flist[i].toxml()) == None):
                                #if (domain_name == "edu/ucla"):
                                #  print "found no face number. continue"
				continue
			#remove brackets
			face = re.search(">[^<]*<", flist[i].toxml()).group(0)[1:-1]
			#the node forwards the prefix through a face that uses a topology link
			#that's good enough, move on to the next prefix in the node
			if(node_faces.get(face)):
                                #print "appending fprefix: " + fprefix
                                #if (domain_name == "edu/ucla"):
                                #print "adding to valid list, fprefix forwarded through face on a topology link: " + fprefix
				valid_list.append(ndnfprefix)
				break
                        else:
                                #print "adding to valid list, else of if(node_faces.get(face)) face: " + face + " fprefix: " + fprefix
				valid_list.append(ndnfprefix)
				break
        #if (domain_name == "cn/edu/bupt"):
        #  print "returning valid_list:"
        #  print valid_list
        #print "returning valid_list:"
        #print valid_list
        #print "get_valid_prefixes() end return"
	return valid_list
#html for header & start of body
def gen_html_start():
	html_start = """
<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<title>NDN Testbed Status</title>
<link rel="stylesheet" type="text/css" href="style.css" />
<script type='text/javascript' src='http://ajax.googleapis.com/ajax/libs/jquery/1.6.4/jquery.min.js'></script>
<script type="text/JavaScript" src="mjs.js"></script>
</head>
"""
	return html_start

def gen_prefix_status_description():
	tbd = """
<br/>
<font size="3" face="arial">Site Prefix Status: (Green: node has FIB entry for prefix; Red: no FIB entry; Yellow: no FIB entry but prefix is in node's domain) <br></font>
<font size="3" face="arial">Clock Skew Status: (As compared to UCLA Node's time: Green: < 5 secs off; Yellow: 5 <  > 30 secs; Red: > 30 seconds off) <br><br></font>
<font size="3" face="arial">Notes on current (March 14, 2017) status: Hyperbolic Routing is now the default for NLSR on the Testbed. <br></font>
<font size="3" face="arial">Notes on current (Feb. 20, 2018) status: We are expanding what is reported at the top of this status table. Versions for NLSR, ndn-cxx and libchronosync are blank right now, they are coming soon....<br></font>
<font size="3" face="arial">Notes on current (Apr. 14, 2018) status: We are in the process of changing over to TLS/https access for the ndn status page. Some nodes will look down when they might not be.<br></font>
<font size="3" face="arial">Notes on current (July 24, 2018) status: Adding line to status page for TLS certificate expiry. <br></font>
<font size="3" face="arial">Notes on current (October 22, 2018) status: Updated to NFD 0.6.4. <br></font>
<font size="3" face="arial">Notes on current (November 1, 2018) status: We are having some serious problems with the new build of NLSR. Expect Testbed nodes to be up and down a lot while we test and debug. <br></font>
<font size="3" face="arial">Notes on current (March 11, 2019) status: We are upgrading NDN Testbed nodes to latest release of NFD and NLSR. This includes NLSR changes that are incompatible with previous version so things will be disjoint as they get updated. <br></font>
<font size="3" face="arial">Notes on current (March 13, 2019) status: A bunch of site certs need updating. Things will be bumpy for a while today.. <br></font>
<font size="3" face="arial">Notes on current (April 7, 2019) status: We will be removing some long dormant sites. <br></font>
<font size="3" face="arial">Notes on current (June 16, 2020) status: A 'New NFD Status' line has been added. . <br></font>
<font size="3" face="arial">Notes on current (April 23, 2021) status: UCLACS (spurs.cs.ucla.edu) removed from Testbed. <br></font>
<font size="3" face="arial">Notes on current (May 7, 2021) status: Added a link near the bottom of this page to a geographically accurate image of the Testbed topology. <br></font>
<font size="3" face="arial">Notes on current (Nov 1, 2021) status: In an effort to stay more up to date, we are going to start experimenting with installing NDN packages from the nightly build repo supported by Junxiao. <br></font>
<font size="3" face="arial">Notes on current (Nov 17, 2021) status: Having another go at this, this week: In an effort to stay more up to date, we are going to start experimenting with installing NDN packages from the nightly build repo supported by Junxiao. <br></font>
<br>

"""
	return tbd

#<font size="3" face="arial">Notes on current (October 2, 2015) status: Our status server is getting truncated responses from BUPT. The node is up but the because of the errors the status page reports it as down.<br></font>

#generates html to display forwarding entry status
#list of unique prefix, list of lists, each list represents list of prefixes for a node
def fes_html_gen(all_prefix):
	Node_Name_row = 1
        New_Status_row = 2
        OS_Version_row = 3
        NFD_Version_row = 4
        ndn_cxx_Version_row = 5
        NLSR_Version_row = 6
        ChronoSync_Version_row = 7
        PSync_Version_row = 8
        NFD_Uptime_row = 9
        NLSR_Uptime_row = 10
        TLS_Expiry_row = 11
        SiteCert_Expiry_row = 12
        Current_Time_row = 13
        #UTC_NLSR_StartTime_row = 10
        #UTC_Current_NLSR_Time_row = 11
        #Clock_Skew_row = 12
        Clock_Skew_row = 14
	#a matrix that represents the table, html generation will be based on this matrix
	table_skeleton = []
	#list of node objects
	node_list = []
	#index (of config.node_url) for all offline nodes
	offline_nodes = []
	#used for the loop generating rows 2,3 and 4
	#info_list = ["Version", "Start Time (UTC) ", "Current Time (UTC)", "Clock Skew"]
	info_list = ["New NFD Status", "OS Version", "NFD Version", "libndn-cxx Version", "NLSR Version", "ChronoSync Version", "PSync Version", "NFD Up Time ", "NLSR Up Time", "TLS Expiry", "Site Cert Expiry", "Current Time (UTC)", "Clock Skew"]
	#red, green, yellow, gray, empty space
	cell_content = ["#FF0000", "#7CFC00", "#FFFF00", "#C0C0C0", "&nbsp;"]
	#get time of this script generation
	p =subprocess.Popen(["date","+%Y/%m/%d %H:%M:%S %Z"], stdout=subprocess.PIPE)
	out, err = p.communicate()
	#remove [2:-3] here and in ns.py for python, don't remove for python3
	#out = str(out)[2:-3] + " (CST)"
	#out = str(out) + " (CST)"
	#generate description and beginning of the table
	html_code = gen_html_start()
	html_code += "<br />"
	html_code += "<br />"
        html_code += "<body><font size=\"4\" face=\"arial\">Note the new site location http://ndndemo.arl.wustl.edu/ndn.html</font>\n"
        html_code += "\n"
	html_code += "<br />"
	html_code += "<br />"
        html_code += "<body><font size=\"4\" face=\"arial\">Other NDN status pages:</font>\n"
        html_code += "\n"
	#html_code += "<br />"
        #html_code += "<DT> <A HREF=\"http://ndndemo.arl.wustl.edu/cacti/\">NDN Testbed Cacti graphs </A>"
        #html_code += "\n"
	html_code += "<br />"
        html_code += "<DT> <A HREF=\"https://nlsr-status.ndn.today/\">NDN Routing (NLSR Status)</A>"
        html_code += "\n"
	html_code += "<br />"
	html_code += "<br />"
	#html_code += "<br />"
        #html_code += "<DT> <A HREF=\"https://ivisa.named-data.net/testbed_map/\">Chavoosh's Node Status map</A>"
        #html_code += "\n"
	html_code += "<br />"
        #html_code += "<DT> <A HREF=\"http://ether.remap.ucla.edu/anmol/proxystatus.html\">NDN Proxies</A>"
        #html_code += "\n"
	#html_code += "<br />"
	html_code += "<br />"
	html_code += "<body><font size=\"4\" face=\"arial\">NDN Testbed Snapshot:"+out+"</font>"
	html_code += "<br />(Status updates every 10 minutes)<br />"
	html_code += "<br />(Only the main site prefixes are shown)<br />"
	html_code += gen_prefix_status_description()
	
	#html_code += "<br />\n<form action=\"http://cgi.cs.arizona.edu/~yifengl/tbs.cgi\">\n"
	#html_code += "<input type=\"submit\" value=\"Refresh\"></form>\n<br>\n"
	table_width = str(180+len(config.node_url)*70)
	html_code += "<table border =\"1\"; width=\""+table_width+"px\";>\n<tr><td>&nbsp;</td>\n"

	#Build skeleton for table representation
	#+5 is for the first 5 rows.
	#for i in range(0, len(all_prefix)+5):
	for i in range(0, len(all_prefix)+Clock_Skew_row):
		table_skeleton.append([])

	#gather reqired info for the first 5 rows
	for i in range(0, len(config.node_url)):
		#get_node_info is defined in ns.py
		#node_list.append(get_node_info(config.xml_list[i], config.node_url[i][2]))
		N = get_node_info(config.xml_list[i], config.node_url[i][2], versions_file_list[i])
                if ( N.get_name() == "UCLA") :
                    #print "Found UCLA"
                    standard_ucla_time = N.get_node_time()
                    #print "found UCLA setting standard_ucla_time: " + standard_ucla_time
		node_list.append(N)

	#generates the first row (ONLINE or OFFLINE). Done in row major order (horizontally).
	for i in range(0, len(config.node_url)):
		if(node_list[i].get_stat() == "ONLINE"):
			table_skeleton[Node_Name_row-1].append(1) #online
		else:
                        print "Marking a node as OFFLINE" 
			table_skeleton[Node_Name_row-1].append(0) #offline
			offline_nodes.append(i)

	for i in range(0, len(config.node_url)):
		if(node_list[i].get_stat() == "ONLINE"):
			table_skeleton[New_Status_row-1].append(1) #online
		else:
                        print "Marking a node as OFFLINE" 
			table_skeleton[New_Status_row-1].append(0) #offline
			#offline_nodes.append(i)

	#generate rows 2,3,4,5: API number, start time, current time and clock skew respectively. Done in row major order (horizontally).
	for i in range(0, len(info_list)):
		for j in node_list:
			#row 2 NFD Version
			#if(i == 0):
			if(i == (OS_Version_row - 2)):
				if(j.get_stat()== "ONLINE"):
					table_skeleton[OS_Version_row -1].append(j.get_os_version())
				else:
					table_skeleton[OS_Version_row -1].append(4) #&nbsp;
                                #table_skeleton[OS_Version_row -1].append(4) #&nbsp;
			if(i == (NFD_Version_row - 2)):
				if(j.get_stat()== "ONLINE"):
					table_skeleton[NFD_Version_row -1].append(j.get_nfd_version())
				else:
					table_skeleton[NFD_Version_row -1].append(4) #&nbsp;
                        if(i == (ndn_cxx_Version_row - 2)):
                                if(j.get_stat()== "ONLINE"):
                                       table_skeleton[ndn_cxx_Version_row-1].append(j.get_ndn_cxx_version())
                                else:
                                       table_skeleton[ndn_cxx_Version_row-1].append(4) #&nbsp;
                                #table_skeleton[ndn_cxx_Version_row -1].append(4) #&nbsp;
                        if(i == (NLSR_Version_row - 2)):
                                if(j.get_stat()== "ONLINE"):
                                       table_skeleton[NLSR_Version_row-1].append(j.get_nlsr_version())
                                else:
                                       table_skeleton[NLSR_Version_row-1].append(4) #&nbsp;
                                #table_skeleton[NLSR_Version_row -1].append(4) #&nbsp;
			if(i == (ChronoSync_Version_row - 2)):
				if(j.get_stat()== "ONLINE"):
					table_skeleton[ChronoSync_Version_row-1].append(j.get_chronosync_version())
				else:
					table_skeleton[ChronoSync_Version_row-1].append(4) #&nbsp;
				#table_skeleton[ChronoSync_Version_row -1].append(4) #&nbsp;
			if(i == (PSync_Version_row - 2)):
				if(j.get_stat()== "ONLINE"):
					table_skeleton[PSync_Version_row-1].append(j.get_psync_version())
				else:
					table_skeleton[PSync_Version_row-1].append(4) #&nbsp;
			#row 3 NFD Up Time
			if(i == (NFD_Uptime_row - 2)):
				if(j.get_stat()== "ONLINE"):
                                        p =subprocess.Popen(["date","-u","-d "+j.get_start(),"+%s"], stdout=subprocess.PIPE)
	                                start_time_secs, err = p.communicate()
                                        #print "start_time_secs " + start_time_secs
                                        p =subprocess.Popen(["date","-u","-d "+j.get_node_time(),"+%s"], stdout=subprocess.PIPE)
	                                node_time_secs, err = p.communicate()
                                        #print "node_time_secs " + node_time_secs
                                        elapsed_secs=int(node_time_secs)-int(start_time_secs)
                                        #print "elapsed_secs %d" % (elapsed_secs)
                                        elapsed_days=elapsed_secs/(60*60*24)
                                        remaining_secs=elapsed_secs - (elapsed_days * 60*60*24)
                                        elapsed_hours=remaining_secs/(60*60)
                                        remaining_secs=remaining_secs - (elapsed_hours * 60*60)
                                        elapsed_mins=remaining_secs/(60)
                                        remaining_secs=remaining_secs - (elapsed_mins * 60)
                                        if (elapsed_days > 1) :
                                          up_time_str=" "+str(elapsed_days)+" days"
                                          #print "Up %d days" % (elapsed_days)
                                        else:
                                          if (elapsed_days > 0) :
                                            up_time_str=" "+str(elapsed_days)+" day"
                                            #print "Up %d day" % (elapsed_days)
                                          else:
                                            if (elapsed_hours > 0) :
                                              up_time_str=" "+str(elapsed_hours)+"h:"+str(elapsed_mins)+"m"
                                              #print "Up %dh:%dm" % (elapsed_hours, elapsed_mins)
                                            else:
                                              up_time_str=" "+str(elapsed_mins)+"m:"+str(remaining_secs)+"s"
                                              #print "Up %dm %ds" % (elapsed_mins, remaining_secs)
					      #table_skeleton[2].append(j.get_start())
                                        #print up_time_str
                                        #print "%dd %dh %dm %ds" % (elapsed_days, elapsed_hours, elapsed_mins, remaining_secs)
					#table_skeleton[2].append(j.get_start())
					table_skeleton[NFD_Uptime_row - 1].append(up_time_str)
                                        #print "after j.get_start() table_skeleton[2] = " + str(table_skeleton[2])
				else:	
					table_skeleton[NFD_Uptime_row - 1].append(4) #&nbsp;
                        if(i == (NLSR_Uptime_row - 2)):
                                if(j.get_stat()== "ONLINE"):
                                        print "NAME: " + j.get_name()
                                        start_time_secs = j.get_nlsr_start_time()
                                        print "NLSR start_time_secs >" + start_time_secs + "<"
                                        node_time_secs = j.get_nlsr_current_time()
                                        print "NLSR node_time_secs >" + node_time_secs + "<"
                                        #if ((node_time_secs == '' ) or (start_time_secs == '')):
                                        if ((node_time_secs and start_time_secs ) and (len(node_time_secs) > 1) and (len(start_time_secs) > 1)):
                                          elapsed_secs=int(node_time_secs)-int(start_time_secs)
                                        else:
                                          elapsed_secs=0
                                        print "NLSR elapsed_secs %d" % (elapsed_secs)
                                        elapsed_days=elapsed_secs/(60*60*24)
                                        remaining_secs=elapsed_secs - (elapsed_days * 60*60*24)
                                        elapsed_hours=remaining_secs/(60*60)
                                        remaining_secs=remaining_secs - (elapsed_hours * 60*60)
                                        elapsed_mins=remaining_secs/(60)
                                        remaining_secs=remaining_secs - (elapsed_mins * 60)
                                        if (elapsed_days > 1) :
                                          up_time_str=" "+str(elapsed_days)+" days"
                                          #print "Up %d days" % (elapsed_days)
                                        else:
                                          if (elapsed_days > 0) :
                                            up_time_str=" "+str(elapsed_days)+" day"
                                            #print "Up %d day" % (elapsed_days)
                                          else:
                                            if (elapsed_hours > 0) :
                                              up_time_str=" "+str(elapsed_hours)+"h:"+str(elapsed_mins)+"m"
                                              #print "Up %dh:%dm" % (elapsed_hours, elapsed_mins)
                                            else:
                                              up_time_str=" "+str(elapsed_mins)+"m:"+str(remaining_secs)+"s"
                                              #print "Up %dm %ds" % (elapsed_mins, remaining_secs)
                                              #table_skeleton[2].append(j.get_start())
                                        #print up_time_str
                                        #print "%dd %dh %dm %ds" % (elapsed_days, elapsed_hours, elapsed_mins, remaining_secs)
                                        #table_skeleton[2].append(j.get_start())
                                        table_skeleton[NLSR_Uptime_row - 1].append(up_time_str)
                                        #print "after j.get_start() table_skeleton[2] = " + str(table_skeleton[2])
                                else:
                                        table_skeleton[NLSR_Uptime_row - 1].append(4) #&nbsp;
                        #if(i == (NLSR_Uptime_row - 2)):
                        #        #if(j.get_stat()== "ONLINE"):
                        #        #       table_skeleton[1].append(j.get_nfd_version())
                        #        #else:
                        #        #       table_skeleton[1].append(4) #&nbsp;
                        #        table_skeleton[NLSR_Uptime_row -1].append(4) #&nbsp;
			#row 4 Current Time (UTC)
			if(i == (TLS_Expiry_row - 2)):
				if(j.get_stat()== "ONLINE"):
					table_skeleton[TLS_Expiry_row-1].append(j.get_tls_expiry())
				else:
					table_skeleton[TLS_Expiry_row-1].append(4) #&nbsp;
			if(i == (SiteCert_Expiry_row - 2)):
				if(j.get_stat()== "ONLINE"):
					table_skeleton[SiteCert_Expiry_row-1].append(j.get_sitecert_expiry())
				else:
					table_skeleton[SiteCert_Expiry_row-1].append(4) #&nbsp;
			if(i == (Current_Time_row - 2)):
				if(j.get_stat()== "ONLINE"):
					table_skeleton[Current_Time_row - 1].append(j.get_node_time())
                                        #print "adding get_node_time() to table: " + j.get_node_time()
				else:	
					table_skeleton[Current_Time_row - 1].append(4) #&nbsp;
                                        #print "NOT adding get_node_time() to table: " + j.get_node_time()
			# UTC NLSR Start time
			#if(i == (UTC_NLSR_StartTime_row - 2)):
			#	if(j.get_stat()== "ONLINE"):
			#		table_skeleton[UTC_NLSR_StartTime_row - 1].append(j.get_utc_nlsr_start_time())
                        #                #print "adding get_node_time() to table: " + j.get_node_time()
			#	else:	
			#		table_skeleton[UTC_NLSR_StartTime_row - 1].append(4) #&nbsp;
                        #                #print "NOT adding get_node_time() to table: " + j.get_node_time()
			# UTC Current Time for NLSR calc.
			#if(i == (UTC_Current_NLSR_Time_row - 2)):
			#	if(j.get_stat()== "ONLINE"):
			#		table_skeleton[UTC_Current_NLSR_Time_row - 1].append(j.get_utc_current_nlsr_time())
                        #                #print "adding get_node_time() to table: " + j.get_node_time()
			#	else:	
			#		table_skeleton[UTC_Current_NLSR_Time_row - 1].append(4) #&nbsp;
                        #                #print "NOT adding get_node_time() to table: " + j.get_node_time()
			# Clock Skew
			if(i == (Clock_Skew_row - 2)):
				if(j.get_stat() == "ONLINE"):
                                        #print "calculating skew: machine_time: " + j.get_machine_time() 
                                        #print "calculating skew: standard_ucla_time: " + standard_ucla_time 
                                        #print "calculating skew: node_time: " + j.get_node_time()
					#skew = time_loe(j.get_machine_time(), j.get_node_time(), 5, 30, 3)

					#skew = time_loe(standard_ucla_time, j.get_node_time(), 5, 30, 3)
					skew = time_loe(standard_ucla_time, j.get_node_time(), 5, 30, 0)
                                        #skew = 1
					if(skew == 1):
						table_skeleton[Clock_Skew_row-1].append(1) #green
					elif(skew == 2):
						table_skeleton[Clock_Skew_row-1].append(2) #yellow
					else:
						table_skeleton[Clock_Skew_row-1].append(0) #red
				else:
					table_skeleton[Clock_Skew_row-1].append(0) #red

	#generate the rest of the rows (6 and beyond). 
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
	#for j in range(5, len(table_skeleton)):
	for j in range(Clock_Skew_row, len(table_skeleton)):
                #print "fes_html_gen() checking prefix: " + all_prefix[j-4].get_prefix()
		for i in range(0, len(config.node_url)):
                        #for k in range(0, len(all_prefixes_available[i])):
                        #    print "all_prefixes_available[i:%d][k:%d]: %s " % (i, k, all_prefixes_available[i][k])
			#if the current node has this prefix, then color is green
			if(all_prefix[j-Clock_Skew_row].get_prefix() in all_prefixes_available[i]):
				table_skeleton[j].append(1) #green
			#if the current node is offline, then color is gray
			elif(i in offline_nodes):
				table_skeleton[j].append(3) #gray
			#if the current node does not have the prefix, but the
			#prefix is the prefix of the current node, then color is
			#yellow
			elif(not(all_prefix[j-Clock_Skew_row].get_prefix() in all_prefixes_available[i])
			and (all_prefix[j-Clock_Skew_row].get_domain() == config.node_url[i][1])):
                                #print "fes_html_gen() setting table_skeleton[%d] to YELLOW" % j
				table_skeleton[j].append(2) #yellow
			#the current node do not have this prefix, color is red
			else:
                                #print "fes_html_gen() setting table_skeleton[%d] to RED" % j
				table_skeleton[j].append(0) #red

	all_url_links = dict()
	for i in range(0, len(config.node_url)):
		#all_url_links[config.node_url[i][1]] = config.node_url[i][0][:-7]
		all_url_links[config.node_url[i][1]] = config.node_url[i][0][:-1]
	for i in range(0, len(table_skeleton)):
		if(i == Node_Name_row):
			html_code += "<tr>\n<td width = 180px;>"+"<font size=\"2\">"+info_list[i-1]+"</td>"+"</font>\n"
		elif(i == New_Status_row):
			html_code += "<tr>\n<td width = 180px;>"+"<font size=\"2\">"+info_list[i-1]+"</td>"+"</font>\n"
		elif(i == OS_Version_row):
			html_code += "<tr>\n<td width = 180px;>"+"<font size=\"2\">"+info_list[i-1]+"</td>"+"</font>\n"
		elif(i == NFD_Version_row):
			html_code += "<tr>\n<td width = 180px;>"+"<font size=\"2\">"+info_list[i-1]+"</td>"+"</font>\n"
		elif(i == ndn_cxx_Version_row):
			html_code += "<tr>\n<td width = 180px;>"+"<font size=\"2\">"+info_list[i-1]+"</td>"+"</font>\n"
		elif(i == NLSR_Version_row):
			html_code += "<tr>\n<td width = 180px;>"+"<font size=\"2\">"+info_list[i-1]+"</td>"+"</font>\n"
		elif(i == ChronoSync_Version_row):
			html_code += "<tr>\n<td width = 180px;>"+"<font size=\"2\">"+info_list[i-1]+"</td>"+"</font>\n"
		elif(i == PSync_Version_row):
			html_code += "<tr>\n<td width = 180px;>"+"<font size=\"2\">"+info_list[i-1]+"</td>"+"</font>\n"
		elif(i == NFD_Uptime_row):
			html_code += "<tr>\n<td width = 180px;>"+"<font size=\"2\">"+info_list[i-1]+"</td>"+"</font>\n"
		elif(i == NLSR_Uptime_row):
			html_code += "<tr>\n<td width = 180px;>"+"<font size=\"2\">"+info_list[i-1]+"</td>"+"</font>\n"
		elif(i == TLS_Expiry_row):
			html_code += "<tr>\n<td width = 180px;>"+"<font size=\"2\">"+info_list[i-1]+"</td>"+"</font>\n"
		elif(i == SiteCert_Expiry_row):
			html_code += "<tr>\n<td width = 180px;>"+"<font size=\"2\">"+info_list[i-1]+"</td>"+"</font>\n"
		elif(i == Current_Time_row):
			html_code += "<tr>\n<td width = 180px;>"+"<font size=\"2\">"+info_list[i-1]+"</td>"+"</font>\n"
		#elif(i == UTC_NLSR_StartTime_row):
		#	html_code += "<tr>\n<td width = 180px;>"+"<font size=\"2\">"+info_list[i-1]+"</td>"+"</font>\n"
		#elif(i == UTC_Current_NLSR_Time_row):
		#	html_code += "<tr>\n<td width = 180px;>"+"<font size=\"2\">"+info_list[i-1]+"</td>"+"</font>\n"
		elif(i >= Clock_Skew_row):
			link = all_url_links.get(get_domain(all_prefix[i-Clock_Skew_row].get_prefix()))
			if(link):
				html_code += "<tr>\n<td width = 180px;><a href=\""+link
				html_code += "\" target=\"_blank\">"+"<font size=\"2\">"+all_prefix[i-Clock_Skew_row].get_prefix()+"</a></td>"+"</font>\n"
			else:
				html_code += "<tr>\n<td width = 180px;><a href=\""
				html_code += "\" target=\"_blank\">"+"<font size=\"2\">"+all_prefix[i-Clock_Skew_row].get_prefix()+"</a></td>"+"</font>\n"

		#table_skeleton[i] should have the same length as config.node_url
		for j in range(0, len(config.node_url)):
			#print "i,j " + str(i) + " " + str(j)
			if(i == (Node_Name_row -1)):
				if(table_skeleton[i][j] == 1):
					html_code += "<td width = 70px; bgcolor =\""+cell_content[1]+"\"><a href = \""
					html_code += config.node_url[j][0][:-1]+"\" target=\"_blank\">"+"<font size=\"2\">"+config.node_url[j][2]+"</td>"+"</font>\n"
				elif(table_skeleton[i][j] == 0):
					html_code += "<td width = 70px; bgcolor =\""+cell_content[0]+"\"><a href = \""
					html_code += config.node_url[j][0][:-1]+"\" target=\"_blank\">"+"<font size=\"2\">"+config.node_url[j][2]+"</td>"+"</font>\n"
			elif(i == (New_Status_row -1)):
				if(table_skeleton[i][j] == 1):
					html_code += "<td width = 70px; bgcolor =\""+cell_content[1]+"\"><a href = \""
					html_code += config.node_url[j][0][:-1]+"/n/"+"\" target=\"_blank\">"+"<font size=\"2\">"+config.node_url[j][2]+"</td>"+"</font>\n"
				elif(table_skeleton[i][j] == 0):
					html_code += "<td width = 70px; bgcolor =\""+cell_content[0]+"\"><a href = \""
					html_code += config.node_url[j][0][:-1]+"/n/"+"\" target=\"_blank\">"+"<font size=\"2\">"+config.node_url[j][2]+"</td>"+"</font>\n"
                        #Version
			elif(i == (OS_Version_row -1)):
				if(table_skeleton[i][j] == 4):
					html_code += "<td><font size=\"2\">"+cell_content[4]+"</font></td>\n"
				else:
					html_code += "<td><font size=\"2\">"+table_skeleton[i][j]+"</font></td>\n"
			elif(i == (NFD_Version_row -1)):
				if(table_skeleton[i][j] == 4):
					html_code += "<td><font size=\"2\">"+cell_content[4]+"</font></td>\n"
				else:
					html_code += "<td><font size=\"2\">"+table_skeleton[i][j]+"</font></td>\n"
			elif(i == (ndn_cxx_Version_row -1)):
				if(table_skeleton[i][j] == 4):
					html_code += "<td><font size=\"2\">"+cell_content[4]+"</font></td>\n"
				else:
					html_code += "<td><font size=\"2\">"+table_skeleton[i][j]+"</font></td>\n"
			elif(i == (NLSR_Version_row -1)):
				if(table_skeleton[i][j] == 4):
					html_code += "<td><font size=\"2\">"+cell_content[4]+"</font></td>\n"
				else:
					html_code += "<td><font size=\"2\">"+table_skeleton[i][j]+"</font></td>\n"
			elif(i == (ChronoSync_Version_row -1)):
				if(table_skeleton[i][j] == 4):
					html_code += "<td><font size=\"2\">"+cell_content[4]+"</font></td>\n"
				else:
					html_code += "<td><font size=\"2\">"+table_skeleton[i][j]+"</font></td>\n"
			elif(i == (PSync_Version_row -1)):
				if(table_skeleton[i][j] == 4):
					html_code += "<td><font size=\"2\">"+cell_content[4]+"</font></td>\n"
				else:
					html_code += "<td><font size=\"2\">"+table_skeleton[i][j]+"</font></td>\n"
			elif(i == (NFD_Uptime_row -1)):
				if(table_skeleton[i][j] == 4):
					html_code += "<td><font size=\"2\">"+cell_content[4]+"</font></td>\n"
				else:
					html_code += "<td><font size=\"2\">"+table_skeleton[i][j]+"</font></td>\n"
			elif(i == (NLSR_Uptime_row -1)):
				if(table_skeleton[i][j] == 4):
					html_code += "<td><font size=\"2\">"+cell_content[4]+"</font></td>\n"
				else:
					html_code += "<td><font size=\"2\">"+table_skeleton[i][j]+"</font></td>\n"
			elif(i == (TLS_Expiry_row -1)):
				if(table_skeleton[i][j] == 4):
					html_code += "<td><font size=\"2\">"+cell_content[4]+"</font></td>\n"
				else:
					html_code += "<td><font size=\"2\">"+table_skeleton[i][j]+"</font></td>\n"
			elif(i == (SiteCert_Expiry_row -1)):
				if(table_skeleton[i][j] == 4):
					html_code += "<td><font size=\"2\">"+cell_content[4]+"</font></td>\n"
				else:
					#html_code += "<td bgcolor =\""+cell_content[0]+"\">"+cell_content[4]+"</td>\n"
					#html_code += "<td bgcolor =\"#7CFC00\"><font size=\"2\">"+table_skeleton[i][j]+"</font></td>\n"
					html_code += "<td><font size=\"2\">"+table_skeleton[i][j]+"</font></td>\n"
			elif(i == (Current_Time_row -1)):
                                #print "checking table_skeleton[i][j] to RED" ,  i,j
				if(table_skeleton[i][j] == 4):
					html_code += "<td><font size=\"2\">"+cell_content[4]+"</font></td>\n"
				else:
					html_code += "<td><font size=\"2\">"+table_skeleton[i][j]+"</font></td>\n"
			#elif(i == (UTC_NLSR_StartTime_row -1)):
                        #        print "checking table_skeleton[i][j] to RED" ,  i,j
			#	if(table_skeleton[i][j] == 4):
			#		html_code += "<td><font size=\"2\">"+cell_content[4]+"</font></td>\n"
			#	else:
			#		html_code += "<td><font size=\"2\">"+table_skeleton[i][j]+"</font></td>\n"
			#elif(i == (UTC_Current_NLSR_Time_row -1)):
                        #        print "checking table_skeleton[i][j] to RED" ,  i,j
			#	if(table_skeleton[i][j] == 4):
			#		html_code += "<td><font size=\"2\">"+cell_content[4]+"</font></td>\n"
			#	else:
			#		print "html_code: " + html_code
			#		print "<td><font size=\"2\">"+table_skeleton[i][j]+"</font></td>\n"
			#		html_code += "<td><font size=\"2\">"+table_skeleton[i][j]+"</font></td>\n"
			elif(i == (Clock_Skew_row -1)):
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
	#html_code += wp_table_gen()
	#html_code += dl_html_gen()
	#html_code += "<div><input id=\"b4\" type=\"button\" value=\"Show Topology\" style=\"width: 250px\" onclick=\"changeTableStatus(this)\"/></div>"
	#html_code += "\n<div id=\"topo\" class=\"hidden\">\n"
	html_code += "<br />"
	html_code += "<br />"
	html_code += "<br />"
        html_code += "<DT> <A HREF=\"http://ndndemo.arl.wustl.edu/topology2.png\">Click here for a Geographically accurate topology image</A>"
        html_code += "\n"
	html_code += "<br />"
	#html_code += "<img border=\"0\" src=\"topology.png\" alt = \"testbed\" width=\"1600\" height=\"800\"/></div>\n"
	html_code += "<img border=\"0\" src=\"topology.png\" alt = \"testbed\" width=\"2400\" height=\"1200\"/></div>\n"
	html_code += "</body>\n</html>\n"
	return html_code

#Each node can advertise 2 kinds of prefixes:
#ndn:/ndn/prefix and/or ndn:/prefix
#We want to display only 1 (preferably ndn:/ndn/prefix).
#Display the other only if the preferred prefix does not
#exist.
#Lists are passed by reference in python
def adjust_prefix_list(all_fentry_prefix):
	prefixes = dict()
	for i in all_fentry_prefix:
		prefixes[i.get_prefix()] = 1
	for prefix_key in config.names:
		#if prefixes has the ndn:/prefix version of a prefix,
		#remove the ndn:/prefix version if it exists.
		if(prefixes.get(prefix_key)):
			for j in range(0, len(all_fentry_prefix)):
				if(all_fentry_prefix[j].get_prefix() == config.names[prefix_key]):
					all_fentry_prefix.remove(all_fentry_prefix[j])
					#there are no duplicates, so it's safe
					#to remove just the first occurrence
					break
		#if prefixes does not have ndn:/prefix version of a prefix,
		#then use ndn:/prefix version if it exists. There is nothing
		#to do for this case

		#if both versions of the prefix is not in the hashtable
		#then add in the ndn:/ndn/prefix version to show that
		#no one can see this prefix.

		#config.names[prefix_key] == "" could cause some problems,
		#most likely need to update the extensions in get_domain
		#This might will occur in setup, which means the p(..) node
		#contains a malformed ccnx ospf prefix
		elif(not(prefixes.get(prefix_key) and not(prefixes.get(config.names[prefix_key])))):
			all_fentry_prefix.append(Fentry(prefix_key, config.names[prefix_key]))
	fentry_domain_sort(all_fentry_prefix)

def fentry_status_gen():
	#every valid prefix(prefixes that represent a node in the topology e.g. ndn:/ndn/some_website.edu)
	all_fentry_prefix = []
	all_nodes_prefix_lists = []
	my_output_file = "/home/jdd/WU-ARL/ndnstatus/ndn_prefix/tbs_ndnx.html"

	#get and store all xml from ccndstatus webages
	get_all_xml(config.node_url, "/home/jdd/WU-ARL/ndnstatus/ndn_prefix/xmlfiles/", config.xml_list, 10);
        ## handle UCLA differently
	#subprocess.call(["cp", "/home/research/jdd/Library/HTML/Public/ndnstatus/ndn_prefix/xmlfiles/UCLA", "/home/research/jdd/Library/HTML/Public/ndnstatus/ndn_prefix/xmlfiles/UCLA.html"])
	#subprocess.call(["/home/research/jdd/Library/HTML/Public/ndnstatus/ndn_prefix/processUCLA.sh", "/home/research/jdd/Library/HTML/Public/ndnstatus/ndn_prefix/xmlfiles/UCLA.html", "/home/research/jdd/Library/HTML/Public/ndnstatus/ndn_prefix/xmlfiles/UCLA"])
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
	setup("/home/jdd/WU-ARL/ndnstatus/ndn_prefix/config_file_ndnx")
	fentry_status_gen()
	#print(datetime.now())
if __name__=="__main__":main()
