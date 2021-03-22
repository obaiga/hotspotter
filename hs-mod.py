#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 14 17:56:16 2021

@author: obaiga


[hotspotter]-[Config]
Class ChipConfig
cc_cfg.chip_sqrt_area = 750
"""

import multiprocessing
multiprocessing.freeze_support()
from hscom import fileio as io
from hscom import params
from hotspotter import HotSpotterAPI as api
from hsgui import guiback
from hsgui import guitools
from hotspotter import HotSpotterAPI
from hscom import helpers as util

# python
import numpy as np
import sys 

defaultdb = None
preload = False
app = None

def parse_arguments(defaultdb, usedbcache):
    from hscom import argparse2
    from hscom import params
    from hscom import helpers as util
    from hscom import fileio as io
    import sys
    args = argparse2.parse_arguments(defaultdb=defaultdb)
    # Parse arguments
    args = argparse2.fix_args_with_cache(args)
    if usedbcache:
        if args.vdd:
            util.vd(args.dbdir)
            args.vdd = False
        if util.inIPython() or '--cmd' in sys.argv:
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
        #args = back.params.args
        if db_dir is None:
            msg = 'Select (or create) a database directory.'
            db_dir = guitools.select_directory(msg)
        print('[*back] user selects database: ' + db_dir)
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
args = parse_arguments(defaultdb, defaultdb == 'cache')
# --- Build HotSpotter API ---
hs = open_database(args.dbdir)
setcfg = args.setcfg
if setcfg is not None:
    # FIXME move experiment harness to hsdev
    import experiment_harness
    print('[tapi.main] setting cfg to %r' % setcfg)
    varied_list = experiment_harness.get_varied_params_list([setcfg])
    cfg_dict = varied_list[0]
    hs.prefs.query_cfg.update_cfg(**cfg_dict)
    hs.prefs.save()
    hs.prefs.printme()
# Load all data if needed now, otherwise be lazy
try:
    load_all = preload
    hs.load(load_all=load_all)
    db_dir = hs.dirs.db_dir
    io.global_cache_write('db_dir', db_dir)
except ValueError as ex:
    print('[tapi.main] ValueError = %r' % (ex,))
    if params.args.strict:
        raise


#%%
        
cx_list = None     
cx_list = hs.get_valid_cxs() if cx_list is None else cx_list
if not np.iterable(cx_list):
    valid_cxs = [cx_list]
cx_list = np.array(cx_list)  # HACK
   
hs.load_chips(cx_list=cx_list)
hs.load_features(cx_list=cx_list)


#%%

# A list of default internal headers to display
table_headers = {
    'gxs':  ['gx', 'gname', 'nCxs', 'aif'],
    'cxs':  ['cid', 'name', 'gname', 'nGt', 'nKpts', 'theta'],
    'nxs':  ['nx', 'name', 'nCxs'],
    'res':  ['rank', 'score', 'name', 'cid']
}

# Lists internal headers whos items are editable
table_editable = {
    'gxs':  [],
    'cxs':  ['name'],
    'nxs':  ['name'],
    'res':  ['name'],
}

# A map from short internal headers to fancy headers seen by the user
fancy_headers = {
    'gx':         'Image Index',
    'nx':         'Name Index',
    'cid':        'Chip ID',
    'aif':        'All Detected',
    'gname':      'Image Name',
    'nCxs':       '#Chips',
    'name':       'Name',
    'nGt':        '#GT',
    'nKpts':      '#Kpts',
    'theta':      'Theta',
    'roi':        'ROI (x, y, w, h)',
    'rank':       'Rank',
    'score':      'Confidence',
    'match_name': 'Matching Name',
}

def _populate_table(tblname, extra_cols={},
                    index_list=None, prefix_cols=[]):
    print('[*back] _populate_table(%r)' % tblname)
    headers = table_headers[tblname]
    editable = table_editable[tblname]
    if tblname == 'cxs':  # in ['cxs', 'res']: TODO props in restable
        prop_keys = list(hs.tables.prop_dict.keys())
    else:
        prop_keys = []
    col_headers, col_editable = guitools.make_header_lists(headers,
                                                           editable,
                                                           prop_keys)
    if index_list is None:
        index_list = hs.get_valid_indexes(tblname)
    # Prefix datatup
    prefix_datatup = [[prefix_col.get(header, 'error')
                       for header in col_headers]
                      for prefix_col in prefix_cols]
    body_datatup = hs.get_datatup_list(tblname, index_list,
                                            col_headers, extra_cols)
    datatup_list = prefix_datatup + body_datatup
    row_list = list(range(len(datatup_list)))
    # Populate with fancy headers.
    col_fancyheaders = [fancy_headers[key]
                        if key in fancy_headers else key
                        for key in col_headers]

def populate_chip_table():
    _populate_table('cxs')
    
#%%
'''
function: [hsgui]-[guiback]-precompute_queries(back)
'''    

# # function: precompute_feats()    
# hs.update_samples()
# hs.refresh_features()
# #back.front.blockSignals(prevBlock)
# populate_chip_table()
# print('')

valid_cx = hs.get_valid_cxs()
valid_cx = [0]
fmtstr = util.progress_str(len(valid_cx), '[back*] Query qcx=%r: ')
for count, qcx in enumerate(valid_cx):
    sys.stdout.write(fmtstr % (qcx, count))
    hs.query(qcx, dochecks=False)
    if count % 100 == 0:
        sys.stdout.write('\n ...')
sys.stdout.write('\n ...')
print('')
