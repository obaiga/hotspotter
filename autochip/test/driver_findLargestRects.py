# driver_findLargestRects.py
'''
This is a driver for findLargestRects.py

Author: Joshua Beard
C: 2/10/17
E: 2/20/17

'''
import numpy as np
import math
import scipi.io as sio

''' Parameters '''
templateName = 'template0.mat'

''' Initialization '''


matContents = sio.loadmat('template0.mat')	# Load up the template generated in ML
template = matContents['template'] 			# get the actual template
