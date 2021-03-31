"""
    This program will run a query for every chip in the chip table. We will then 
    export its results to a csv file which MCL will use to cluster chips to 
    represent cats. makeMatrix will need to also use csv file
"""

import numpy as np 
import csv

SAME_IMAGE_WEIGHT = .9
SAME_SET_WEIGHT =  .9
SAME_CHIP_WEIGHT = 1
SAME_SET_WEIGHT_MIN = 0.25

def createMatrix(hs): #maybe get rid of *args and **kwargs everywhere
    numChips = hs.get_num_chips()
    scoreMatrix = np.zeros((numChips,numChips))        
    for i in hs.get_valid_cxs(): #iterate through all chips
        # Get chip info
        chip1 = hs.cx2_cid(i)               
        chip1_imageName = hs.cx2_gname(i)   
        
        # Run query and get scores
        results = hs.query(chip1)          
        results = results.cx2_score        
        
        # Normalize scores from [0,1]
        maxScore = max(results)            
        if not maxScore: # If no positive matches, don't divide by zero
            results = [0]*len(results)
        else:
            results = [thisScore/maxScore for thisScore in results]
            
        # Adjust scores for chips from same set, then populate matrix
        for j in hs.get_valid_cxs():
         
            # Get chip info
            chip2 = hs.cx2_cid(j)
            chip2_imageName = hs.cx2_gname(j)
            
            # For all unique chip pairs
            if chip1!=chip2:
            
                # If chips are from the same image
                if chip1_imageName == chip2_imageName:
                    scoreMatrix[i][j] = sameImageScore(results[j])
                    scoreMatrix[j][i] = sameImageScore(results[j])
                # If chips are from the same set and this is the first query on this pair
                elif sameSet(chip1_imageName, chip2_imageName) and scoreMatrix[i][j] == 0.0:
                    scoreMatrix[i][j] = sameSetScore(results[j])
                    scoreMatrix[j][i] = sameSetScore(results[j])

                # If chips are from same set and this is second query on this pair
                elif sameSet(chip1_imageName, chip2_imageName) and scoreMatrix[i][j] != 0.0:
                    scoreMatrix[i][j] = sameSetScore((scoreMatrix[i][j] + results[j])/2)
                    scoreMatrix[j][i] = sameSetScore((scoreMatrix[i][j] + results[j])/2)
                
                # If not from same set, and first query
                elif not sameSet(chip1_imageName, chip2_imageName) and scoreMatrix[i][j] == 0.0:
                    scoreMatrix[i][j] = results[j] 
                    scoreMatrix[j][i] = results[j]
                
                # If not from same set and second query
                else:
                    scoreMatrix[i][j] = (scoreMatrix[i][j] + results[j])/2
                    scoreMatrix[j][j] = (scoreMatrix[j][i] + results[j])/2

            # If they are the same chip
            else:
                scoreMatrix[i][j] = SAME_CHIP_WEIGHT
                scoreMatrix[j][i] = SAME_CHIP_WEIGHT
    return scoreMatrix
    
def sameImageScore(newScore):
    return SAME_IMAGE_WEIGHT

def sameSetScore(score):
    return max((score + SAME_SET_WEIGHT)/2, SAME_SET_WEIGHT_MIN)


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
    
    
