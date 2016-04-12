#!/usr/bin/env python
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys


edges_with_labels={}
nodes_with_positions={}

def process_nodes():
  shortNametWords = {}
  positionWords = {}

  #print "process_nodes():"
  f = open('geocode.json','r')

  foundShortName = False
  foundPosition = False

  line = f.readline()

  #print "line: ", line
  while line != '' :
    words = line.split()
    #print "words[0]: ", words[0]
    if words[0] == "\"shortname\":":
      #words = line.split(':')
      #print "found line with shortname"
      shortNameWords = words[1].split(',')
      foundShortName = True
      shortName = shortNameWords[0][1:len(shortNameWords[0])-1]
      #print "shortName: ", shortName
    if words[0] == "\"position\":":
      indexLB = line.find("[")
      indexRB = line.find("]")
      indexCOMMA = line.find(",")
      #print "indexLB: ", indexLB, " indexCOMMA: ", indexCOMMA, " indexRB: ", indexRB
      #print "line[LB+1,COMMA]: ", line[indexLB+1:indexCOMMA]
      #print "line[COMMA+1,RB]: ", line[indexCOMMA+1:indexRB]
      x = float(line[indexLB+1:indexCOMMA])
      y = float(line[indexCOMMA+1:indexRB])
      #print "x,y", x, ", ", y
      foundPosition = True
    if foundShortName == True and foundPosition == True :
      nodes_with_positions[shortName] = (x,y)
      #print "processed node: ", shortName, "with position: x: ", x, "y: ", y
      foundShortName = False
      foundPosition = False
    line = f.readline()
    #print "line: ", line

def process_edges():
  startWords = {}
  endWords = {}
  labelWords = {}


  f = open('links.json','r')

  foundStart = False
  foundEnd = False
  foundLabel = False
  line = f.readline()

  while line != '' :
    words = line.split()
    if words[0] == "\"start\":":
      startWords = words[1].split(',')
      #print "found Start", startWords[0]
      foundStart = True
      startName = startWords[0][1:len(startWords[0])-1]
    if words[0] == "\"end\":":
      endWords = words[1].split(',')
      #print "found End", endWords[0]
      foundEnd = True
      endName = endWords[0][1:len(endWords[0])-1]
    if words[0] == "\"nlsr_weight\":":
      labelWords = words[1].split(',')
      #print "found label", labelWords[0]
      foundLabel = True
    if foundStart == True and foundEnd == True and foundLabel == True:
      #print "(", startWords[0], ",", endWords[0], "): ", labelWords[0]
      edge = (startName, endName)
      edges_with_labels[edge] = labelWords[0]
      foundStart = False
      foundEnd = False
      foundLabel = False
    #print line
    line = f.readline()
  
def NDN_graph():

    #nodes_with_positions={'WU': (38.14907010, -90.30334710), 'UIUC': (40.60260390, -88.23171080000002), 'UM': (35.11860990, -89.93700109999999), 'UA': (32.22896140, -110.94832260), 'URJC': (40.3359, -3.8732)}
    #edges_with_labels={('WU','UIUC'): '9', ('WU', 'UM'): '17', ('WU', 'UA'): '33', ('WU', 'URJC'): '86'}


    process_edges()
    process_nodes()

    G=nx.Graph()
    G.position={}
    G.edge_labels = {}

    for n,(y,x) in nodes_with_positions.iteritems():
        node = n
        # USA
        if node == "NEU":
          x = x + 10
          y = y + 20
        if node == "UIUC":
          x = x - 1
          y = y + 2
        if node == "WU":
          x = x - 6
          y = y - 3
        if node == "UM":
          x = x + 7
          y = y - 8
        if node == "MICH":
          x = x 
          y = y + 12
        if node == "NIST":
          x = x + 13
          y = y + 11
        if node == "UA":
          y = y - 10
        if node == "CAIDA":
          x = x - 20
          y = y - 20
        if node == "BYU":
          y = y + 20
          x = x - 5
        if node == "CSU":
          y = y + 10
          x = x 
        if node == "UCLA":
          y = y + 10
          x = x -20
        if node == "REMAP":
          y = y + 3
          x = x -2
        if node == "UCI":
          x = x - 6
          y = y - 6
        # EUROPE
        if node == "LIP6":
          x = x + 9
          y = y + 2
        if node == "NTNU":
          y = y 
          x = x 
        if node == "COPELABS":
          y = y - 25
          x = x 
        if node == "URJC":
          y = y
          x = x - 10
        if node == "BASEL":
          y = y - 7
          x = x + 17
        if node == "ORANGE":
          y = y + 1
          x = x - 23
        if node == "SYSTEMX":
          y = y + 6
          x = x - 12
        if node == "GOETTINGEN":
          y = y + 2
          x = x + 25
        if node == "PADUA":
          y = y -20 
          x = x + 20
        if node == "MINHO":
          y = y -15 
          x = x -10
        # SOUTH AMERICA
        if node == "UFPA":
          y = y 
          x = x 
        # ASIA
        if node == "UI":
          y = y 
          x = x 
        if node == "OSAKA":
          y = y -10
          x = x +9
        if node == "ANYANG":
          y = y +17
          x = x +4
        if node == "TONGJI":
          y = y -5
          x = x -6
        if node == "WASEDA":
          x = x + 6
          y = y +5
        if node == "KISTI":
          x = x-1
          y = y
        if node == "BUPT":
          y = y + 20
          x = x - 16
        if node == "SRRU":
          y = y - 5
          x = x - 21

        G.add_node(node)
        G.position[node] = (x,y)
        #print "Adding node: >", node, "< with position: ", x, ",", y
        print "Adding node: >", node, "< with position: ", G.position[node]

    for (n1,n2),l in edges_with_labels.iteritems():
        G.add_edge(n1,n2)
        print "Adding edge: >", n1, "< >", n2, "< ", l
        G.edge_labels[(n1,n2)] = l

    return G            

if __name__ == '__main__':
    import networkx as nx

    G=NDN_graph()

    for n in G.nodes():
       print "node n:", n

    print("digraph has %d nodes with %d edges"\
          %(nx.number_of_nodes(G),nx.number_of_edges(G)))
    graphLabel = "NDN Testbed ("
    graphLabel += str(nx.number_of_nodes(G))
    graphLabel += " nodes, "
    graphLabel += str(nx.number_of_edges(G))
    graphLabel += " links with NLSR costs) "
    print graphLabel
    try:
        print "about to plt.figure"
        plt.figure(figsize=(24,12))
        plt.title(graphLabel, fontsize=24)
        print "about to nx.draw"
        #nx.draw(G,G.position, with_labels=True)
        nx.draw(G,G.position, node_size=1000, with_labels=True)
        print "about to nx.draw_networkx_edge_labels"
        nx.draw_networkx_edge_labels(G,G.position, edge_labels=G.edge_labels)

        # scale the axes 

        # plt.xlim(-130,5)
        # plt.ylim(30,53)

        plt.xlim(-150,150)
        plt.ylim(-10,70)

        plt.savefig("full.png")
    except:
        print "exception: ", sys.exc_info()[0]
      
        #pass



