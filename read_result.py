#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 14:46:21 2021

@author: obaiga
"""
from __future__ import division, print_function
from hscom import __common__
(print, print_, print_on, print_off,
 rrr, profile) = __common__.init(__name__, '[mc3]')

from hscom import fileio as io
from hscom import argparse2
from hscom import params
from hsgui import guitools
from hotspotter import HotSpotterAPI
from hotspotter import match_chips3 as mc3
from hotspotter import matching_functions as mf
from hotspotter import DataStructures as ds
from hotspotter import QueryResult as qr
from hscom import helpers

# python
#import pyflann
import numpy as np
import sys 

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
# =============================================================================
#     Initialization - dataset
# =============================================================================
defaultdb = None
preload = False

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
def load_resdict(hs, qcxs, qdat, aug=''):
    real_uid, title_uid = mf.special_uids(qdat, aug)
    # Load the result structures for each query.
    try:
        qcx2_res = {}
        for qcx in qcxs:
            res = qr.QueryResult(qcx, real_uid, qdat)
            res.load(hs)
            qcx2_res[qcx] = res
    except IOError:
        return None
    return qcx2_res

def load_cached_query(hs, qdat, aug_list=['']):
    qcxs = qdat._qcxs
    result_list = []
    for aug in aug_list:
        qcx2_res = load_resdict(hs, qcxs, qdat, aug)
        if qcx2_res is None:
            return None
        result_list.append(qcx2_res)
    print('[mc3] ... query result cache hit')
    return result_list
#%%
hs.assert_prefs()
query_cfg = hs.prefs.query_cfg
qdat = hs.qdat
qdat.set_cfg(query_cfg)
aug = ''
real_uid, title_uid = mf.special_uids(qdat, aug)
try:
        
    res = qr.QueryResult(qdat,real_uid)
    res.load(hs)
        
except Exception as ex:
    # TODO Catch actuall exceptions here
    print('[**query()] ex = %r' % ex)
    
#%%
    