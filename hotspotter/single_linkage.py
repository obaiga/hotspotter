from scipy.cluster.hierarchy import linkage, dendrogram
from matplotlib import pyplot as plt
import csv
import numpy

reader = csv.reader(open("scores.csv", "rb"), delimiter=",")
x = list(reader)
Z = numpy.array(x).astype("float")
#result1 = linkage(Z, 'single')
#dn = dendrogram(result1)
result2 = linkage(Z, 'complete')
dn = dendrogram(result2)
plt.show()
