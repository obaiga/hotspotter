# 
'''
This is a tool for loading a .mat file and turning it into a template for autochipping

Author: Joshua Beard
C: 2/27/17
EDITS:

TODO:


'''
import scipy.io as sio
import os

def getTemplate(pathTo,matFileName):
	if os.sep == '\\':				# Windows
		if pathTo.endswith('\\'):	# separator is present
			m = sio.loadmat(pathTo+matFileName)
		else:						# separator is absent
			m = sio.loadmat(pathTo+'\\'+matFileName)
	else:							# Unix
		if pathTo.endswith('/'):	# separator is present
			m = sio.loadmat(pathTo+matFileName)
		else:						# separator is absent
			m = sio.loadmat(pathTo+'/'+matFileName)
	#/if os.sep
	
	return = m['template']
	