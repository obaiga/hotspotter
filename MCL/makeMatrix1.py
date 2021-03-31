"""
    This program needs to be able to read in relationships between chips from the same image,
    images from the same set, and scores realting chips to eachother from recognition algorithm
"""
#not sure what all dependencies I need. Look at what is used in HotSPotter Api
import numpy as np
import csv
#import HotSpotterAPI as HSP
#import QueryResult as QR

secsThresh = 90
secsInDay = 86400

def createMatrix(hs): #not sure what all needs to be pased in
        fileName = "Matrix.csv"
        file = open(fileName,'rb')
        data = csv.reader(file, delimiter =',')
        Matrix = [row for row in data]
         
	size = hs.get_num_chips()
	
	#parse the chip table to determine matches
	for chip1 in hs.get_valid_cxs(): #iterate through chip table to gather all asscoitations
		chip1Name = hs.cx2_gname(chip1)
		for chip2 in hs.get_valid_cxs(): #for each chip check all other chips looking at their names
			chip2Name = hs.cx2_gname(chip2)
			if hs.cx2_cid(chip1) != hs.cx2_cid(chip2):
				if sameImage(chip1Name, chip2Name) == True:
					Matrix[hs.cx2_cid(chip1) -1][hs.cx2_cid(chip2) -1] = Matrix[hs.cx2_cid(chip1) -1][hs.cx2_cid(chip2) -1] + 100 
					Matrix[hs.cx2_cid(chip2) -1][hs.cx2_cid(chip1) -1] = Matrix[hs.cx2_cid(chip2) -1][hs.cx2_cid(chip1) -1] + 100
				elif sameSet(chip1Name, chip2Name) == True:
					Matrix[hs.cx2_cid(chip1) -1][hs.cx2_cid(chip2) -1] = Matrix[hs.cx2_cid(chip1) -1][hs.cx2_cid(chip2) -1] + 20
					Matrix[hs.cx2_cid(chip2) -1][hs.cx2_cid(chip1) -1] =Matrix[hs.cx2_cid(chip2) -1][hs.cx2_cid(chip1) -1] + 20
				
			
		
	return Matrix
	
def sameSet(chip1, chip2):

    #if in same location
    if getLoc(chip1) == getLoc(chip2):
        #if on same date
        if getDate(chip1) == getDate(chip2):
            #print "same location and date"

            #if close time
            if np.abs(getTime(chip1) - getTime(chip2)) <= secsThresh:
                #print "within secsThresh"
                return True
            else:
                #print "not within secsThresh"
                return False
        #elif one day apart but still less than 90 second:
        #    (getTime(chip1) <= secsThresh or
        #     getTime(chip1) > (secsInDay - secThresh)):
            #check dates still

        else:
            #print "not same date"
            return False
    else:
        #print "not same location"
        return False


def getLoc(chip):
    chipList = chip.split("__")
    loc = (chipList[0] + "__" + chipList[1] +"__"+chipList[2])
    return loc

def getDate(chip):
    date  = chip.split("__")[3]
    return date

#def getDateInDays(date):
    # figure out if stuff happened at end of a month (or year...)

def getTime(chip):
    chipList = chip.split("__")
    timeStr = chipList[4]

    timeStr = timeStr.split("(")[0]
    timeList = timeStr.split("-")

    time = int(timeList[0])*3600 + int(timeList[1])*60 + int(timeList[2])

    return time

	
def sameImage(chip1, chip2):

	if chip1 == chip2:
		return True
	else:
		return False

	
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
	
	
