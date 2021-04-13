#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  6 16:45:00 2021
@author: obaiga

------------------
Replace Hotspotter functions: show the result with 1 query vs 1 database image 

Query function: Hotspotter 1vs1

Please before running the program, modify Initilization part 

Bug:Sometimes, click a matched keypoint to observe detailed results, it shows valueError
'too many values to unpack'
------------------
"""

#%%
from __future__ import division, print_function
from os.path import join, expanduser,split
import numpy as np
import sys
### from Hotspotter
from hscom import helpers
from hscom import fileio as io
from hscom import __common__
from hscom import argparse2
from hscom import params
from hotspotter import HotSpotterAPI
from hsviz import draw_func2 as df2
from hsviz import viz
from hsviz import interact

(print, print_, print_on, print_off,
 rrr, profile) = __common__.init(__name__, '[helpers]')

HOME = expanduser('~')
GLOBAL_CACHE_DIR = join(HOME, '.hotspotter/global_cache')
helpers.ensuredir(GLOBAL_CACHE_DIR)

#%%
# =============================================================================
#  Initialization (User needs to modify the below contens )
# =============================================================================

### New database path
dpath = 'C:\\Users\\95316\\code1\\Snow leopard'
#dpath = 'C:\\Users\\95316\\code1'
###Database name
new_db = 'right_diff_cats'
#new_db = 'Hotspotter-Left-6'

Flag_img = False
query_img = '01__Station04__Camera2__2012-7-22__1-53-20(0).JPG'
database_img = '01__Station05__Camera1__2012-6-19__1-56-58(6).JPG'
Flag_cx  = True
query_cx = 1   ## start from 0
db_cx = 4     ## start from 0


#%%
# =============================================================================
#   Detailed Function for Dataset
# =============================================================================

def parse_arguments(defaultdb, usedbcache):
    args = argparse2.parse_arguments(defaultdb=defaultdb)
    # Parse arguments
    args = argparse2.fix_args_with_cache(args)
    if usedbcache:
        if args.vdd:
            helpers.vd(args.dbdir)
            args.vdd = False
        if helpers.inIPython() or '--cmd' in sys.argv:
            args.nosteal = True
    params.args = args
    # Preload process args
    if args.delete_global:
        io.delete_global_cache()
    return args

def open_database(db_dir=None):
    # File -> Open Database
    try:
        # Use the same args in a new (opened) database
        args = params.args
        # Try and load db
        if args is not None:
            args.dbdir = db_dir
        hs = HotSpotterAPI.HotSpotter(args=args, db_dir=db_dir)
        hs.load(load_all=False)
        # Write to cache and connect if successful
        io.global_cache_write('db_dir', db_dir)
        #back.layout_figures()
    except Exception as ex:
        import traceback
        import sys
        print(traceback.format_exc())
        print('aborting open database')
        print(ex)
        if '--strict' in sys.argv:
            raise
        raise
    print('')
    return hs

#%%
# =============================================================================
#     Initialization -  dataset
# =============================================================================
db_dir = join(dpath, new_db)

#------ function:[hsgui]-[guitools]- def select_directory
caption='Select Directory'
print('Selected Directory: %r' % dpath)
io.global_cache_write('select_directory', split(dpath)[0])
print('[*back] valid new_db_dir = %r' % db_dir)
io.global_cache_write('db_dir', db_dir)
helpers.ensurepath(db_dir)
    
    
defaultdb = None
preload = False

args = parse_arguments(defaultdb, defaultdb == 'cache')
# --- Build HotSpotter API ---
hs = open_database(db_dir)

#%%
# =============================================================================
#         Load Chip & Feature 
# =============================================================================
cx_list = None     


cx_list = hs.get_valid_cxs() if cx_list is None else cx_list
    # Explain function-[hs.get_valid_cxs()]
    # valid_cxs = np.where(hs.tables.cx2_cid > 0)[0] 
if not np.iterable(cx_list):
    valid_cxs = [cx_list]
cx_list = np.array(cx_list)  # HACK
   
hs.load_chips(cx_list=cx_list)
hs.load_features(cx_list=cx_list)



#%%
# =============================================================================
#  Show results part
# =============================================================================
if Flag_img & 1:
    query_gx = np.where(hs.tables.gx2_gname == query_img)
    if len(query_gx)>0:
        query_cx = hs.gx2_cxs(query_gx[0][0])[0]
        query_cid = hs.cx2_cid(query_cx)
    else:
        print('query image %s does not exsit.'%query_img)
        
    print('[back] query(cid=%r)' % query_cid)
    print('[back] query (cx = %r)' % query_cx)
    
    db_gx = np.where(hs.tables.gx2_gname == database_img)
    if len(query_gx)>0:
        db_cx = hs.gx2_cxs(db_gx[0][0])[0]
        db_cid = hs.cx2_cid(db_cx)
    else:
        print('database image %s does not exsit.'%database_img)
        
    print('[back] database (cid=%r)' % db_cid)
    print('[back] database (cx = %r)' % db_cx)
elif Flag_cx & 1:
    pass

try:
    query_res = hs.query(query_cx)
except Exception as ex:
    # TODO Catch actually exceptions here
    print('[back] ex = %r' % ex)
    raise

#%%
# =============================================================================
#       Plot results (click in a figure or out of figure)
# =============================================================================

FNUMS = dict(image=1, chip=2, res=3, inspect=4, special=5, name=6)
viz.register_FNUMS(FNUMS)
  
fnum = FNUMS['inspect']
did_exist = df2.plt.fignum_exists(fnum)
df2.figure(fnum=fnum, docla=True, doclf=True)
interact.interact_chipres(hs, query_res, cx=db_cx, fnum=fnum)


