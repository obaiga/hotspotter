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
# hs.load_chips()
# hs.load_features()


#%%
# print('\n=============================')
# print('[fc2] Precomputing and loading features: %r' % hs.get_db_name())
# print('=============================')
# #----------------
# # COMPUTE SETUP
# #----------------
# cx_list = None
# use_cache = not hs.args.nocache_feats
# use_big_cache = use_cache and cx_list is None
# feat_cfg = hs.prefs.feat_cfg
# feat_uid = feat_cfg.get_uid()
# if hs.feats.feat_uid != '' and hs.feats.feat_uid != feat_uid:
#     print('[fc2] Disagreement: OLD_feat_uid = %r' % hs.feats.feat_uid)
#     print('[fc2] Disagreement: NEW_feat_uid = %r' % feat_uid)
#     print('[fc2] Unloading all chip information')
#     hs.unload_all()
#     hs.load_chips(cx_list=cx_list)
# print('[fc2] feat_uid = %r' % feat_uid)
# # Get the list of chip features to load
# cx_list = hs.get_valid_cxs() if cx_list is None else cx_list
# if not np.iterable(cx_list):
#     cx_list = [cx_list]

# cx_list = np.array(cx_list)  # HACK
# if use_big_cache:  # use only if all descriptors requested
#     kpts_list, desc_list = fc2._load_features_bigcache(hs, cx_list)
# else:
#     kpts_list, desc_list = fc2._load_features_individualy(hs, cx_list)
# # Extend the datastructure if needed
# list_size = max(cx_list) + 1
# helpers.ensure_list_size(hs.feats.cx2_kpts, list_size)
# helpers.ensure_list_size(hs.feats.cx2_desc, list_size)
# # Copy the values into the ChipPaths object
# for lx, cx in enumerate(cx_list):
#     hs.feats.cx2_kpts[cx] = kpts_list[lx]
# for lx, cx in enumerate(cx_list):
#     hs.feats.cx2_desc[cx] = desc_list[lx]
# hs.feats.feat_uid = feat_uid
# print('[fc2]=============================')

#%%
query_cfg = None 
cxs = hs.get_indexed_sample()

if query_cfg is None:
    query_cfg = hs.prefs.query_cfg
qreq = mc3.prep_query_request(qreq=hs.qdat,qcxs=[qcx],dcxs=cxs,
                              query_cfg=query_cfg,**kwargs)


