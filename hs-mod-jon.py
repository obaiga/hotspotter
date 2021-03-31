#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 14 17:56:16 2021

@author: obaiga
-----------------------------------------



-----------------------------------------
[hotspotter]-[Config]
Class ChipConfig
cc_cfg.chip_sqrt_area = 750
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
## args.dbdir = '/Users/obaiga/Jupyter/Python-Research/Compare-Data/Hotspotter-Left-6'

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
    load_all = preload  ## False
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
# if not np.iterable(cx_list):
#     valid_cxs = [cx_list]
# cx_list = np.array(cx_list)  # HACK
   
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
#   Detailed Query Function
# =============================================================================
'''
Important: [hotspotter]-[QueryResult]-Class: QueryResult
'''
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

def prepare_query(qdat, qcxs, dcxs):
    qdat._qcxs = qcxs
    qdat._dcxs = dcxs
    #---------------
    # Flip if needebe
    query_type = qdat.cfg.agg_cfg.query_type
    if query_type == 'vsone':
        (dcxs, qcxs) = (qdat._qcxs, qdat._dcxs)
    elif query_type == 'vsmany':
        (dcxs, qcxs) = (qdat._dcxs, qdat._qcxs)
    else:
        raise Exception('Unknown query_type=%r' % query_type)
    return qcxs, dcxs

def prequery_checks(hs, qdat):
    query_uid = qdat.cfg.get_uid('noCHIP')
    feat_uid = qdat.cfg._feat_cfg.get_uid()
    query_hist_id = (feat_uid, query_uid)
    if hs.query_history[-1][0] != feat_uid:
        print('[mc3] FEAT_UID is different. Need to reload features')
        print('[mc3] Old: ' + str(hs.query_history[-1][0]))
        print('[mc3] New: ' + str(feat_uid))
        hs.unload_cxdata('all')
        hs.refresh_features()
    elif hs.query_history[-1][1] != query_uid:
        print('[mc3] QUERY_UID is different. Need to refresh features')
        print('[mc3] Old: ' + str(hs.query_history[-1][1]))
        print('[mc3] New: ' + str(query_uid))
        hs.refresh_features()
    hs.query_history.append(query_hist_id)
    print('[mc3] query_dcxs(): query_uid = %r ' % query_uid)
    
'''
Important: [hotspotter]-[DataStructures]-Class: NNIndext
'''
def ensure_nn_index(hs, qdat, dcxs):
    # NNIndexes depend on the data cxs AND feature / chip configs
    feat_uid = qdat.cfg._feat_cfg.get_uid()
    dcxs_uid = helpers.hashstr_arr(dcxs, 'dcxs') + feat_uid
    if not dcxs_uid in qdat._dcxs2_index:
        # Make sure the features are all computed first
        print('[mc3] qdat._data_index[dcxs_uid]... cache miss')
        print('[mc3] dcxs_ is not in qdat cache')
        print('[mc3] hashstr(dcxs_) = %r' % dcxs_uid)
        print('[mc3] REFRESHING FEATURES')
        hs.refresh_features(dcxs)
        # Compute the FLANN Index
        data_index = ds.NNIndex(hs, dcxs)
        qdat._dcxs2_index[dcxs_uid] = data_index
    else:
        print('[mc3] qdat._data_index[dcxs_uid]... cache hit')
    qdat._data_index = qdat._dcxs2_index[dcxs_uid]
    
def execute_query_safe(hs, qdat, qcxs, dcxs, use_cache=True):
    '''Executes a query, performs all checks, callable on-the-fly'''
    print('[mc3] Execute query: q%s' % hs.cidstr(qcxs))
    qcxs, dcxs = prepare_query(qdat, qcxs, dcxs)
    # caching
    if not hs.args.nocache_query and use_cache:
        result_list = load_cached_query(hs, qdat)
        if not result_list is None:
            return result_list
    print('[mc3] qcxs=%r' % qdat._qcxs)
    print('[mc3] len(dcxs)=%r' % len(qdat._dcxs))
    ensure_nn_index(hs, qdat, dcxs)
    # Do the actually query
    result_list = execute_query_fast(hs, qdat, qcxs, dcxs)
    for qcx2_res in result_list:
        for qcx, res in qcx2_res.iteritems():
            res.save(hs)
    return result_list

def execute_query_fast(hs, qdat, qcxs, dcxs):
    '''Executes a query and assumes qdat has all precomputed information'''
    # Nearest neighbors
    neighbs = mf.nearest_neighbors(hs, qcxs, qdat)
    # Nearest neighbors weighting and scoring
    weights, filt2_meta = mf.weight_neighbors(hs, neighbs, qdat)
    # Thresholding and weighting
    nnfiltFILT = mf.filter_neighbors(hs, neighbs, weights, qdat)
    # Nearest neighbors to chip matches
    matchesFILT = mf.build_chipmatches(hs, neighbs, nnfiltFILT, qdat)
    # Spatial verification
    matchesSVER = mf.spatial_verification(hs, matchesFILT, qdat)
    # Query results format
    result_list = [
        mf.chipmatch_to_resdict(hs, matchesSVER, filt2_meta, qdat),
    ]
    return result_list

#%%
# =============================================================================
#     Main Query Part
# =============================================================================
#Detailed function: [hsgui]-[guiback]-function: query()

valid_cx = hs.get_valid_cxs()
        # Explain: valid_cxs = np.where(hs.tables.cx2_cid > 0)[0]
'wrapper that queries the entire database'
dcxs = hs.get_indexed_sample()   ## 0-(num-1)
        # Explain: dcxs = hs.indexed_sample_cx

query_cfg=None 
dochecks=True
valid_cx = [0]
#%%
for qcx in valid_cx:
    try: 
#        res = hs.query(qcx)
        #------function: hs.query()
#        res = hs.query_database(qcx)
        #-----function: hs.query_datbase()
        'queries the entire (sampled) database'
        print('\n====================')
        print('[hs] query database')
        print('====================')

        if query_cfg is None:
            hs.assert_prefs()
            query_cfg = hs.prefs.query_cfg

        qdat = hs.qdat
            # Explain: hs.qdat = DataStructures.QueryData() 
        qdat.set_cfg(query_cfg)
        dcxs = hs.get_indexed_sample()
        try:
#            res = mc3.query_dcxs(hs, qcx, dcxs, hs.qdat, dochecks=dochecks)
            #------function:matching_chips3.query_dcxs()
            'wrapper that bypasses all that "qcx2_ map" buisness'
            if dochecks:
                prequery_checks(hs, qdat)
            result_list = execute_query_safe(hs, qdat, [qcx], dcxs)
            res = result_list[0].values()[0]
            
        except mf.QueryException as ex:
            msg = '[hs] Query Failure: %r' % ex
            print(msg)
            if hs.args.strict:
                raise
        print(res)
        
    except Exception as ex:
        # TODO Catch actuall exceptions here
        print('[**query()] ex = %r' % ex)



#%%   
# # detailed function: [DataStructures]-[Class NNIndex]-[function: init()]    
    
# print('[ds] building NNIndex object')
# cx2_desc  = hs.feats.cx2_desc
# assert max(cx_list) < len(cx2_desc)
# # Make unique id for indexed descriptors
# feat_uid   = hs.prefs.feat_cfg.get_uid()
#         ## feat_uid = '_FEAT(hesaff+sift,0_9001)_CHIP(sz750)'
# sample_uid = util.hashstr_arr(cx_list, 'dcxs')
#         ## sample_uid = 'dcxs((444,)kqudaahl)'
# uid = '_' + sample_uid + feat_uid

# # Number of features per sample chip
# nFeat_iter1 = map(lambda cx: len(cx2_desc[cx]), iter(cx_list))
# nFeat_iter2 = map(lambda cx: len(cx2_desc[cx]), iter(cx_list))
# nFeat_iter3 = map(lambda cx: len(cx2_desc[cx]), iter(cx_list))

# # Inverted index from indexed descriptor to chipx and featx
# _ax2_cx = ([cx] * nFeat for (cx, nFeat) in zip(cx_list, nFeat_iter1))
# _ax2_fx = (range(nFeat) for nFeat in iter(nFeat_iter2))
# ax2_cx  = np.array(list(chain.from_iterable(_ax2_cx)))
# ax2_fx  = np.array(list(chain.from_iterable(_ax2_fx)))
# ## For example, there are 444 chips, totally 2133155 features; 
# ## ax2_fx = arange(1,2133155); ax2_cx = ([0:6631]=0; [6632:6632+6042]=1; [:+1574]=2;[:+2436]=3)

# # Aggregate indexed descriptors into continuous structure
# try:
#     # sanatize cx_list
#     cx_list = [cx for cx, nFeat in zip(iter(cx_list), nFeat_iter3) if nFeat > 0]
#     if isinstance(cx2_desc, list):
#         ax2_desc = np.vstack((cx2_desc[cx] for cx in cx_list))  
#             ##ax2_desc.size = [2133155,128]
#     elif isinstance(cx2_desc, np.ndarray):
#         ax2_desc = np.vstack(cx2_desc[cx_list])
# except MemoryError as ex:
#     with util.Indenter2('[mem error]'):
#         print(ex)
#         print('len(cx_list) = %r' % (len(cx_list),))
#         print('len(cx_list) = %r' % (len(cx_list),))
#     raise
# except Exception as ex:
#     with util.Indenter2('[unknown error]'):
#         print(ex)
#         print('cx_list = %r' % (cx_list,))
#     raise
    
# # Build/Load the flann index
# flann_params = {'algorithm': 'kdtree', 'trees': 4}
# precomp_kwargs = {'cache_dir': hs.dirs.cache_dir,
#                   'uid': uid,
#                   'flann_params': flann_params,
#                   'force_recompute': params.args.nocache_flann}
#                             ## from hscom import params
#                             ## params.args.nocache_flann = False
# flann = algos.precompute_flann(data = ax2_desc,**precomp_kwargs)
 
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