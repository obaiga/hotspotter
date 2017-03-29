''' 
autochip.py
Author: Joshua Beard
Contributor: Taz Bales-Heisterkamp
Last Edited: 3/29/17
'''

EXTENSION = '.bmp'

''' Do autochipping '''
def doAutochipping(directoryToTemplates, exclFac = 1, stopCrit = .9, skip = 8, crit = [0,0,1], minSize = [1,1]):
	'''
	Driver for autochipping. Designed to be plug-n-play with HotSpotter GUI
	Author: Joshua Beard

	C: 2/27/17

	EDITS:

			
	NOTES:

	TODOS:

	'''
	''' Initialization '''
	print('[ac] doing autochipping')
	import os
	chippedImages = {};
	for fileName in os.listdir(directoryToTemplates):
		if fileName.endswith('EXTENSION'):
			# get template and autochip
			template = getTemplate(directoryToTemplates, fileName, EXTENSION)
			chips = autochip(template, exclFac, skip, stopCrit, crit, minSize)
			chippedImages[fileName[0:len(fileName)-len(EXTENSION)]] = chips
	return chippedImages
#/doAutochipping

''' autochip '''
def autochip(template, exclFac = 1, skip = 8, stopCrit = .75, crit = [0,0,1], minSize = [1,1]):
	'''
	Find largest rectangles within a template.
	Input:
		template
			<numpyEXTENSIONrix, dtype=bool>
			boolean region defining area of interest. MATLAB EXTENSION file, converted to numpyEXTENSIONrix 	
		exclFac
			<int>
			Measure of how much of each chip we ignore on consecutive searches
			0 corresponds with ignoring just the point at the center of mass
		skip
			<int>
			number of lines we skip when searching for largest rectangles
		stopCrit
			<number>
			stopping criteria for terminating autochipping
			If stopCrit < 1, corresponds to paercentage of template chipped
			If stopCrit > 1, corresponds with number of chips
			If stopCrit == 1, only pulls one chip
		crit
			<list, dtype>
			maximization criteria for finding largest rectangles
		minSize
			<list>
			minimum size of rectangle. 
			If minSize >= 1, corresponds to pixels
			If minSize < 1, corresponds to fraction of image size
			
	Output:
		Set of chips defined by (x, y, w, h) in raster order
		
	Author: Joshua Beard
	Contributor: Taz Bales-Heisterkamp
	C: 2/18/17

	
	EDITS:

			
	NOTES:
		Two ways to implement matrices in python:
			1. A = matrix([[1,2,3],[4,5,6]])
			2. A = matrix('1,2,3;4,5,6')
	
	TODOS:
		DONE	2/26/17	Bring everything into a loop to generalize
		2/26/17 get rid of COL, ROW, WIDTH, HEIGHT for memory and speed?
	
	'''
	
	''' Initialization '''
	#import numpy as np
	import math
	
	templateMod = template.copy()	# Get a template to mess around with
	chipBounds = [];				# Initialize chip bounds
	
	''' DEBUG 
	import pdb'''
	
	''' Work '''
	stopCrit = abs(stopCrit)	# Make sure we don't try to mess with negatives
	# If we're running until we capture a certain percentage
	if stopCrit < 1:	
		#pdb.set_trace()
		templateCoverage = template.sum()*1.0	# Use this for finding our stop criteria
		# run until we've covered X% of the template
		while templateMod.sum()/templateCoverage > (1-stopCrit):
			
			# Get the bounds of the next chip
			R = findLargestRects(templateMod, crit, minSize, skip)
			chipBounds.append([R['bounds']])	# Get first chip bounds as tuple, store in list
			
			# Get bounds for new rectangle
			col = R['bounds'][0]
			row = R['bounds'][1]
			width = R['bounds'][2]
			height = R['bounds'][3]
	
			# Get bounds for rectangle to remove from future searches
			if exclFac > 0:	# If we want to remove a rectangle
				rmWidth = int(math.floor(width/exclFac))
				rmHeight = int(math.floor(height/exclFac))
				if exclFac == 1:
					rmRow = row
					rmCol = col
				else:
					rmRow = int(row+(math.floor(rmHeight/2)))
					rmCol = int(col+(math.floor(rmWidth/2)))
			else:			# If we want to remove a point
				rmWidth = 0
				rmHeight = 0
				rmRow = int(row+math.floor(height/2))
				rmCol = int(col+math.floor(width/2))

			''' DB 
			pdb.set_trace()'''
			# Cut out some part of template for next search
			templateMod[rmRow:rmRow+rmHeight+1,rmCol:rmCol+rmWidth+1] = 0;
		# /while
	
	# If we're running until we get a certain number of chips
	elif stopCrit > 1:
		for q in range(0,int(round(stopCrit))):
			# Get the bounds of the next chip
			R = findLargestRects(templateMod, crit, minSize, skip)
			chipBounds.append([R['bounds']])	# Get first chip bounds as tuple, store in list
			
			# Get bounds for new rectangle
			col = R['bounds'][0]
			row = R['bounds'][1]
			width = R['bounds'][2]
			height = R['bounds'][3]
	
			# Get bounds for rectangle to remove from future searches
			if exclFac > 0:	# If we want to remove a rectangle
				rmWidth = int(math.floor(width/exclFac))
				rmHeight = int(math.floor(height/exclFac))
				if exclFac == 1:
					rmRow = row
					rmCol = col
				else:
					rmRow = int(row+(math.floor(rmHeight/2)))
					rmCol = int(col+(math.floor(rmWidth/2)))
			else:	# If we want to remove a point
				rmWidth = 0
				rmHeight = 0
				rmRow = int(row+math.floor(height/2))
				rmCol = int(col+math.floor(width/2))

			''' DB 
			pdb.set_trace()'''
			# Cut out some part of template for next search
			templateMod[rmRow:rmRow+rmHeight+1,rmCol:rmCol+rmWidth+1] = 0;
		# /for

	# If we're just grabbing one chip
	else:
		R = findLargestRects(templateMod, crit, minSize, skip)
		chipBounds.append([R['bounds']])	# Get first chip bounds as tuple, store in list


	return chipBounds
#/autochip

''' Helper function FINDLARGESTRECTS '''
def findLargestRects(template, crit=[0,0,1], minSize=[1,1], skip=1):
	'''
	RETURNS: 
		R = {'bounds':(col, row, maxW[row, col], maxH[row, col]), 'critVals': critVals, 'maxW':maxW, 'maxH':maxH}
	
	Find largest rectangles within a template.
	Input:
		template 	
			<numpyEXTENSIONrix, dtype=bool>
			boolean region defining area of interest.
		minSize 	
			<tuple>
			[height, width] defining minimum size of a rectangle.
			Default: [1,1]
		crit 		
			<tuple>
			optimization criteria to define how we weight a rectangle's dimensions. 
			maximizes like this: [height, width, area]
			Examples: 
				Let S[r_i,c_j] = side length of largest square w/ raster origin at (r_i,c_j)
				For each pixel in S, maximization criterion is proportional to:
					(crit[0]+crit[1]+crit[2]*S(r_i,c_j))*S[r_i,c_j],
				So:
				[1 1 0] maximizes perimeter
				[0 0 1] maximizes area
			Default: [0 0 1]
		skip
			<int>
			number of lines to skip when searching for the largest rectangle.
			Examples:
				skip == 1  -> search every line (slow execution, finds largest rectangles)
				skip == 16 -> search every 16th line (fast execution, doesn't always find largest rectangles)
			Default: 8
	Output:
		R
		critVals - value of crit calculated for each pixel
		maxH, maxW - for each pixel in template[nR,nC], return height and width of largest rectangle found there
		rectMask - mask of the largest rectangle in the image
		
	Author: Unknown (MATLAB)
	Translated from MATLAB to Python by Joshua Beard
	Contributors: Taz Bales-Heisterkamp
	1/28/17
	
	EDITS:
		1/28/17 started writing [jb]
		2/26/17 Need to use MATRIX.copy() to get copy by values, not reference!
			
	NOTES:
		Two ways to implement matrices in python:
			1. A = matrix([[1,2,3],[4,5,6]])
			2. A = matrix('1,2,3;4,5,6')
	
	TODOS:
		DONE 1/28/17 Return things
		DONE 2/24/17 Figure out why maxW and maxH return 349 as largest side length (this is the max for S)
		DONE 2/26/17 Currently only returns squares. I believe it has something to do with copying
			Turns out it was an indentation problem
			
		
	
	'''
	
	''' Initialization '''

	
	# Don't need to write nargin clause because of default variable definitions
	# Import necessary modules 
	import numpy as np
	import math
	#import scipy.io as sio
	'''Python Debug
	import pdb
	pdb.set_trace()'''

	
	# get height, width of template
	nR,nC = template.shape;

	# If minSize is less than one, use it as a percentage of size of template	
	if minSize[0] < 1:	# height
		minSize[0] = math.floor(minSize[0]*nR)
	if minSize[1] < 1:	# width
		minSize[1] = math.floor(minSize[1]*nC)
	
		
	# If we haven't run FINDLARGESTSQUARES yet, do it. 
	if template.max() - template.min() == 1:
		S = findLargestSquares(template)
	else: 	# o.t.w. just use our "template"
		S = template
	
	# Get longest square side
	n = S.max()
	
	# Duplicate template for messing around with it
	maxW = S.copy()
	maxH = S.copy()
	
	# Synthesize criteria-weighted values for each of the largest squares
	critVals = np.multiply((crit[0] + crit[1] + crit[2]*S), S)
	
	# Set actual minimum height and width, based on optional image scaling
	d = round((3*n)/4)
	# either min(input minimum, .75 * max square side)  or  1
	minHeight = max(min(minSize[0], d),1)
	minWidth = max(min(minSize[1], d),1) 
	
	''' Search for rectangles with width > height '''
	''' 
		Opportunity to optimize by looking at rows/columns before iterating through.
		If a row or a column does not have any foreground, don't even look at it.
	'''
	# Initialize a lookup list for referencing width for a given height
	# Create one extra so we don't have to worry about indexing issues (0 or 1)
	h2w = [0]*(n+1)
	
	# Iterate through every row, skipping every SKIP rows (0, nR-1)
	for r_i in range(0,nR,skip):
		# Reset List
		h2w = [0]*(n+1)
		
		# Go through all pixels in a column in reverse raster (generates raster)
		for c_j in range(nC-1,-1,-1):
			''' DEBUG when using template0.pickle
			if r_i == 2 and c_j == 1:
				pdb.set_trace()'''
			# Grab side length
			s = S[r_i,c_j]
			# If we're looking at the foreground (not background)
			if s > 0:
				# Initialize maximum crit-weighted values
				maxCrit = critVals[r_i,c_j]
				
				# Go through all possible height/width combos
				# Highest values are most likely to be best choices (for time)
				for height in range(s,0,-1):
					# Look up width that corresponds to given height
					#width = h2w[height-1]
					width = h2w[height]
					# Width is either that value(+1) or precalculated width
					width = max(width+1, s)
					# Update height-width lookup list with (maybe) new width
					#h2w[height-1] = width
					h2w[height] = width
					# Calculate crit-weighted value for this rectangle
					thisCrit = crit[0]*height + crit[1]*width + crit[2]*width*height
					# If thisCrit is larger than maxCrit...
					if thisCrit > maxCrit:
						''' DEBUG
						pdb.set_trace()'''
			        	# ...update maxCrit and max width and height matrices
						maxCrit = thisCrit
						maxW[r_i,c_j] = width
						maxH[r_i,c_j] = height
					# /if thisCrit
				# /for height
				
				# Update criteria values with maxCrit
				critVals[r_i,c_j] = maxCrit
			# /if s
			
			# Reset all other height-width lookup values
			'''Next line maybe work?'''
			h2w[s+1:] = [0]*len(h2w[s+1:]) # try this out
			#h2w[s:] = [0]*len(h2w[s:])
		# /for c_j	
	# /for r_i
	del h2w # Delete it for memory
	
	
	''' Search for rectangles with height > width '''
	''' 
	NOTE:
		Opportunity to optimize by looking at rows/columns before iterating through.
		If a row or a column does not have any foreground, don't even look at it.
	'''	
	
	# Initialize a lookup list for referencing width for a given height
	# Create one extra so we don't have to worry about indexing issues (0 or 1)
	w2h = [0]*(n+1)
		
	# Iterate through every column, skipping every SKIP columns (0, nC-1)
	for c_j in range(0,nC,skip):
		# Reset List
		w2h = [0]*(n+1)
		
		# Go through all pixels in a row in reverse raster (generates raster)
		for r_i in range(nR-1,-1,-1):
			''' DEBUG
			if maxW[r_i,c_j] >= 349:
				pdb.set_trace()'''
			# Grab side length
			s = S[r_i,c_j]
			# If we're looking at the foreground (not background)
			if s > 0:
				# Initialize maximum crit-weighted values
				maxCrit = critVals[r_i,c_j];
				
				# Go through all possible width-height combos
				# Highest values are most likely to be best choices (for time)
				for width in range(s,0,-1):
					# Look up height that corresponds to given width
					height = w2h[width]
					#height = w2h[width-1]
					# Heigth is either that value(+1) or precalculated height
					height = max(height+1, s)
					# Update width-height lookup list with (maybe) new width
					w2h[width] = height
					#w2h[width-1] = height
					# Calculate crit-weighted value for this rectangle
					thisCrit = crit[0]*height + crit[1]*width + crit[2]*width*height
					# If thisCrit is larger than maxCrit...
					if thisCrit > maxCrit:
						#pdb.set_trace()
						# ...update maxCrit and max width and height matrices
						maxCrit = thisCrit
						maxW[r_i,c_j]  = width
						maxH[r_i,c_j]  = height
					# /if thisCrit
				# /for height
				
				# Update criteria values with maxCrit
				critVals[r_i,c_j] = maxCrit
			# /if s
			
			# Reset all other height-width lookup values
			#w2h[s:] = [0]*len(w2h[s:])
			'''Maybe this?'''
			w2h[s+1:] = [0]*len(w2h[s+1:]) #try this out
		# /for c_j	
	# /for r_i
	#del w2h	# Delete it for memory
	
	
	# Make a copy for playing around with
	critVals_atLeastMin = critVals
	# If any values in tempCrit are less than minimum sizes, set them to 0
	'''
	2/23/17 21:57
	This line seems to be an issue:
		critVals_atLeastMin[(maxH < minHeight) or (maxW < minWidth)] = 0
	The error thrown when using it is:
		"ValueError: The truth value of an array with more than one element is ambiguous. Use a.any() or a.all()"
	2/23/17 22:36
		Seems to be working ok after playing around with it

	'''
	# If height or width is too small, don't even consider it
	critVals_atLeastMin[maxH < minHeight] = 0
	critVals_atLeastMin[maxW < minWidth] = 0
	
	# If there is at least one rectangle larger than min, get it
	if critVals_atLeastMin.any():
		pos = critVals_atLeastMin.argmax()
	else:	# otw, grab the largest one we can find.	
		pos = critVals.argmax()
	
	# Convert linear index to subscript
	row, col = np.unravel_index(pos, (nR, nC))

	
	'''pdb
	pdb.set_trace()'''
	
	# Initialize mask as zeros
	rectMask = np.zeros((nR,nC))	
	# Define largest rectangle with mask
	rectMask[row : (row+maxH[row,col]), col : (col+maxW[row,col])] = 1;
	# Added bounds output for integration
	R = {'bounds':(col, row, maxW[row, col], maxH[row, col]), 'critVals': critVals, 'maxW':maxW, 'maxH':maxH}
	
	return R
#/FindLargestRectangles

''' Helper function FINDLARGESTSQUARES '''	
def findLargestSquares(template):
	import numpy as np
	import math

	# get height, width of template
	nR,nC = template.shape;
	# Use boolean template to create a float matrix for tracking square sizes
	S = np.multiply(np.ones((nR, nC)), template)

	
	# Start with this pixel:
	'''
	0 0 0 0
	0 0 0 0 
	0 0 1 0 
	0 0 0 0 
	'''
	# Move left then up.
	for r_i in range(nR-2,-1,-1):
		for c_j in range(nC-2,-1,-1):
			if S[r_i,c_j]:
				a = S[r_i  , c_j+1]
				b = S[r_i+1, c_j  ]
				d = S[r_i+1, c_j+1]
				S[r_i,c_j] = min(a,b,d) + 1
			#/if S
		#/for c_j
	#/for r_i
	# Cast as an int for space and ability to index
	S = S.astype(int)	# Added 2/23/17
	return S
#/FindLargestSquares		
	
''' Helper function GETTEMPLATE '''
from scipy import misc
from os import sep
from numpy import asmatrix

def getTemplate(pathTo, templateFileName, ext = EXTENSION):
	if sep == '\\':					# Windows
		if pathTo.endswith('\\'):	# separator is present
			if templateFileName.endswith(ext):
				m = misc.imread(pathTo+templateFileName)
			else:			
				m = misc.imread(pathTo+templateFileName+ext)
		else:						# separator is absent
			if templateFileName.endswith(ext):
				m = misc.imread(pathTo+'\\'+templateFileName)
			else:				
				m = misc.imread(pathTo+'\\'+templateFileName+ext)
	else:							# Unix
		if pathTo.endswith('/'):	# separator is present
			if templateFileName.endswith(ext):
				m = misc.imread(pathTo+templateFileName)			
			else:
				m = misc.imread(pathTo+templateFileName+ext)
		else:						# separator is absent
			if templateFileName.endswith(ext):
				m = misc.imread(pathTo+'/'+templateFileName)				
			else:
				m = misc.imread(pathTo+'/'+templateFileName+ext)
	#/if os.sep
	
	return asmatrix(m)
#/ getTemplate

''' MAIN '''	
if __name__ == "__main__":
	import sys
	if len(sys.argv) == 2:
		chippedImages = doAutochipping(sys.argv[1])
		print chippedImages
	else:# len(sys.argv) == 3:
		template = getTemplate(sys.argv[1], sys.argv[2])
		C = autochip(template)
		print C


	
	
	
	
