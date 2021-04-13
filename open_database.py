# -*- coding: utf-8 -*-
"""
Created on Thu Apr  8 13:36:26 2021
@author: obaiga

------------------
Replace Hotspotter functions: open database, load chip, load feature and query 

Query function: Hotspotter 1vs1

Please before running the program, modify Initilization part 
------------------
"""
#%%
from __future__ import division, print_function
from os.path import join, expanduser,split
import numpy as np

### from Hotspotter
from hscom import helpers
from hscom import fileio as io
from hscom import __common__
from hscom import argparse2
from hscom import params
from hotspotter import HotSpotterAPI


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
###Database name
new_db = 'right_Cat1'


#%%
# =============================================================================
#   Function 
# =============================================================================

def parse_arguments(defaultdb, usedbcache):
    args = argparse2.parse_arguments(defaultdb=defaultdb)
    # Parse arguments
    args = argparse2.fix_args_with_cache(args)
    if usedbcache:
        if args.vdd:
            helpers.vd(args.dbdir)
            args.vdd = False
    params.args = args
    # Preload process args
    if args.delete_global:
        io.delete_global_cache()
    return args

def preload_args_process(args):
    from hscom import helpers
    # Process relevant args
    cids = args.query
    if args.vdd:
        helpers.vd(args.dbdir)
        args.vdd = False
    load_all = args.autoquery or len(cids) > 0
    return load_all, cids

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
#     Main Query Part
# =============================================================================
#Detailed function: [hsgui]-[guiback]-function: query()

cx_list = hs.get_valid_cxs()
for cx in cx_list:

    
    cid = hs.cx2_cid(cx)
    print('[back] cx = %r' % cx)
    print('[back] query(cid=%r)' % (cid))
    try:
        res = hs.query(cx)
    except Exception as ex:
        # TODO Catch actually exceptions here
        print('[back] ex = %r' % ex)
        raise
        
#%%
# =============================================================================
#    Create flat table (Hotspotter (Original version))
# =============================================================================
from hotspotter import load_data2 as ld2
def write_flat_table(hs):
    dbdir = hs.dirs.db_dir
    # Make flat table
    valid_cx = hs.get_valid_cxs()
    flat_table  = make_flat_table(hs, valid_cx)
    flat_table_fpath  = join(dbdir, 'flat_table.csv')
    # Write flat table
    print('[ld2] Writing flat table')
    helpers.write_to(flat_table_fpath, flat_table)
    
def make_flat_table(hs, cx_list):
    # Valid chip tables
    if len(cx_list) == 0:
        return ''
    cx2_cid   = hs.tables.cx2_cid[cx_list]
    # Use the indexes as ids (FIXME: Just go back to g/n-ids)
    cx2_gname = hs.cx2_gname(cx_list)
    cx2_name  = hs.cx2_name(cx_list)
    try:
        cx2_roi   = hs.tables.cx2_roi[cx_list]
    except IndexError as ex:
        print(ex)
        cx2_roi = np.array([])
    cx2_theta = hs.tables.cx2_theta[cx_list]
    prop_dict = {propkey: [cx2_propval[cx] for cx in iter(cx_list)]
                 for (propkey, cx2_propval) in hs.tables.prop_dict.iteritems()}
    # Turn the chip indexes into a DOCUMENTED csv table
    header = '# flat table'
    column_labels = ['ChipID', 'Image', 'Name', 'roi[tl_x  tl_y  w  h]', 'theta']
    column_list   = [cx2_cid, cx2_gname, cx2_name, cx2_roi, cx2_theta]
    column_type   = [int, int, int, list, float]
    if not prop_dict is None:
        for key, val in prop_dict.iteritems():
            column_labels.append(key)
            column_list.append(val)
            column_type.append(str)

    chip_table = ld2.make_csv_table(column_labels, column_list, header, column_type)
    return chip_table

write_flat_table(hs)