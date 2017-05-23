#!/usr/bin/env python

import sys
import numpy as np
import time
from optparse import OptionParser
import logging

def normalize(A):
    column_sums = A.sum(axis=0)
    new_matrix = A / column_sums[np.newaxis, :]
    return new_matrix

def inflate(A, inflate_factor):
    return normalize(np.power(A, inflate_factor))

def expand(A, expand_factor):
    return np.linalg.matrix_power(A, expand_factor)

def add_diag(A, mult_factor):
    return A + mult_factor * np.identity(A.shape[0])

def get_clusters(A):
    clusters = []
    for i, r in enumerate((A>0).tolist()):
        if r[i]:
            clusters.append(A[i,:]>0)

    clust_map  ={}
    for cn , c in enumerate(clusters):
        for x in  [ i for i, x in enumerate(c) if x ]:
            clust_map[cn] = clust_map.get(cn, [])  + [x]
    return clust_map

def draw(G, A, cluster_map):
    import networkx as nx
    import matplotlib.pyplot as plt

    clust_map = {}
    for k, vals in cluster_map.items():
        for v in vals:
            clust_map[v] = k

    colors = []
    for i in range(len(G.nodes())):
        colors.append(clust_map.get(i, 100))

    pos = nx.spring_layout(G)

    from matplotlib.pylab import matshow, show, cm
    plt.figure(2)
    nx.draw_networkx_nodes(G, pos,node_size = 200, node_color =colors , cmap=plt.cm.Blues )
    nx.draw_networkx_edges(G,pos, alpha=0.5)
    matshow(A, fignum=1, cmap=cm.gray)
    plt.show()
    show()


def stop(M, i):

    if i%5==4:
        m = np.max( M**2 - M) - np.min( M**2 - M)
        if m==0:
            logging.info("Stop at iteration %s" % i)
            return True

    return False


def mcl(M, expand_factor = 2, inflate_factor = 2, max_loop = 10 , mult_factor = 1):
    M = add_diag(M, mult_factor)
    M = normalize(M)

    for i in range(max_loop):
        logging.info("loop %s" % i)
        M = inflate(M, inflate_factor)
        M = expand(M, expand_factor)
        if stop(M, i): break

    clusters = get_clusters(M)
    return M, clusters

def networkx_mcl(G, expand_factor = 2, inflate_factor = 2, max_loop = 10 , mult_factor = 1):
    import networkx as nx
    A = nx.adjacency_matrix(G)
    return mcl(np.array(A.todense()), expand_factor, inflate_factor, max_loop, mult_factor)

def print_info(options):
    print("-" * 60)
    print("MARKOV CLUSTERING:")
    print("-" * 60)
    print("  expand_factor: %s" % options.expand_factor)
    print("  inflate_factor: %s" % options.inflate_factor)
    print("  mult factor: %s" % options.mult_factor)
    print("  max loops: %s\n" % options.max_loop)

def get_options():
    usage = "usage: %prog [options] <input_matrix>"
    parser = OptionParser(usage)
    parser.add_option("-e", "--expand_factor",
                      dest="expand_factor",
                      default=2,
                      type=int,
                      help="expand factor (default: %default)")
    parser.add_option("-i", "--inflate_factor",
                      dest="inflate_factor",
                      default=3,# was 2
                      type=float,
                      help="inflate factor (default: %default)")
    parser.add_option("-m", "--mult_factor",
                      dest="mult_factor",
                      default=3,#was 2
                      type=float,
                      help="multiply factor (default: %default)")
    parser.add_option("-l", "--max_loops",
                      dest="max_loop",
                      default=60,
                      type=int,
                      help="max loops (default: %default)")
    parser.add_option("-o", "--output", metavar="FILE", 
                      help="output (default: stdout)")

    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=True,
                      help="verbose (default: %default)")
    parser.add_option("-d", "--draw-graph",
                      action="store_true", dest="draw", default=False,
                      help="show graph with networkx (default: %default)")
    

    (options, args) = parser.parse_args()

    try:
        filename = args[0]
    except:
        raise Exception('input', 'missing input filename')


    return options, filename

def get_graph(csv_filepath, csv_name='scores.csv'):
    from os.path import join
    import networkx as nx
    csv_filename = join(csv_filepath, csv_name)
    M = []
    for r in open(csv_filename):
        r = r.strip().split(",")
        M.append(list(map(lambda x: float(x.strip()), r)))

    G = nx.from_numpy_matrix(np.matrix(M))
    return np.array(M), G

def clusters_to_output(hs, clusters):
    #walk through dict print out all chips belonging to each cluster
    print("Clusters:")
    for k, v in clusters.items():
        print('{}, {}'.format(k, v))

        
    """
    create a 2d array that walks through clusters dict
    and wrights the image the chip comes from and the cluster it 
    belongs to 
    """
    imageList = [[]]
    temp = 0
    
    for k,v in clusters.items():
        for chipID in v:
            imageList[temp].append(str(k+1))                # Cat name
            #imageList[temp].append("cat"+str(k+1))
            imageList[temp].append(hs.cx2_gname(chipID))    # Image Name
            #image = hs.cx2_gname(chipID)
            imageSplit = hs.cx2_gname(chipID).split("__")   # Parse image info
            imageSplit[len(imageSplit)-1] = imageSplit[len(imageSplit)-1].split('.')[0] # Cut image type
            #import pdb; pdb.set_trace()
            #imageSplit = image.split("__")
            for i in range(len(imageSplit)-1):          # For all parsed fields (except time)
                imageList[temp].append(imageSplit[i])   # Record info
            imageTime = imageSplit[len(imageSplit)-1].split("(")        # Parse out set numeral (from PantheraR)
            imageList[temp].append(imageTime[0])        # Add time
            temp =  temp +1
            imageList.append([])    # Add null entry for future entries
    imageList.remove([])            # Remove null entries                               
    
    
    # Count and print number of clusters (cats)
    clusterCount = len(clusters) #how many clusters or cats we have
    print ("clusterCount: " +str(clusterCount))
                                   
    #Here we are walking through the dict and creating a new one
    #Where we force the chip to belong to one cluster(the cluster with the lower number
    
    cid_dict = {}
    for k,v in clusters.items():
        for chipID in v:
            if (chipID+1) not in cid_dict.keys():
                cid_dict[chipID+1] = "cat_"+str(k+1)
            else:
                cid_dict[chipID+1] = cid_dict[chipID+1] +"/cat_"+str(k+1)
    for k,v in cid_dict.items():
        print('{}, {}'.format(k,v))
    print("Thats the list")
    """
    
    chip_gname = hs.cx2_gname(0)
    cat1name = 0
    cat2name = 0
    cat3name = 0
    cat1count = 0
    cat2count = 0
    cat3count = 0
    maxChips = hs.get_num_chips() -1
    for i in hs.get_valid_cxs():
        chip1_gname = hs.cx2_gname(i)
        #print ("start case1")
        if(i == 0):
            cat1name = cid_dict[1]
            print ("start case")
        if(chip1_gname != chip_gname):
            print ("new image")
            if (cat1count >=cat2count) and (cat1count >= cat3count):
                largest = cat1name
            elif(cat2count >=cat1count) and (cat2count >=cat3count):
                largest = cat1name
            else:
                if cat3name == 0:
                    largest = cat1name
                else:
                    largest = cat3name
            totalcount = cat1count+cat2count+cat3count
            for chipname in range((i+1-totalcount),i+1):
                cid_dict[chipname] = largest                  
            cat1name = cid_dict[i+1]
            cat2name = 0
            cat3name = 0
            cat1count = 1
            cat2count = 0
            cat3count = 0
            chip_gname = hs.cx2_gname(i)
    
        else:
            if cid_dict[i+1] == cat1name:
                
                cat1count = (cat1count +1)
            elif cat2name == 0:
                cat2name = cid_dict[i+1]
                cat2count = (cat2count + 1)
            elif cid_dict[i+1] == cat2name:
                cat2count = (cat2count +1)
            elif cat3name == 0:
                cat3name = cid_dict[i+1]
                cat3count = (cat3count + 1)
            elif cid_dict[i+1] == cat3name:
                cat3count = (cat3count +1)
            else:
                print("more then three cats in 1 image")
                cat1count = cat1count +1

    for k,v in cid_dict.items():
        print('{}, {}'.format(k,v))
    """                          
    
    for chipobj in hs.get_valid_cxs():
        chipID = hs.cx2_cid(chipobj)
        chipname = cid_dict[chipID]
        #print chipname
        #chipname = "Cat_"+str(cid_dict[chipID])
        #chipname = "cat1_cat2"
        hs.change_name(chipobj, chipname)
    
    return imageList, clusterCount


if __name__ == '__main__':

    options, filename = get_options()
    print_info(options)
    M, G = get_graph(filename)

    print(" number of nodes: %s\n" % M.shape[0])

    print("{}: {}".format(time.time(), "evaluating clusters..."))
    M, clusters = networkx_mcl(G, expand_factor = options.expand_factor,
                               inflate_factor = options.inflate_factor,
                               max_loop = options.max_loop,
                               mult_factor = options.mult_factor)
    print("{}: {}".format(time.time(), "done\n"))

    clusters_to_output(clusters, options)

    if options.draw:
        print("{}: {}".format(time.time(), "drawing..."))
        draw(G, M, clusters)
        print("{}: {}".format(time.time(), "done"))
