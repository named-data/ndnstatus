import re
import config
import subprocess
from xml.dom.minidom import parse, parseString

def get_direct_links(xml_string):
	dl_list = []
	if(len(xml_string) == 0):
		return dl_list
	try:
		xml = parseString(xml_string)
	except Exception as e:
		return dl_list
	for ip in xml.getElementsByTagName("ip"):
		res = re.search(">[^<]*<", ip.toxml())
		if(res != None):
			res = re.search("10\.0\..*", res.group(0))
			if(res != None):
				dl_list.append(res.group(0)[:-1])
	return dl_list

def get_all_links(node_url):
	all_links = []
	for i in range(0, len(node_url)):
		all_links.append(get_direct_links(config.xml_list[i]))
	return all_links

def gen_dl_table_description():
	tbd = """
<br />
<br />
<div><font size="4" face="arial">Tunnel Configuration Status:</font></div>
<br/>
<input id = "b3" type="button" value="Show Tunnel Configuration Status" style="width: 250px" onclick="changeTableStatus(this)"/>
<div id="table3" class="hidden">
<div class="td">
<div><p>Shows whether a tunnel is configured according to the testbed topology.</p></div>

<li class="l1">
<ul>
<li class="l2">
	<span class="c1"><table border ="1";><tr><td width = 100px; bgcolor ="#7CFC00";>&nbsp;</td></tr></table></span>
	<span class="c1f1">means tunnel is configured correctly.</span>
</li>
<li class="l2">
	<span class="c1"><table border ="1";><tr><td width = 100px; bgcolor ="#FF0000";>&nbsp;</td></tr></table></span>
	<span class="c1f1">means tunnel is not configured.</span>
</li>
<li class="l2">
	<span class="c1"><table border ="1";><tr><td width = 100px; bgcolor ="#C0C0C0";>&nbsp;</td></tr></table></span>
	<span class="c1f1">means tunnel is not in topology, and not configured.</span>
</li>
</ul>
</li>
</div>
"""
	return tbd

def dl_html_gen():
	table_width = str(300+len(config.node_url)*100)
	html_code = gen_dl_table_description()
	html_code += "</p><table border =\"1\"; width=\""+table_width+"px\";>\n<tr><td>&nbsp;</td>\n"
	all_links = []
	planned_links = config.planned_links
	current_links = config.current_links
	node_url = config.node_url
	llist = config.llist
	all_links = get_all_links(node_url)
	unknown = ""
	errors = ""
	#print(all_links)
	for i in range(0, len(all_links)):
		for j in all_links[i]:
			in_list = False
			for k in range(0, len(llist)):
				if(llist[k][0] == j and node_url[i][2] == llist[k][1]):
					current_links[llist[k][3]][llist[k][4]] = 1
					in_list = True
					break
				elif(llist[k][0] == j and node_url[i][2] != llist[k][1]):
					errors += "Possible Error detected: " + llist[k][0] + " from: " + node_url[i][2] + "<br />\n"
					in_list = True
			if(not(in_list)):
				unknown += "Unknown link detected: " + j + " in "+node_url[i][2]+"<br />\n"
	#print(current_links)
	for i in range(0, len(node_url)):
		html_code += "<td width = 100px;><a href = \""+node_url[i][0][:-7]+"\" target=\"_blank\">"+node_url[i][2]+"</a></td>\n"
	html_code += "</tr>\n"
	for i in range(0, len(current_links)):
		html_code += "<tr><td><a href = \""+node_url[i][0][:-7]+"\" target=\"_blank\">"+node_url[i][2]+"</a></td>\n"
		for j in range (0, len(current_links[i])):
			if(planned_links[i][j] == 1 and current_links[i][j] == 1):
				html_code += "<td bgcolor =\"#7CFC00\">&nbsp;</td>\n"
			elif(planned_links[i][j] == 1 and current_links[i][j] == 0):
				html_code += "<td bgcolor =\"#FF0000\">&nbsp;</td>\n"
			elif(planned_links[i][j] == 0 and current_links[i][j] == 1):
				html_code += "<td bgcolor =\"#00FFFF\">&nbsp;</td>\n"
			else:
				html_code += "<td bgcolor =\"#C0C0C0\">&nbsp;</td>\n"
		html_code += "</tr>\n"
	html_code += "</table>\n"
	if(unknown != ""):
		html_code += "<p><br />Additional Links:<br />" +unknown+"</p>\n"
	if(errors != ""):
		html_code += "<p><br />Errors Encountered:<br />" +errors+"</p>\n"
	else:
		html_code += "<p><br />Errors Encountered: None!<br /></p>\n"
	html_code += "</div>\n"
	return html_code
