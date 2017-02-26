# driver_findLargestRects.py
'''
This is a driver for findLargestRects.py

Author: Joshua Beard
C: 2/10/17
E: 2/24/17
	2/23/17 
		Got importing working alright.
		Initial tests result in bounds = (670, 223, 349, 349), which is curious specifically the width and height of the largest rectangle are both supposedly 349, which seems unlikely. I need to go back to MATLAB to verify using this template.
		It seems the maxW and maxH matrices do not get updated with new widths and heights, as 349 is the largest square side returned from findLargestSquares

'''
#import numpy as np
#import math
import scipy.io as sio
import sys

''' Parameters '''
# BEWARE the hardcoded path
hsPath = '/home/joshuabeard/Documents/hotspotter'
testPath = '/home/joshuabeard/Documents/hotspotter/autochip/test'
templateName = 'template1.mat'
#template = pickle.load(open("template0.pickle", "rb")) # If using simple template for testing

''' More imports after defining parameters '''
sys.path.append(hsPath)
sys.path.append(testPath)
import autochip.findLargestRects as flr


''' Initialization '''
matContents = sio.loadmat(testPath + '/' + templateName)	# Load up the template generated in ML
template = matContents['template'] 		# get the actual template

largestRect = flr.findLargestRects(template)

print largestRect
