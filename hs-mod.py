#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 14 17:56:16 2021

@author: obaiga
"""

from __future__ import division, print_function
import multiprocessing
import numpy as np
import hotspotter.feature_compute2 as fc2
def preload_args_process(args):
    from hscom import helpers
    import sys
    # Process relevant args
    cids = args.query
    if args.vdd:
        helpers.vd(args.dbdir)
        args.vdd = False
    load_all = args.autoquery or len(cids) > 0
    if helpers.inIPython() or '--cmd' in sys.argv:
        args.nosteal = True
    return load_all, cids

def imports():
    pass

#%%
multiprocessing.freeze_support()

defaultdb=None
usedbcache=True
default_load_all=True
import matplotlib
matplotlib.use('Qt5Agg')
imports()
from hscom import argparse2
from hscom import helpers
from hotspotter import HotSpotterAPI as api
args = argparse2.parse_arguments(defaultdb=defaultdb)
# Parse arguments
args = argparse2.fix_args_with_cache(args)
if usedbcache:
    load_all, cids = preload_args_process(args)
else:
    args = argparse2.fix_args_shortnames(args)
    load_all = helpers.get_flag('--load-all', default_load_all)
    
    # Preload process args
if args.delete_global:
    from hscom import fileio as io
    io.delete_global_cache()
    
    # --- Build HotSpotter API ---
hs = api.HotSpotter(args)
#%%
setcfg = args.setcfg

if setcfg is not None:
    import experiment_harness
    print('[main] setting cfg to %r' % setcfg)
    varried_list = experiment_harness.get_varried_params_list([setcfg])
    cfg_dict = varried_list[0]
    #print(cfg_dict)
    hs.prefs.query_cfg.update_cfg(**cfg_dict)
    hs.prefs.save()
    #hs.prefs.printme()
    # load default preferences
    hs.default_preferences()
 #%%   
# Load all data if needed now, otherwise be lazy
try:
    hs.load(load_all=load_all)
    from hscom import fileio as io
    #imported from wrong module
    #from hotspotter import fileio as io
    db_dir = hs.dirs.db_dir
    io.global_cache_write('db_dir', db_dir)
except ValueError as ex:
    print('[main] ValueError = %r' % (ex,))
    if hs.args.strict:
        raise
#%%
hs.load_chips()
hs.load_features()


#%%
query_cfg = None 
if query_cfg is None:
    query_cfg = hs.prefs.query_cfg


