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
    #print "process_nodes(): top of while"
    words = line.split()
    #print "words[0]: ", words[0]
    #print "process_nodes(): checking shortname"
    if words[0] == "\"shortname\":":
      #words = line.split(':')
      #print "found line with shortname"
      shortNameWords = words[1].split(',')
      foundShortName = True
      shortName = shortNameWords[0][1:len(shortNameWords[0])-1]
      #print "shortName: ", shortName
    #print "process_nodes(): checking position"
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
    #print "process_nodes(): checking founds"
    if foundShortName == True and foundPosition == True :
      if shortName.startswith( 'AWS-' ) == False:
        nodes_with_positions[shortName] = (x,y)
        #print "processed node: ", shortName, "with position: x: ", x, "y: ", y
      foundShortName = False
      foundPosition = False
    line = f.readline()
    #print "line: >", line, "<"
  #print "end process_nodes():"

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
    #print "back from  process_edges():"
    process_nodes()
    #print "back from  process_nodes():"

    G=nx.Graph()
    G.position={}
    G.edge_labels = {}

    for n,(y,x) in nodes_with_positions.iteritems():
        node = n
        # Adjust x position
        if x > 100:
          x = x - 140
        else:
          if x > -10 and x < 20:
            x = x -50
        if node == "TONGJI":
          y = y + 0.25
          x = x + 2
        if node == "WASEDA":
          x = x +2
        if node == "AVEIRO":
          x = x -2
          y = y -1.0
        if node == "GIST":
          x = x -3
          y = y +0.7
        if node == "KISTI":
          x = x +2
          y = y -2
        if node == "LIP6":
          x = x -10
        if node == "ORANGE":
          y = y -1
        if node == "UA":
          y = y +0.5
        if node == "CAIDA":
          x = x -5
        if node == "UCLACS":
          y = y +1.5
          x = x + 1.5
        if node == "UCLA":
          y = y +1
          x = x +2
        if node == "REMAP":
          y = y +1
          x = x +1
        if node == "UCI":
          x = x -1
        #if node == "VERISIGN":
        #  y = y -1
        #if node == "NTNU":
        #  y = y - 12.6
        #  x = x - 5.0
        if node == "MML1":
          x = x - 60
        if node == "MML2":
          x = x - 60
        if node == "COPELABS":
          y = y - 0.5
          x = x + 4
        if node == "UI":
          y = y + 36.7
          x = x + 23
        if node == "GOETTINGEN":
          y = y -2
          x = x + 8
        if node == "OSAKA":
          y = y - 1
          x = x + 7
        if node == "MINHO":
          y = y - 0.5
          x = x - 3
        if node == "SAVI":
          y = y + 1.0
          x = x - 3
        #if node == "NIST":
        #  x = x + 8
        #  y = y - 0.25
        if node == "MSU":
          y = y + 16.25
          x = x - 4
        if node == "MUMBAI_AWS":
          y = y + 16
          x = x - 120
        if node == "UUM":
          y = y + 26.7
          x = x + 15
        if node == "SRRU":
          y = y + 16
        if node == "UASLP":
          y = y + 8.5
          #x = x - 3
        if node == "UFBA":
          y = y + 36.5
          x = x - 3
        #if node == "AAU":
        #  x = x - 1
        #  y = y + 1.3
        if node == "UNIVH2C":
          x = x - 2.5
          y = y + 1.3
        if node == "PADUA":
          x = x + 2
        if node == "BERN":
          y = y - 1
        if node == "TNO":
          y = y + 0.4
          x = x - 5.0
        if node == "PKUSZ":
          y = y + 18
          x = x - 0
        if node == "CNIC":
          y = y + 0
          x = x - 2
        if node == "QUB":
          y = y - 3
        #if node == "PKU":
        #  x = x -3
        G.add_node(node)
        G.position[node] = (x,y)
        #print "Adding node: >", node, "< with position: ", x, ",", y
        #print "Adding node: >", node, "< with position: ", G.position[node]

    #print "about to add edges"
    for (n1,n2),l in edges_with_labels.iteritems():
        G.add_edge(n1,n2)
        #print "Adding edge: >", n1, "< >", n2, "< ", l
        G.edge_labels[(n1,n2)] = l

    #print "done adding edges"
    return G            

if __name__ == '__main__':
    import networkx as nx

    G=NDN_graph()
    #print "after NDN_graph"

    #for n in G.nodes():
    #   print "node n:", n

    #print("digraph has %d nodes with %d edges"\
    #      %(nx.number_of_nodes(G),nx.number_of_edges(G)))
    graphLabel = "NDN Testbed ("
    #graphLabel += str(nx.number_of_nodes(G) - 13)
    graphLabel += str(nx.number_of_nodes(G) )
    graphLabel += " nodes, "
    graphLabel += str(nx.number_of_edges(G))
    graphLabel += " links with NLSR costs) "
    print graphLabel
    try:
        #print "about to plt.figure"
        plt.figure(figsize=(28,14))
        plt.title(graphLabel, fontsize=24)
        print "about to nx.draw"
        #nx.draw(G,G.position, with_labels=True)
        nx.draw_networkx(G,G.position, node_size=1000, with_labels=True)
        print "about to nx.draw_networkx_edge_labels"
        nx.draw_networkx_edge_labels(G,G.position, edge_labels=G.edge_labels)

        # scale the axes 
        plt.xlim(-130,5)
        #plt.ylim(-90,90)
        plt.ylim(30,53)

        plt.xticks([])
        plt.yticks([])

        plt.savefig("topology.png")
    except:
        print "exception: ", sys.exc_info()[0]
      
        #pass



