"""
    This program will run a query for every chip in the chip table. We will then 
    export its results to a csv file which MCL will use to cluster chips to 
    represent cats. makeMatrix will need to also use csv file
"""

import numpy as np 
import csv

def loadmatrix(hs): #maybe get rid of *args and **kwargs everywhere
        fileName = "Matrix.csv"
        file = open(fileName,'rb')
        data = csv.reader(file, delimiter =',')#might need to be "," instead of '\t'
        Matrix = [row for row in data]
        

        
        size = hs.get_num_chips()
	
	#walk the chip table and run a query for every chip and place results in Matrix
	for chip1 in hs.get_valid_cxs():
                ID = hs.cx2_cid(chip1)
                res_dict = {}
                res_dict = hs.query(ID)
                results = res_dict.cx2_score #i think cx2_score
                for col in range(size-1):
                        Matrix[ID-1][col] = (Matrix[ID-1][col] + results[col])
				
			
		
	return Matrix
	

	
def createFile(hs, Mat):
        size = hs.get_num_chips()
	file_obj = open("Matrix.csv", "w")
	for row in range(size):
		for col in range(size-1): 
			file_obj.write(str(Mat[row,col]) + ",")
		file_obj.write(str(Mat[row,size-1]) +"\n")
        #print "file created"

	
if __name__ == "__main__":
	Matrix = createMatrix(hs)
	createFile(hs, Matrix)
	
	
