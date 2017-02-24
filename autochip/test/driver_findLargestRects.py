# driver_findLargestRects.py
'''
This is a driver for findLargestRects.py

Author: Joshua Beard
C: 2/10/17
E: 2/20/17

'''

import numpy as np
import math
import scipy.io as sio
import sys
# BEWARE the hardcoded path
sys.path.append('/home/joshuabeard/Documents/hotspotter/autochip')
from findLargestRects as flr


''' Parameters '''
templateName = 'template0.mat'

''' Initialization '''
matContents = sio.loadmat(templateName)	# Load up the template generated in ML
template = matContents['template'] 		# get the actual template

largestRect = flr.findLargestRects(template)


