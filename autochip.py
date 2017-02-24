def autochip(template):
	'''
	Find largest rectangles within a template.
	Input:
		template
			MATLAB .mat file, converted to numpy.matrix 	
			<numpy.matrix, dtype=bool>
			boolean region defining area of interest.
	Output:
		Set of chips defined by (x, y, w, h) in raster order
		
	Author: Joshua Beard
	Contributor: Taz Bales-Heisterkamp
	C: 2/18/17
	E: 2/18/17
	
	EDITS:
		2/18/17 started writing [jb]
			
	NOTES:
		Two ways to implement matrices in python:
			1. A = matrix([[1,2,3],[4,5,6]])
			2. A = matrix('1,2,3;4,5,6')
	
	TODOS:
		1/28/17 Return things
	
	'''
	
	''' Initialization '''
