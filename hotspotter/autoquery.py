''' Migrate all autoquery functionality here '''
import numpy as np 
import csv

SAME_IMAGE_WEIGHT = .9
SAME_SET_WEIGHT =  .9
SAME_SET_WEIGHT_MIN = 0.25
DEFAULT_TIME_DELTA_MAX = 90

#import MCL as mcl
# Initialize at zero

def makeScoreMat(hs):
    # Get parameters
    params = hs.prefs.autoquery_cfg
    
    numChips = hs.get_num_chips()
    scoreMat = np.zeros((numChips, numChips))
    print("[aq] beginning autoquery")

    ''' Make score matrix with query results '''
    for i in hs.get_valid_cxs():    # For each chip
        
        cid1 = hs.cx2_cid(i)        # Get chip id
        c1_gname = hs.cx2_gname(i)  # Get image name
        
        results = hs.query(i)                       # Query this chip
        if isinstance(results, str):                # If query returned no keypoints
            results = [0]*len(hs.get_valid_cxs())   # Set matches to 0
        else:                                       # Valid query
            results = results.cx2_score             # Toss everything except the score
        
        # Normalize scores
        maxScore = max(results)
        if not maxScore:                # Don't divide by 0
            results = [0]*len(results)
        else:                           # Normalize
            results = [score/maxScore for score in results]
        
        for j in hs.get_valid_cxs():
            
            cid2 = hs.cx2_cid(j)
            c2_gname = hs.cx2_gname(j)
            
            # If same chip
            if cid1==cid2:
                print(cid1),
                print(" == "),
                print(cid2)
                scoreMat[i][j] = params.self_loop_weight
                scoreMat[j][i] = params.self_loop_weight

            # Unique chips
            else:
                # If chips are from the same image
                if c1_gname == c2_gname:
                    scoreMat[i][j] = sameImageScore(results[j], params)
                    scoreMat[j][i] = sameImageScore(results[j], params)
                # If chips are from the same set and this is the first query on this pair
                elif sameSet(c1_gname, c2_gname, params.maximum_time_delta) and scoreMat[i][j] == 0.0:
                    scoreMat[i][j] = sameSetScore(results[j], params)
                    scoreMat[j][i] = sameSetScore(results[j], params)

                # If chips are from same set and this is second query on this pair
                elif sameSet(c1_gname, c2_gname, params.maximum_time_delta) and scoreMat[i][j] != 0.0:
                    scoreMat[i][j] = sameSetScore((scoreMat[i][j] + results[j])/2, params)
                    scoreMat[j][i] = sameSetScore((scoreMat[i][j] + results[j])/2, params)
                
                # If not from same set, and first query
                elif not sameSet(c1_gname, c2_gname, params.maximum_time_delta) and scoreMat[i][j] == 0.0:
                    scoreMat[i][j] = results[j] 
                    scoreMat[j][i] = results[j]
                
                # If not from same set and second query
                else:
                    scoreMat[i][j] = (scoreMat[i][j] + results[j])/2
                    scoreMat[j][j] = (scoreMat[j][i] + results[j])/2
    print("[aq] autoquery done")
    return scoreMat
    
def sameImageScore(score, params):
    newScore = params.same_image_score
    return newScore

def sameSetScore(score, params):
    newScore = max((score + params.same_set_boost)/2, params.same_set_boost)
    return newScore

''' Everything below is 100% Noah '''
def sameSet(chip1, chip2, dt=DEFAULT_TIME_DELTA_MAX):
    
    #if in same location
    if getLoc(chip1) == getLoc(chip2):
        #if on same date
        if getDate(chip1) == getDate(chip2):
            #print "same location and date"
            
            #if close time
            if np.abs(getTime(chip1) - getTime(chip2)) <= dt:
                    #print "within TIME_DELTA_MAX"
                    return True
            else:
                    #print "not within TIME_DELTA_MAX"
                    return False
            #elif one day apart but still less than 90 second:
            #    (getTime(chip1) <= TIME_DELTA_MAX or
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


