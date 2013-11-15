import re
import math
import config
import subprocess
import time
from tbs import *

def wp_setup(filename):
	config_file = open(filename, 'r')
	#9695 url
	node_list = []
	#9696 url
	wp_list = []
	#read in and save everything from wp_config_file
	for line in config_file:
		line_len = len(line)
		#nothing on this line, go to the next line
		if(line_len <= 0):
			continue
		#port 9695's url
		if(line[0] == "n"):
			#split elements separated by a comma + space after removing .( and )\n
			node_tuple = line[2:-2].split(", ")
			#place the elements in a tuple and insert into (local) node_list
			node_list.append((node_tuple[0], node_tuple[1], node_tuple[2]))
		#port 9696's url
		if(line[0] == "w"):
			wp_tuple = line[2:-2].split(", ")
			wp_list.append((wp_tuple[0], wp_tuple[1], wp_tuple[2]))	
	config_file.close()
	#sort the nodes of topology by domain
	node_list.sort(key = lambda tup: tup[1])
	wp_list.sort(key = lambda tup: tup[1])
	#insert sorted lists into global structs in config.py
	for node in node_list:
		config.wp_node_url.append(node)
	for node in wp_list:
		config.wp_wp_url.append(node)

def send_mail(addr, subject, msg, cc):
	p1 = subprocess.Popen(['echo', msg], stdout=subprocess.PIPE)
	p2 = subprocess.Popen(['mailx','-c', cc,'-s' ,subject, addr], stdin=p1.stdout)
	p1.stdout.close()
	output = p2.communicate()[0]

#optons: w+ for new files, w for existing files
def save_state(cur_state, filename, write_option):
	state_file = open(filename, write_option)
	output = ""
	#both rows should have the same length
	for i in range(len(cur_state)):
		for j in range(len(cur_state[i])):
			output += str(cur_state[i][j]) + ","
		output = output[:-1] + "\n" #remove last ","
	ouput = output[:-1] #remove last "\n"
	state_file.writelines(output)
	state_file.close()

def diff_states(cur_state, prev_state_file):
	try:
		i = 0
		#open previous state & check if any nodes went down
		state_file = open(prev_state_file, 'r')
		for line in state_file:
			prev_state = line.split(",")
			for index in range(0, len(prev_state)):
				if(cur_state[i][index] == 0 and prev_state[index] == "1"):
					alert_url = ""
					if(i == 0):
						alert_url = config.wp_node_url[index][0]
					else:
						alert_url = config.wp_wp_url[index][0]
					alert_msg = "Hello,\nThe NDN Testbed monitoring script (http://www.cs.arizona.edu/people/yifengl/tbs.html) "
					alert_msg += "detects node at ("+alert_url+") is currently down. Plese verify--send feedback "
					alert_msg += "if the script produced incorrect results.\nThanks!"
					#send_mail("yifengl@email.arizona.edu", "WebSocket Proxy is Down", alert_msg, "nano@remap.ucla.edu jburke@remap.ucla.edu")
			i +=1
		save_state(cur_state, prev_state_file, "w")

	except IOError as e:
		#previous state doesn't exist, write current state & be done 
		save_state(cur_state, prev_state_file, "w+")

def gen_wp_table_description():
	tbd ="""
<p><font size="4" face="arial"><p>WebSocket Proxy Status:<br /></p></font>
<br\><input id = "b2" type="button" value="Show WebSocket Proxy Status" style="width: 250px" onclick="changeTableStatus(this)"/>
<div id="table2" class="hidden">
<div class="td">
<div><p>Shows the status of the websocket proxies.</p></div>
<ul>
<li class="l1">For each entry in the first row:
<ul>
	<li class="l2">
		<span class="c1"><table border ="1";><tr><td width = 100px; bgcolor ="#7CFC00";>&nbsp;</td></tr></table></span>
		<span class="c1f1">means CCNx of current node (port 9695) is online.</span>
	</li> 
	<li class="l2">
		<span class="c1"><table border ="1";><tr><td width = 100px; bgcolor ="#FF0000";>&nbsp;</td></tr></table></span>
		<span class="c1f1">means CCNx of current node (port 9695) is offline.</span>
	</li>
</ul>
</li>

<li class="l1">For each entry in the second row:
<ul>
		<li class="l2">
			<span class="c1"><table border ="1";><tr><td width = 100px; bgcolor ="#7CFC00";>&nbsp;</td></tr></table></span>
			<span class="c1f1">means TCP connections can be established with port 9696(WebSocket Proxy) of current node.</span>
		</li> 
		<li class="l2">
			<span class="c1"><table border ="1";><tr><td width = 100px; bgcolor ="#FF0000";>&nbsp;</td></tr></table></span>
			<span class="c1f1">means TCP connections cannot be established with port 9696 (WebSocket Proxy) of current node.</span>
		</li>
</ul>
</li>
</ul>
</div>
"""
	return tbd

def wp_table_gen():
	up = 1 #assume a node is online by default, change to down if detected otherwise
	wp_setup("/home/yifengl/testbed/e/wp_config_file") #read information from setup file
	cell_content = ["#FF0000", "#7CFC00", "#FFFF00", "#C0C0C0", "&nbsp;"] #red, green, yellow, gray, empty space
	#get status of port 9695
	get_all_xml(config.wp_node_url, "/home/yifengl/testbed/e/wp_xml_files/", config.wp_xml_list, 1)
	#get status of port 9696
	get_all_xml(config.wp_wp_url, "/home/yifengl/testbed/e/wp_wp_res/", config.wp_wp_res, 1)

	#representation of the table that will be desplayed (not used for html gen, but state checking)
	current_state = [[],[]]
	for i in range(0, len(config.wp_node_url)):	
		current_state[0].append(1)
		current_state[1].append(1)
	
	#rough estimate of a good size for the entire table
	table_width = str(200+len(config.wp_node_url)*100)
	#gen fixed html, used for easy modification for future javascripts
	html_code = gen_wp_table_description()
	#gen actual table
	html_code += "<table border =\"1\"; width=\""+table_width+"px\";>\n<tr><td>CCNx Stack Status</td>\n" 

	for i in range(0, len(config.wp_node_url)):
		#if no xml response, then assume the 9695 is down
		if(config.wp_xml_list[i] == ""):
			up = 0
			current_state[0][i] = 0
		#color cell accordingly
		html_code +="<td width = 100px; bgcolor =\""+cell_content[up]+"\"><a href = \""
		html_code +=config.wp_node_url[i][0][:-7]+"\" target=\"_blank\">"+config.wp_node_url[i][2]+"</td>\n"
		up = 1 #always assume node is online, change to offline if detected otherwise
	html_code += "</tr>\n" #end of row
	html_code += "<tr><td>Proxy Status</td>\n"
	up = 1
	#do same thing for port 9696
	for i in range(0, len(config.wp_wp_res)):
		if(len(config.wp_wp_res[i]) < 1):
			up = 0
			current_state[1][i] = 0
		html_code +="<td width = 100px; bgcolor =\""+cell_content[up]+"\">&nbsp;</td>\n"
		up = 1
	html_code += "</tr>\n</table>\n\n</div>\n"
	#send email to operators if necessary
	diff_states(current_state, "/cs/www/people/yifengl/proxy_states")
	return html_code	
