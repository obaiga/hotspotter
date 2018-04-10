from scipy.cluster.hierarchy import linkage, dendrogram
from matplotlib import pyplot as plt
from os.path import join
import csv
import numpy

def do_clustering(hs, method= 'complete'):
    # Open scores.csv for reading
    # Then store score data in an array
    fpath = join(hs.dirs.internal_dir, 'scores.csv')
    reader = csv.reader(open(fpath, "rb"), delimiter=",")
    x = list(reader)
    nchips = len(x[1]) # Calculating number of chips
    Z = numpy.array(x).astype("float")

    # Perform single linkage clustering
    # 'result' is a nx4 array
    # index 0 & 1 are the two clusters that get combined
    # index 2 is the distance of the clusters combined
    # index 3 is the number of items in the newly formed cluster
    print("[hs.clustering]: Clustering with %s method" % method)
    result = linkage(Z, method)
    # Calculate a stopping point & print it
    stop_point = 0.7*max(result[:,2])
    print(result)
    print(stop_point)

    # Create a list to store clusters in
    clusters = list(list()) # Initialize clusters to a list of lists
    # Adjust clusters so that each chip starts in its own cluster
    for i in range(nchips):
        clusters.append([i])
    # Calculating clusters from linkage array
    # Output should be number of chips in each cluster
    #   as well as the chip IDs of each chip in the clusters
    nclusters = 1
    for merge in result:
        # Check if the distance between the two clusters being combined is less than
        #   the stopping stop_point
        if(merge[2] <= stop_point):
            # Get the cluster num of each cluster being combined
            cl1 = int(merge[0])
            cl2 = int(merge[1])
            # Form & display new cluster
            newCluster = clusters[cl1] + clusters[cl2]
            print(newCluster)
            # Add new cluster to the list
            clusters.append(newCluster)
            # Remove clusters that have been merged
            clusters[cl1] = []
            clusters[cl2] = []
        else:
            # Stop when stopping point has been reached
            break
    #print(clusters)
    #clusters.remove([])
    #print(clusters)
    return clusters

'''
# Display number of cats found
for cluster in clusters:
    if(len(cluster) > 0):
        print("Cat %(ncat)d had %(nchips)d chips: " %{'ncat': nclusters, 'nchips': len(cluster)})
        print(cluster)
        nclusters += 1
print("Found %d cats" % nclusters)
'''

def clusters_to_output(hs, clusters):
    #walk through dict print out all chips belonging to each cluster
    print("Clusters:")
    for cluster in clusters:
        print(cluster)


    """
    create a 2d array that walks through clusters dict
    and wrights the image the chip comes from and the cluster it
    belongs to
    """
    imageList = [[]]
    temp = 0
    k = 0
    for cluster in clusters:
        if(len(cluster) > 0):
            for chipID in cluster:
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
                temp =  temp + 1
                imageList.append([])    # Add null entry for future entries
            k = k + 1
    imageList.remove([])            # Remove null entries


    # Count and print number of clusters (cats)
    clusterCount = k #how many clusters or cats we have
    print ("clusterCount: " +str(clusterCount))

    #Here we are walking through the dict and creating a new one
    #Where we force the chip to belong to one cluster(the cluster with the lower number

    cid_dict = {}
    k = 0
    for cluster in clusters:
        if(len(cluster) > 0):
            for chipID in cluster:
                if (chipID+1) not in cid_dict.keys():
                    cid_dict[chipID+1] = "cat_"+str(k+1)
                else:
                    cid_dict[chipID+1] = cid_dict[chipID+1] +"/cat_"+str(k+1)
            k = k + 1

    for k,v in cid_dict.items():
        print('{}, {}'.format(k,v))
    print("Thats the list")

    for chipobj in hs.get_valid_cxs():
        chipID = hs.cx2_cid(chipobj)
        chipname = cid_dict[chipID]
        #print chipname
        #chipname = "Cat_"+str(cid_dict[chipID])
        #chipname = "cat1_cat2"
        hs.change_name(chipobj, chipname)

    return imageList, clusterCount
