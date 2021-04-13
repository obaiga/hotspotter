#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  6 16:45:00 2021
@author: obaiga

------------------
Replace Hotspotter functions: open database, load chip, load feature and query 

Query function: Hotspotter 1vs1

Please before running the program, modify Initilization part 
------------------
"""

#%%
from __future__ import division, print_function
from os.path import join, expanduser,split,exists
from os import makedirs 
import numpy as np
### from Hotspotter
from hscom import helpers
from hscom import fileio as io
from hscom import __common__
from hscom import argparse2
from hscom import params
from hotspotter import HotSpotterAPI
from hsviz import draw_func2 as df2
from hsviz import viz

(print, print_, print_on, print_off,
 rrr, profile) = __common__.init(__name__, '[helpers]')

HOME = expanduser('~')
GLOBAL_CACHE_DIR = join(HOME, '.hotspotter/global_cache')
helpers.ensuredir(GLOBAL_CACHE_DIR)

Flag_save = 1
#%%
# =============================================================================
#  Initialization (User needs to modify the below contens )
# =============================================================================

### New database path
dpath = 'C:\\Users\\95316\\code1\\Snow leopard'
###Database name
new_db = 'left_diff_cats'

db_dir = join(dpath, new_db)
save_dir = join(db_dir,'results','all_matched')
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


if not exists(save_dir):
    makedirs(save_dir)


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
#     Detail plot function
# =============================================================================
(print, print_, print_on, print_off, rrr, profile, printDBG) = \
    __common__.init(__name__, '[viz]', DEBUG=False)
NO_LABEL_OVERRIDE = helpers.get_arg('--no-label-override', type_=bool, default=None)

# COLORS

ORANGE = np.array((255, 127,   0, 255)) / 255.0
RED    = np.array((255,   0,   0, 255)) / 255.0
GREEN  = np.array((  0, 255,   0, 255)) / 255.0
BLUE   = np.array((  0,   0, 255, 255)) / 255.0
YELLOW = np.array((255, 255,   0, 255)) / 255.0
BLACK  = np.array((  0,   0,   0, 255)) / 255.0
WHITE  = np.array((255, 255, 255, 255)) / 255.0
GRAY   = np.array((127, 127, 127, 255)) / 255.0
DEEP_PINK    = np.array((255,  20, 147, 255)) / 255.0
PINK         = np.array((255,  100, 100, 255)) / 255.0
FALSE_RED    = np.array((255,  51,   0, 255)) / 255.0
TRUE_GREEN   = np.array((  0, 255,   0, 255)) / 255.0
DARK_ORANGE  = np.array((127,  63,   0, 255)) / 255.0
DARK_YELLOW  = np.array((127,  127,   0, 255)) / 255.0
PURPLE = np.array((102,   0, 153, 255)) / 255.0
UNKNOWN_PURP = PURPLE
    
def res_show_chipres(res, hs, cx, **kwargs):
    'Wrapper for show_chipres(show annotated chip match result) '
    return show_chipres(hs, res, cx, **kwargs)

def show_chipres(hs, res, cx, fnum=None, pnum=None, sel_fm=[], in_image=False, **kwargs):
    'shows single annotated match result.'
    qcx = res.qcx
    #cx2_score = res.get_cx2_score()
    cx2_fm    = res.get_cx2_fm()
    cx2_fs    = res.get_cx2_fs()
    #cx2_fk    = res.get_cx2_fk()
    #printDBG('[viz.show_chipres()] Showing matches from %s' % (vs_str))
    #printDBG('[viz.show_chipres()] fnum=%r, pnum=%r' % (fnum, pnum))
    # Test valid cx
    printDBG('[viz] show_chipres()')
    if np.isnan(cx):
        nan_img = np.zeros((32, 32), dtype=np.uint8)
        title = '(q%s v %r)' % (hs.cidstr(qcx), cx)
        df2.imshow(nan_img, fnum=fnum, pnum=pnum, title=title)
        return
    fm = cx2_fm[cx]
    fs = cx2_fs[cx]
    #fk = cx2_fk[cx]
    #vs_str = hs.vs_str(qcx, cx)
    # Read query and result info (chips, names, ...)
    if in_image:
        # TODO: rectify build_transform2 with cc2
        # clean up so its not abysmal
        rchip1, rchip2 = [hs.cx2_image(_) for _ in [qcx, cx]]
        kpts1, kpts2   = viz.cx2_imgkpts(hs, [qcx, cx])
    else:
        rchip1, rchip2 = hs.get_chip([qcx, cx])
        kpts1, kpts2   = hs.get_kpts([qcx, cx])

    # Build annotation strings / colors
    lbl1 = 'q' + hs.cidstr(qcx)
    lbl2 = hs.cidstr(cx)
    if in_image:
        # HACK!
        lbl1 = None
        lbl2 = None
    # Draws the chips and keypoint matches
    kwargs_ = dict(fs=fs, lbl1=lbl1, lbl2=lbl2, fnum=fnum,
                   pnum=pnum, vert=hs.prefs.display_cfg.vert)
    kwargs_.update(kwargs)
#    ax, xywh1, xywh2 = df2.show_chipmatch2(rchip1, rchip2, kpts1, kpts2, fm, **kwargs_)
    ax, xywh1, xywh2 = show_chipmatch2(rchip1, rchip2, kpts1, kpts2, fm, **kwargs_)
    x1, y1, w1, h1 = xywh1
    x2, y2, w2, h2 = xywh2
    if len(sel_fm) > 0:
        # Draw any selected matches
        _smargs = dict(rect=True, colors=df2.BLUE)
#        df2.draw_fmatch(xywh1, xywh2, kpts1, kpts2, sel_fm, **_smargs)
        draw_fmatch(xywh1, xywh2, kpts1, kpts2, sel_fm, **_smargs)
    offset1 = (x1, y1)
    offset2 = (x2, y2)
    annotate_chipres(hs, res, cx, xywh2=xywh2, in_image=in_image, offset1=offset1, offset2=offset2, **kwargs)
    return ax, xywh1, xywh2

### from viz
def annotate_chipres(hs, res, cx, showTF=True, showScore=True, title_pref='',
                     title_suff='', show_2nd_gname=True, show_2nd_name=True, 
                     show_1st=True,
                     time_appart=True, in_image=False, offset1=(0, 0),
                     offset2=(0, 0), show_query=True, xywh2=None, **kwargs):
    printDBG('[viz] annotate_chipres()')
    #print('Did not expect args: %r' % (kwargs.keys(),))
    qcx = res.qcx
    score = res.cx2_score[cx]
    matched_kpts= np.float32(len(res.cx2_fs[cx]))
    print('matched_kpts=%d'%matched_kpts)
    # TODO Use this function when you clean show_chipres
    (truestr, falsestr, nonamestr) = ('TRUE', 'FALSE', '???')
    is_true, is_unknown = hs.is_true_match(qcx, cx)
    isgt_str = nonamestr if is_unknown else (truestr if is_true else falsestr)
    match_color = {nonamestr: df2.UNKNOWN_PURP,
                   truestr:   df2.TRUE_GREEN,
                   falsestr:  df2.FALSE_RED}[isgt_str]
    # Build title
    title = '*%s*' % isgt_str if showTF else ''
    if showScore:
        score_str = (' score=' + helpers.num_fmt(score))% (score)
        score_str +=('   matched_kpts='+ helpers.num_fmt(matched_kpts))% (matched_kpts)
        
        title += score_str
    title = title_pref + str(title) + title_suff
    # Build xlabel
    xlabel_ = []
    ax = df2.gca()
    ax._hs_viewtype = 'chipres'
    ax._hs_qcx = qcx
    ax._hs_cx = cx
    
    if 'show_1st':
        xlabel_.append('top_gname=%r'%hs.cx2_gname(qcx))
        xlabel_.append('top_name=%r'%hs.cx2_name(qcx))

    if 'show_2nd_gname':
        xlabel_.append('\n below_gname=%r' % hs.cx2_gname(cx))
    if 'show_2nd_name':
        xlabel_.append('below_name=%r' % hs.cx2_name(cx))
    if 'time_appart':
        xlabel_.append('\n' + hs.get_timedelta_str(qcx, cx))
    xlabel = ', '.join(xlabel_)


    if NO_LABEL_OVERRIDE:
        title = ''
        xlabel = ''
    df2.set_title(title, ax)
    df2.set_xlabel(xlabel, ax)
    if in_image:
        roi1 = hs.cx2_roi(qcx) + np.array(list(offset1) + [0, 0])
        roi2 = hs.cx2_roi(cx) + np.array(list(offset2) + [0, 0])
        theta1 = hs.cx2_theta(qcx)
        theta2 = hs.cx2_theta(cx)
        # HACK!
        lbl1 = 'q' + hs.cidstr(qcx)
        lbl2 = hs.cidstr(cx)
        if show_query:
            df2.draw_roi(roi1, bbox_color=df2.ORANGE, label=lbl1, theta=theta1)
        df2.draw_roi(roi2, bbox_color=match_color, label=lbl2, theta=theta2)
        # No matches draw a red box
        if len(res.cx2_fm[cx]) == 0:
            df2.draw_boxedX(roi2, theta=theta2)
    else:
        if xywh2 is None:
            xy, w, h = df2._axis_xy_width_height(ax)
            xywh2 = (xy[0], xy[1], w, h)
        df2.draw_border(ax, match_color, 4, offset=offset2)
        # No matches draw a red box
        if len(res.cx2_fm[cx]) == 0:
            df2.draw_boxedX(xywh2)


def show_chipmatch2(rchip1, rchip2, kpts1, kpts2, fm=None, fs=None, title=None,
                    vert=None, fnum=None, pnum=None, **kwargs):
    '''Draws two chips and the feature matches between them. feature matches
    kpts1 and kpts2 use the (x,y,a,c,d)
    '''
    printDBG('[df2] draw_matches2() fnum=%r, pnum=%r' % (fnum, pnum))
    # get matching keypoints + offset
    (h1, w1) = rchip1.shape[0:2]  # get chip (h, w) dimensions
    (h2, w2) = rchip2.shape[0:2]
    # Stack the compared chips
    match_img, woff, hoff = df2.stack_images(rchip1, rchip2, vert)
    xywh1 = (0, 0, w1, h1)
    xywh2 = (woff, hoff, w2, h2)
    # Show the stacked chips
    fig, ax = df2.imshow(match_img, title=title, fnum=fnum, pnum=pnum)
    # Overlay feature match nnotations
    draw_fmatch(xywh1, xywh2, kpts1, kpts2, fm, fs, **kwargs)
    

    
    return ax, xywh1, xywh2


# draw feature match
def draw_fmatch(xywh1, xywh2, kpts1, kpts2, fm, fs=None, lbl1=None, lbl2=None,
                fnum=None, pnum=None, rect=False, colorbar_=True, **kwargs):
    '''Draws the matching features. This is draw because it is an overlay
    xywh1 - location of rchip1 in the axes
    xywh2 - location or rchip2 in the axes
    '''
    if fm is None:
        assert kpts1.shape == kpts2.shape, 'shapes different or fm not none'
        fm = np.tile(np.arange(0, len(kpts1)), (2, 1)).T
#    pts       = kwargs.get('draw_pts', False)
#    ell       = kwargs.get('draw_ell', True)
#    lines     = kwargs.get('draw_lines', True)
        
    pts = False
    ell = True 
    lines = True
    
    ell_alpha = kwargs.get('ell_alpha', .4)
    nMatch = len(fm)
    #printDBG('[df2.draw_fnmatch] nMatch=%r' % nMatch)
    x1, y1, w1, h1 = xywh1
    x2, y2, w2, h2 = xywh2
    offset2 = (x2, y2)
    # Custom user label for chips 1 and 2
    if lbl1 is not None:
        df2.absolute_lbl(x1 + w1, y1, lbl1)
    if lbl2 is not None:
        df2.absolute_lbl(x2 + w2, y2, lbl2)
    # Plot the number of matches
    if kwargs.get('show_nMatches', False):
        df2.upperleft_text('#match=%d' % nMatch)
    # Draw all keypoints in both chips as points
    if kwargs.get('all_kpts', False):
        all_args = dict(ell=False, pts=pts, pts_color=GREEN, pts_size=2,
                        ell_alpha=ell_alpha, rect=rect)
        all_args.update(kwargs)
        df2.draw_kpts2(kpts1, **all_args)
        df2.draw_kpts2(kpts2, offset=offset2, **all_args)
    # Draw Lines and Ellipses and Points oh my
    if nMatch > 0:
        colors = [kwargs['colors']] * nMatch if 'colors' in kwargs else df2.distinct_colors(nMatch)
        if fs is not None:
            colors = df2.feat_scores_to_color(fs, 'hot')

        acols = df2.add_alpha(colors)

        # Helper functions
        def _drawkpts(**_kwargs):
            _kwargs.update(kwargs)
            fxs1 = fm[:, 0]
            fxs2 = fm[:, 1]
            df2.draw_kpts2(kpts1[fxs1], rect=rect, **_kwargs)
            df2.draw_kpts2(kpts2[fxs2], offset=offset2, rect=rect, **_kwargs)

        def _drawlines(**_kwargs):
            _kwargs.update(kwargs)
            df2.draw_lines2(kpts1, kpts2, fm, fs, kpts2_offset=offset2, **_kwargs)

        # User helpers
        if ell:
            _drawkpts(pts=False, ell=True, color_list=colors)
        if pts:
            _drawkpts(pts_size=8, pts=True, ell=False, pts_color=BLACK)
            _drawkpts(pts_size=6, pts=True, ell=False, color_list=acols)
        if lines:
            _drawlines(color_list=colors)
    else:
        df2.draw_boxedX(xywh2)
    if fs is not None and colorbar_ and 'colors' in vars() and colors is not None:
        df2.colorbar(fs, colors)
    #legend()
#    print('[draw_fmatch] ell = %r, pts=%r, lines= %r' % (str(ell),str(pts),str(lines)))   ## comment by obaiga
    
    return None


#%%
# =============================================================================
#  Show results part
# =============================================================================
cx_lis = hs.get_valid_cxs()
for query_cx in cx_lis:
    query_cid = hs.cx2_cid(query_cx)
    cx_db_ls = hs.get_valid_cxs()
    for db_cx in cx_db_ls:
        if query_cx != db_cx:
            db_cid = hs.cx2_cid(db_cx)
            print('[back] query(cid=%r)' % query_cid)
            print('[back] query (cx = %r)' % query_cx)
            print('[back] database (cid=%r)' % db_cid)
            print('[back] database (cx = %r)' % db_cx)
            try:
                query_res = hs.query(query_cx)
            except Exception as ex:
                # TODO Catch actually exceptions here
                print('[back] ex = %r' % ex)
                raise
            
            #-----function: def show_single_query(back, res, cx, **kwargs):
            FNUMS = dict(image=1, chip=2, res=3, inspect=4, special=5, name=6)
            viz.register_FNUMS(FNUMS)
            
            fnum = FNUMS['inspect']
            did_exist = df2.plt.fignum_exists(fnum)
            df2.figure(fnum=fnum, docla=True, doclf=True)
            
            #------- function: interact.interact_chipres(back.hs, res, cx=cx, fnum=fnum)
            annote_ptr = [0]
            pnum=(1, 1, 1)
            xywh2_ptr = [None]
            
            #-------function: def _chipmatch_view(pnum=(1, 1, 1), **kwargs):
            
            mode = annote_ptr[0]
            draw_ell = mode >= 1
            draw_lines = mode == 2
            annote_ptr[0] = (annote_ptr[0] + 1) % 3
            df2.figure(fnum=fnum, docla=True, doclf=True)
            # TODO RENAME This to remove res and rectify with show_chipres
            tup = res_show_chipres(query_res, hs, db_cx, fnum=fnum, pnum=pnum,
                                       draw_lines=draw_lines, draw_ell=draw_ell,
                                       colorbar_=True)
            
            figtitle='Inspect Query Result'
            df2.set_figtitle(figtitle + hs.vs_str(query_cx, db_cx))
            #
            if Flag_save & 1:
                fpath = save_dir
                usetitle = 'querycid_' + str(query_cid) + '_db' + str(db_cid)
                df2.save_figure(fnum=fnum, fpath=fpath, usetitle=usetitle, overwrite=True)


   
