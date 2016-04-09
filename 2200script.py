import csv
import networkx as nx
import operator
import copy

MDG = nx.MultiDiGraph()
with open('2200data.csv', 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
        name = row[0]
        univ = row[1]
        bachelors = row[5]
        masters = row[6]
        if bachelors != '':
            MDG.add_weighted_edges_from([(univ, bachelors, 0.5)])
        if masters != '':
            MDG.add_weighted_edges_from([(univ, masters, 1.0)])
    # no normalization yet
    in_deg = MDG.in_degree(weight='weight')
    #sorted_MDG = sorted(in_deg.items(), key=operator.itemgetter(1))
    #print sorted_MDG
    

def get_share(MDG, source, dest):
    try:
        edge_info = MDG[source][dest]
    except:
        return 0
    edge_wt = 0
    for key, value in edge_info.iteritems():
        edge_wt += value['weight']
    in_deg = MDG.in_degree(weight='weight')[dest]
    return edge_wt * 1.0 / in_deg
  
pr = {}      
for node in MDG.nodes():
    pr[node] = 1.0/len(MDG.nodes())
new_pr = {}
num_iters = 20
alpha = 0.15
for iters in range(num_iters):
    print iters
    for dest in pr:
        new_rank = alpha
        for source, rank in pr.iteritems():
            new_rank += (1 - alpha) * rank * get_share(MDG, source, dest)
        new_pr[dest] = new_rank
    pr = copy.copy(new_pr)
    
sorted_pr = sorted(in_deg.items(), key=operator.itemgetter(1))
print sorted_pr
        