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
from hotspotter import match_chips3 as mc3
from hotspotter import matching_functions as mf
from hotspotter import DataStructures as ds
from hotspotter import QueryResult as qr
from hotspotter import algos
from hscom import __common__
(print, print_, print_on, print_off,
 rrr, profile, printDBG) = __common__.init(__name__, '[mc3]', DEBUG=False)

# python
from os.path import split,join
import pyflann
import numpy as np
import os
import sys 
from itertools import chain

#%%
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
# =============================================================================
#     Initialization - dataset
# =============================================================================
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

# valid_cxs = np.where(hs.tables.cx2_cid > 0)[0] 
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

    
#%%

# =============================================================================
#   Main Query
# =============================================================================

# # valid_cxs = np.where(hs.tables.cx2_cid > 0)[0]
# valid_cx = hs.get_valid_cxs()
# valid_cx = [0]
# fmtstr = util.progress_str(len(valid_cx), '[back*] Query qcx=%r: ')
# for count, qcx in enumerate(valid_cx):
#     sys.stdout.write(fmtstr % (qcx, count))
#     hs.query(qcx, dochecks=False)
#     if count % 100 == 0:
#         sys.stdout.write('\n ...')
# sys.stdout.write('\n ...')
# print('')

#%%
# =============================================================================
#       Query function 
# =============================================================================
## [hotspotter]-[matching_functions]: try_load_resdict()
def try_load_resdict(hs, qreq):
    # Load the result structures for each query.
    qcxs = qreq._qcxs
    uid = qreq.get_uid()
    ## [hotspotter]-[Config]
    ## Class: NNConfig  get_uid_list
    
    qcx2_res = {}
    failed_qcxs = []
    print('get_uid:'+str(uid))   # obaiga comment
    # print('qcx:'+str(qcxs))    # obaiga comment
    for qcx in qcxs:
        try:
            res = qr.QueryResult(qcx, uid)   # qr: [hotspotter]-[QueryResult]
            res.load(hs)
            qcx2_res[qcx] = res
        except IOError:
            failed_qcxs.append(qcx)
    return qcx2_res, failed_qcxs


## [hotspotter]-[match_chips]: below functions
def prep_query_request(qreq=None, query_cfg=None, qcxs=None, dcxs=None, **kwargs):
    print(' --- prep query request ---')
    # Builds or modifies a query request object
    def loggedif(msg, condition):
        # helper function for logging if statment results
        printDBG(msg + '... ' + ['no', 'yes'][condition])
        return condition
    if not loggedif('(1) given qreq?', qreq is not None):
        qreq = ds.QueryRequest()
    if loggedif('(2) given qcxs?', qcxs is not None):
        qreq._qcxs = qcxs
    if loggedif('(3) given dcxs?', dcxs is not None):
        qreq._dcxs = dcxs
    if not loggedif('(4) given qcfg?', query_cfg is not None):
        query_cfg = qreq.cfg
    if loggedif('(4) given kwargs?', len(kwargs) > 0):
        query_cfg = query_cfg.deepcopy(**kwargs)
    #
    qreq.set_cfg(query_cfg) 
    # Function: set_cfg
    # qreq.vsmany = query_cfg.agg_cfg.query_type == 'vsmany'
    # qreq.vsone  = query_cfg.agg_cfg.query_type == 'vsone'
    #
    assert (qreq is not None), ('invalid qeury request')
    assert (qreq._qcxs is not None and len(qreq._qcxs) > 0), (
        'query request has invalid query chip indexes')
    assert (qreq._dcxs is not None and len(qreq._dcxs) > 0), (
        'query request has invalid database chip indexes')
    assert (qreq.cfg is not None), (
        'query request has invalid query config')
    return qreq

def pre_exec_checks(hs, qreq):
    print(' --- pre exec checks ---')
    # Get qreq config information
    dcxs = qreq.get_internal_dcxs()
    feat_uid = qreq.cfg._feat_cfg.get_uid()
    dcxs_uid = util.hashstr_arr(dcxs, 'dcxs')
    # Ensure the index / inverted index exist for this config
    dftup_uid = dcxs_uid + feat_uid
    if not dftup_uid in qreq._dftup2_index:
        print('qreq._dftup2_index[dcxs_uid]... nn_index cache miss')
        print('dftup_uid = %r' % (dftup_uid,))
        print('len(qreq._dftup2_index) = %r' % len(qreq._dftup2_index))
        print('type(qreq._dftup2_index) = %r' % type(qreq._dftup2_index))
        print('qreq = %r' % qreq)
        cx_list = np.unique(np.hstack((qreq._dcxs, qreq._qcxs)))
        hs.refresh_features(cx_list)
        # Compute the FLANN Index
        data_index = ds.NNIndex(hs, dcxs)
        qreq._dftup2_index[dftup_uid] = data_index
    qreq._data_index = qreq._dftup2_index[dftup_uid]
    return qreq

# Query Level 2
def process_query_request(hs, qreq, use_cache=True, safe=True):
    '''
    The standard query interface
    '''
    print(' --- process query request --- ')
    # HotSpotter feature checks
    if safe:
        qreq = mc3.pre_cache_checks(hs, qreq)

    # Try loading as many cached results as possible
    use_cache = not params.args.nocache_query and use_cache
    # print('use_cache:'+ str(use_cache))    # obaiga comment
    if use_cache:
        qcx2_res, failed_qcxs = try_load_resdict(hs, qreq)
    else:
        qcx2_res = {}
        failed_qcxs = qreq._qcxs
        
    # print('failed_qcxs:'+str(len(failed_qcxs)))   # obaiga comment
    # Execute and save queries
    if len(failed_qcxs) > 0:
        if safe:
            qreq = pre_exec_checks(hs, qreq)
        computed_qcx2_res = execute_query_and_save_L1(hs, qreq, failed_qcxs)
        qcx2_res.update(computed_qcx2_res)  # Update cached results
    return qcx2_res


# Query Level 1
def execute_query_and_save_L1(hs, qreq, failed_qcxs=[]):
    print('[q1] execute_query_and_save_L1()')
    orig_qcxs = qreq._qcxs
    if len(failed_qcxs) > 0:
        qreq._qcxs = failed_qcxs
    qcx2_res = execute_query_L0(hs, qreq)  # Execute Queries
    for qcx, res in qcx2_res.items():  # Cache Save
        res.save(hs)
    qreq._qcxs = orig_qcxs
    return qcx2_res


# Query Level 0
def execute_query_L0(hs, qreq):
    '''
    Driver logic of query pipeline
    Input:
        hs   - HotSpotter database object to be queried
        qreq - QueryRequest Object   # use prep_qreq to create one
    Output:
        qcx2_res - mapping from query indexes to QueryResult Objects
    '''
    # Query Chip Indexes
    # * vsone qcxs/dcxs swapping occurs here
    qcxs = qreq.get_internal_qcxs()
    # Nearest neighbors (qcx2_nns)
    # * query descriptors assigned to database descriptors
    # * FLANN used here
    neighbs = mf.nearest_neighbors(hs, qcxs, qreq)
    # Nearest neighbors weighting and scoring (filt2_weights, filt2_meta)
    # * feature matches are weighted
    weights, filt2_meta = mf.weight_neighbors(hs, neighbs, qreq)
    # Thresholding and weighting (qcx2_nnfilter)
    # * feature matches are pruned
    nnfiltFILT = mf.filter_neighbors(hs, neighbs, weights, qreq)
    # Nearest neighbors to chip matches (qcx2_chipmatch)
    # * Inverted index used to create cx2_fmfsfk (TODO: ccx2_fmfv)
    # * Initial scoring occurs
    # * vsone inverse swapping occurs here
    matchesFILT = mf.build_chipmatches(hs, neighbs, nnfiltFILT, qreq)
    # Spatial verification (qcx2_chipmatch) (TODO: cython)
    # * prunes chip results and feature matches
    matchesSVER = mf.spatial_verification(hs, matchesFILT, qreq)
    # Query results format (qcx2_res) (TODO: SQL / Json Encoding)
    # * Final Scoring. Prunes chip results.
    # * packs into a wrapped query result object
    qcx2_res = mf.chipmatch_to_resdict(hs, matchesSVER, filt2_meta, qreq)
    
    qcx2_res = []
    
    return qcx2_res

## [HotSpotterAPI]: Class HotSpotter.query_cxs()
def query_cxs(qcx, cxs, query_cfg=None, **kwargs):
    '''wrapper that restricts query to only known groundtruth.
    Calls the function level query wrappers'''
    print('[hs] query_cxs(kwargs=%r)' % kwargs)
    # Ensure that we can process a query like this
    if query_cfg is None:
        
        query_cfg = hs.prefs.query_cfg
    ## hs.prefs.query_cfg = Config.default_vsmany_cfg(hs)    
    ## [hotspotter]-[Config]
    ## Class: AggregateConfig 
    ## agg_cfg.query_type   = 'vsmany'
    qreq = prep_query_request(qreq=hs.qreq,   ## hs.qreq = ds.QueryRequest()  # Query Data
                                  qcxs=[qcx],   
                                  dcxs=cxs,
                                  query_cfg=query_cfg,  
                                  **kwargs)
    try:
        res = process_query_request(hs, qreq)[qcx]
    except mf.QueryException as ex:
        msg = '[hs] Query Failure: %r' % ex
        print(msg)
        if params.args.strict:
            raise
        return msg
    except AssertionError as ex:
        msg = '[hs] Query Failure: %r' % ex
        print(msg)
        raise
    return res
#%%
# =============================================================================
#       Detailed Query 
# =============================================================================
# valid_cx = hs.get_valid_cxs()
# valid_cx = [0]
# ## function: hs.query
# 'wrapper that queries the entire database'
# dcxs = hs.get_indexed_sample()   ## 0-(num-1)
# fmtstr = util.progress_str(len(valid_cx), '[back*] Query qcx=%r: ')
# for count, qcx in enumerate(valid_cx):
#     sys.stdout.write(fmtstr % (qcx, count))
#     res = query_cxs(qcx, dcxs, dochecks=False)

#%%  detailed function: [match_chips3]-[pre_exec_checks(hs qreq)]
query_cfg = hs.prefs.query_cfg
dcxs = hs.get_indexed_sample()   ## 0-(num-1)
valid_cx = [0]
for count, qcx in enumerate(valid_cx):
    ## hs.qreq = DataStructures.QueryRequest()  # Query Data
    qreq = prep_query_request(qreq=hs.qreq,qcxs=[qcx],dcxs=dcxs,
                              query_cfg=query_cfg,dochecks=False)    
    dcxs = qreq.get_internal_dcxs() # Explain:
    ## dcxs = qreq._dcxs if qreq.vsmany else qreq._qcxs
    feat_uid = qreq.cfg._feat_cfg.get_uid()  
    # feat_uid = '_FEAT(hesaff+sift,0_9001)_CHIP(sz750)'
    dcxs_uid = util.hashstr_arr(dcxs, 'dcxs')
    # dcxs_uid = 'dcxs((444)lxkowaav)'
    # Ensure the index / inverted index exist for this config
    dftup_uid = dcxs_uid + feat_uid
    if not dftup_uid in qreq._dftup2_index:   #  # cached indexes
        print('qreq._dftup2_index[dcxs_uid]... nn_index cache miss')
        print('dftup_uid = %r' % (dftup_uid,))
        print('len(qreq._dftup2_index) = %r' % len(qreq._dftup2_index))   
        print('type(qreq._dftup2_index) = %r' % type(qreq._dftup2_index))
        print('qreq = %r' % qreq)
        cx_list = np.unique(np.hstack((qreq._dcxs, qreq._qcxs)))
        hs.refresh_features(cx_list)    
                ##  hs.load_chips(cx_list=cx_list)
                ##  hs.load_features(cx_list=cx_list)
        # Compute the FLANN Index
        data_index = ds.NNIndex(hs, dcxs)  
        ## 'Nearest Neighbor (FLANN) Index Class'
        qreq._dftup2_index[dftup_uid] = data_index
    qreq._data_index = qreq._dftup2_index[dftup_uid]
    

#%%
def precompute_flann(data, cache_dir=None, uid='', flann_params=None,
                     force_recompute=False):
    ''' Tries to load a cached flann index before doing anything'''
    print('[algos] precompute_flann(%r): ' % uid)
    cache_dir = '.' if cache_dir is None else cache_dir
    # Generate a unique filename for data and flann parameters
    fparams_uid = util.remove_chars(str(flann_params.values()), ', \'[]')
    data_uid = util.hashstr_arr(data, 'dID')  # flann is dependent on the data
    flann_suffix = '_' + fparams_uid + '_' + data_uid + '.flann'
    # Append any user labels
    flann_fname = 'flann_index_' + uid + flann_suffix
    flann_fpath = os.path.normpath(join(cache_dir, flann_fname))
    # Load the index if it exists
    flann = pyflann.FLANN()
    load_success = False
    if util.checkpath(flann_fpath) and not force_recompute:
        try:
            #print('[algos] precompute_flann():
                #trying to load: %r ' % flann_fname)
            flann.load_index(flann_fpath, data)
            print('[algos]...flann cache hit')
            load_success = True
        except Exception as ex:
            print('[algos] precompute_flann(): ...cannot load index')
            print('[algos] precompute_flann(): ...caught ex=\n%r' % (ex,))
    if not load_success:
        # Rebuild the index otherwise
        with util.Timer(msg='compute FLANN', newline=False):
            flann.build_index(data, **flann_params)
        print('[algos] precompute_flann(): save_index(%r)' % flann_fname)
        flann.save_index(flann_fpath.encode("utf-8"))
    return flann

#%%   detailed function: [DataStructures]-[Class NNIndex]-[function: init()]    
print('[ds] building NNIndex object')
cx2_desc  = hs.feats.cx2_desc
assert max(cx_list) < len(cx2_desc)
# Make unique id for indexed descriptors
feat_uid   = hs.prefs.feat_cfg.get_uid()
sample_uid = util.hashstr_arr(cx_list, 'dcxs')
uid = '_' + sample_uid + feat_uid
# Number of features per sample chip
nFeat_iter1 = map(lambda cx: len(cx2_desc[cx]), iter(cx_list))
nFeat_iter2 = map(lambda cx: len(cx2_desc[cx]), iter(cx_list))
nFeat_iter3 = map(lambda cx: len(cx2_desc[cx]), iter(cx_list))
# Inverted index from indexed descriptor to chipx and featx
_ax2_cx = ([cx] * nFeat for (cx, nFeat) in zip(cx_list, nFeat_iter1))
_ax2_fx = (range(nFeat) for nFeat in iter(nFeat_iter2))
ax2_cx  = np.array(list(chain.from_iterable(_ax2_cx)))
ax2_fx  = np.array(list(chain.from_iterable(_ax2_fx)))
# Aggregate indexed descriptors into continuous structure
try:
    # sanatize cx_list
    cx_list = [cx for cx, nFeat in zip(iter(cx_list), nFeat_iter3) if nFeat > 0]
    if isinstance(cx2_desc, list):
        ax2_desc = np.vstack((cx2_desc[cx] for cx in cx_list))
    elif isinstance(cx2_desc, np.ndarray):
        ax2_desc = np.vstack(cx2_desc[cx_list])
except MemoryError as ex:
    with util.Indenter2('[mem error]'):
        print(ex)
        print('len(cx_list) = %r' % (len(cx_list),))
        print('len(cx_list) = %r' % (len(cx_list),))
    raise
except Exception as ex:
    with util.Indenter2('[unknown error]'):
        print(ex)
        print('cx_list = %r' % (cx_list,))
    raise
# Build/Load the flann index
flann_params = {'algorithm': 'kdtree', 'trees': 4}
precomp_kwargs = {'cache_dir': hs.dirs.cache_dir,
                  'uid': uid,
                  'flann_params': flann_params,
                  'force_recompute': params.args.nocache_flann}
flann = precompute_flann(ax2_desc,**precomp_kwargs)
 

#%%
# =============================================================================
#  Detailed Query Result 
# =============================================================================

# # [HotspotterAPI]
# # Class HotSpotter: function [default_preferences]
# # hs.prefs.query_cfg = Config.default_vsmany_cfg(hs)
# query_cfg = hs.prefs.query_cfg
# valid_cx = [0]
# for count, qcx in enumerate(valid_cx):
#     ## hs.qreq = ds.QueryRequest()  # Query Data
#     qreq = prep_query_request(qreq=hs.qreq,qcxs=[qcx],dcxs=dcxs,
#                               query_cfg=query_cfg,dochecks=False)
#     qcxs = qreq._qcxs     ## when querying, qreq._qcxs = qcxs
#     uid = qreq.get_uid() 
#     ## uid = _NN(K4+1,last,cks1024)_FILT(lnbnn_1)_SV(50,0.01,0.5_2,csum)
#     ##_AGG(vsmany,csum)_FEAT(hesaff+sift,0_9001)_CHIP(sz750)_dcxs((444)lxkowaav)
    
#     ## [hotspotter]-[Config]
#     ## Class: NNConfig  get_uid_list
    
#     ## function: try_load_resdict------------
#     qcx2_res = {}
#     failed_qcxs = []
#     # print('get_uid:'+str(uid))   # obaiga comment
#     # print('qcx:'+str(qcxs))    # obaiga comment
    
#     for qcx in qcxs:
#         try:
#             res = qr.QueryResult(qcx, uid)  # init
#             # function: res.load(hs)----------
#             fpath = qr.query_result_fpath(hs, qcx, uid)  # obaiga comment
#             qcx_good = res.qcx
#             with open(fpath, 'rb') as file_:
#                 npz = np.load(file_)
#                 ## npz.files: ['_printable_exclude','qcx', 
#                 ## 'uid', 'cx2_fm','cx2_fs','cx2_fk','cx2_score','filt2_meta']
#                 for _key in npz.files:
#                     res.__dict__[_key] = npz[_key]
#                 npz.close()
                
#             print('[qr] res.load() fpath=%r' % (split(fpath)[1],))
#             # These are nonarray items even if they are not lists
#             # tolist seems to convert them back to their original
#             # python representation
#             res.qcx = res.qcx.tolist()
#             try:
#                 res.filt2_meta = res.filt2_meta.tolist()
#             except AttributeError:
#                 print('[qr] loading old result format')
#                 res.filt2_meta = {}
#             res.uid = res.uid.tolist()
#             #-----------
#             qcx2_res[qcx] = res
            
#         except IOError:
#             failed_qcxs.append(qcx)
    #---------------
#%%
# path = hs.dirs.qres_dir
# file_name = 'res_soicpjlbuqjedoah_qcid=1.npz'

# b = np.load(os.path.join(path,file_name))

# file_name2 = 'res_w1=@2,y0es`5;[=]_qcid=1.npz'
# b2 = np.load(os.path.join(path,file_name2))