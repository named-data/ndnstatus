#This files contains variables used by the other files
#A list of xml's for each node
xml_list = []
#correspond to n(...)'s format in config_file 
node_url = []
#(ip used by node1 to forward to node 2, node1, node2)
llist = []
#p(prefix, domain of prefix)
names = dict()
#adjacency matrix of all planned links
planned_links = []
#adjacency matrix of all current links detected
current_links = []
#list of prefixes that should be skipped
invalid_prefix = []
#hash table of valid prefixes for fast lookup
#key: perfix #value: 1 (value is not important)
valid_prefix = dict()
#hash table of valid links for fast lookup
#key: node1's abbreviated name>>node2's abbreviated name
#e.g. UA>>UCLA, look at setup function in tbs.py for more details
#value: ip used for node1 to forward to node2
#valid_link = dict()
#hash table of all valid ip's for every node
#key: ip, value: node's abbreviated name
ip_for_node = dict()
#contains tuples n(...) in wp_config_file
wp_node_url = []
#stores xml's from wget for web proxy nodes
wp_xml_list = []
#prefix = key, domain the prefix belongs to = value, 
#look for p(...) in wp_config_file
wp_names = dict()
#urls of port 9696 webproxy
wp_wp_url = []
#wget result for urls in wp_wp_url
wp_wp_res = []
#more later
