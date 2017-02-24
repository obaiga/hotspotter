''' 
findLargestRects.py

Original Author: Unknown
Translated from MATLAB to Python by Joshua Beard
C: 1/28/17
E: 2/2/17
'''


if __name__ == "__main__":
	import sys
	findLargestRects('~/Documents/hotspotter/autochip/test/'+ sys.argv[1])
	


def findLargestRects(template, crit=[0,0,1], minSize=[1,1], skip=8):
	'''
	Find largest rectangles within a template.
	Input:
		template 	
			<numpy.matrix, dtype=bool>
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
				Let S[r,c] = side length of largest square w/ raster origin at (r,c)
				For each pixel in S, maximization criterion is proportional to:
					(crit[0]+crit[1]+crit[2]*S(r,c))*S[r,c],
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
		critVals - value of crit calculated for each pixel
		maxH, maxW - for each pixel in template[nR,nC], return height and width of largest rectangle found there
		rectMask - mask of the largest rectangle in the image
		
	Author: Unknown (MATLAB)
	Translated from MATLAB to Python by Joshua Beard
	Contributors: Joshua Beard and Taz Bales-Heisterkamp
	C: 1/28/17
	E: 1/28/17
	
	EDITS:
		1/28/17 started writing [jb]
			
	NOTES:
		Two ways to implement matrices in python:
			1. A = matrix([[1,2,3],[4,5,6]])
			2. A = matrix('1,2,3;4,5,6')
	
	TODOS:
		1/28/17 Return things
	
	'''
	
	''' Initialization '''

	
	# Don't need to write nargin clause because of default variable definitions
	# Import necessary modules 
	import numpy as np
	import math
	'''Pyython Debug'''
	import pdb
	#import scipy.io as sio
	
	# get height, width of template
	nR,nC = template.shape;

	# If minSize is less than one, use it as a percentage of size of template	
	if minSize[0] < 1:	# height
		minSize[0] = math.floor(minSize[0]*nR)
	if minSize[1] < 1:	# height
		minSize[1] = math.floor(minSize[1]*nC)
	
		
	# If we haven't run FINDLARGESTSQUARES yet, do it. 
	if template.max() - template.min() == 1:
		S = findLargestSquares(template)
	else: 	# o.t.w. just use our "template"
		S = template
	
	# Get longest square side
	n = S.max()
	
	# Duplicate template for messing around with it
	maxW = S
	maxH = S
	
	# Synthesize criteria-weighted values for each of the largest squares
	critVals = np.multiply((crit[0] + crit[1] + crit[2]*S), S)
	
	# Set actual minimum height and width, based on optional image scaling
	d = round((3*n)/4)
	# either min(input minimum, .75 * max square side)  or  1
	minHeight = max(min(minSize[0], d),1)
	minWidth = max(min(minSize[1], d),1) 
	
	''' Search for rectangles with width > height '''
	''' 
	NOTE:
		Opportunity to optimize by looking at rows/columns before iterating through.
		If a row or a column does not have any foreground, don't even look at it.
	'''
	# Initialize a lookup list for referencing width for a given height
	# Create one extra so we don't have to worry about indexing issues (0 or 1)
	h_w = [0]*(n+1)
	
	# Iterate through every row, skipping every SKIP rows (0, nR-1)
	for r in range(0,nR,skip):
		# Reset List
		h_w = [0]*(n+1)
		
		# Go through all pixels in a column in reverse raster (generates raster)
		for c in range(nC-1,-1,-1):
			# Grab side length
			s = S[r,c]
			# If we're looking at the foreground (not background)
			if s > 0:
				# Initialize maximum crit-weighted values
				maxCrit = critVals[r,c];
				
				# Go through all possible height/width combos
				# Highest values are most likely to be best choices (for time)
				for height in range(s,0,-1):
					# Look up width that corresponds to given height
					width = h_w[height]
					# Width is either that value(+1) or precalculated width
					width = max(width+1, s)
					# Update height-width lookup list with (maybe) new width
					h_w[height] = width
					# Calculate crit-weighted value for this rectangle
					thisCrit = crit[0]*height + crit[1]*width + crit[2]*width*height
					# If thisCrit is larger than maxCrit...
			        if thisCrit > maxCrit:
			        	# ...update maxCrit and max width and height matrices
						maxCrit = thisCrit
						maxW[r,c] = width
						maxH[r,c] = height
					# /if thisCrit
				# /for height
				
				# Update criteria values with maxCrit
				critVals[r,c] = maxCrit
			# /if s
			
			# Reset all other height-width lookup values
			h_w[s:] = [0]*len(h_w[s:])
		# /for c	
	# /for r
	del h_w # Delete it for memory
	
	
	''' Search for rectangles with height > width '''
	''' 
	NOTE:
		Opportunity to optimize by looking at rows/columns before iterating through.
		If a row or a column does not have any foreground, don't even look at it.
	'''	
	
	# Initialize a lookup list for referencing width for a given height
	# Create one extra so we don't have to worry about indexing issues (0 or 1)
	w_h = [0]*(n+1)
		
	# Iterate through every column, skipping every SKIP columns (0, nC-1)
	for c in range(0,nC,skip):
		# Reset List
		w_h = [0]*(n+1)
		
		# Go through all pixels in a row in reverse raster (generates raster)
		for c in range(nR-1,-1,-1):
			# Grab side length
			s = S[r,c]
			# If we're looking at the foreground (not background)
			if s > 0:
				# Initialize maximum crit-weighted values
				maxCrit = critVals[r,c];
				
				# Go through all possible width-height combos
				# Highest values are most likely to be best choices (for time)
				for width in range(s,0,-1):
					# Look up height that corresponds to given width
					height = w_h[width]
					# Heigth is either that value(+1) or precalculated height
					height = max(height+1, s)
					# Update width-height lookup list with (maybe) new width
					w_h[width] = height
					# Calculate crit-weighted value for this rectangle
					thisCrit = crit[0]*height + crit[1]*width + crit[2]*width*height
					# If thisCrit is larger than maxCrit...
			        if thisCrit > maxCrit:
			        	# ...update maxCrit and max width and height matrices
						maxCrit = thisCrit
						maxW[r,c]  = width
						maxH[r,c]  = height
					# /if thisCrit
				# /for height
				
				# Update criteria values with maxCrit
				critVals[r,c] = maxCrit
			# /if s
			
			# Reset all other height-width lookup values
			w_h[s:] = [0]*len(w_h[s:])
		# /for c	
	# /for r
	del w_h	# Delete it for memory
	
	'''pdb'''
	#pdb.set_trace()
	
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

	# Initialize mask as zeros
	rectMask = np.zeros((nR,nC))	
	# Define largest rectangle with mask
	rectMask[row : (row+maxH[row,col]), col : (col+maxW[row,col])] = 1;
	# Added bounds output for integration
	return('bounds', (col, row, maxW[row, col], maxH[row, col]),'critVals', critVals, 'maxH', maxH, 'maxW', maxW, 'rectMask', rectMask)
#/FindLargestRectangles


''' Definition helper function FINDLARGESTSQUARES '''	
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
	for r in range(nR-2,-1,-1):
		for c in range(nC-2,-1,-1):
			if S[r,c]:
				a = S[r  , c+1]
				b = S[r+1, c  ]
				d = S[r+1, c+1]
				S[r,c] = min(a,b,d) + 1
			#/if S
		#/for c
	#/for r
	# Cast as an int for space and ability to index
	S = S.astype(int)	# Added 2/23/17
	return S
#/FindLargestSquares		
	
	
	
	
	
	
	
	
