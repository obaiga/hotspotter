#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 15 22:57:52 2021

@author: obaiga

Function: [hotspotter]-[load_data2]-[load_csv_tables]
"""

#%%
from os.path import join,exists
import os
import re
from PIL import Image
import numpy as np
import hotspotter.DataStructures as ds
from hscom import tools, helpers
import warnings
import cv2
from hscom import fileio as io
from hscom.Parallelize import parallel_compute
import hotspotter.extern_feat as extern_feat
import hotspotter.feature_compute2 as fc2
#%%
db_dir = 'C:\Users\95316\code1\Hotspotter-Left-6'
UNKNOWN_NAME = '____'
NAME_TABLE_FNAME = 'name_table.csv'
IMAGE_TABLE_FNAME = 'image_table.csv'
CHIP_TABLE_FNAME = 'chip_table.csv'

RDIR_INTERNAL2 = '_hsdb'
internal_dir = join(db_dir,RDIR_INTERNAL2)

VERBOSE_LOAD_DATA = True
RDIR_IMG = 'images'

chip_table   = join(internal_dir, CHIP_TABLE_FNAME)
name_table   = join(internal_dir, NAME_TABLE_FNAME)
image_table  = join(internal_dir, IMAGE_TABLE_FNAME)  # TODO: Make optional
img_dir      = join(db_dir, RDIR_IMG)

def tryindex(list, *args):
    for val in args:
        try:
            return list.index(val)
        except ValueError:
            pass
    return -1
#%%

try:
    # ------------------
    # --- READ NAMES ---
    # ------------------
    print('[ld2] Loading name table: %r' % name_table)
    nx2_name = [UNKNOWN_NAME, UNKNOWN_NAME]
    nid2_nx  = {0: 0, 1: 1}
    name_lines = open(name_table, 'r')
    for line_num, csv_line in enumerate(name_lines):
        csv_line = csv_line.strip('\n\r\t ')
        if len(csv_line) == 0 or csv_line.find('#') == 0:
            continue
        csv_fields = [_.strip(' ') for _ in csv_line.strip('\n\r ').split(',')]
        nid = int(csv_fields[0])
        name = csv_fields[1]
        nid2_nx[nid] = len(nx2_name)
        nx2_name.append(name)
    name_lines.close()
    if VERBOSE_LOAD_DATA:
        print('[ld2] * Loaded %r names (excluding unknown names)' % (len(nx2_name) - 2))
        print('[ld2] * Done loading name table')
except IOError as ex:
    print('IOError: %r' % ex)
    print('[ld2.name] loading without name table')
    #raise
except Exception as ex:
    print('[ld2.name] ERROR %r' % ex)
    #print('[ld2.name] ERROR name_tbl parsing: %s' % (''.join(cid_lines)))
    print('[ld2.name] ERROR on line number:  %r' % (line_num))
    print('[ld2.name] ERROR on line:         %r' % (csv_line))
    print('[ld2.name] ERROR on fields:       %r' % (csv_fields))
    
#%%
try:
    # -------------------
    # --- READ IMAGES ---
    # -------------------
    gx2_gname = []
    gx2_aif   = []
    gid2_gx = {}  # this is not used. It can probably be removed

    def add_image(gname, aif, gid):
        gx = len(gx2_gname)
        gx2_gname.append(gname)
        gx2_aif.append(aif)
        if gid is not None:
            # this is not used. It can probably be removed
            gid2_gx[gid] = gx

    print('[ld2] Loading images')
    # Load Image Table
    # <LEGACY CODE>
    if VERBOSE_LOAD_DATA:
        print('[ld2] * Loading image table: %r' % image_table)
    gid_lines = open(image_table, 'r').readlines()
    for line_num, csv_line in enumerate(gid_lines):
        csv_line = csv_line.strip('\n\r\t ')
        if len(csv_line) == 0 or csv_line.find('#') == 0:
            continue
        csv_fields = [_.strip(' ') for _ in csv_line.strip('\n\r ').split(',')]
        gid = int(csv_fields[0])
        # You have 3 csv files. Format == gid, gname.ext, aif
        if len(csv_fields) == 3:
            gname = csv_fields[1]
            aif   = csv_fields[2].lower() in ['true', '1']  # convert to bool correctly
        # You have 4 csv fields. Format == gid, gname, ext, aif
        if len(csv_fields) == 4:
            gname = '.'.join(csv_fields[1:3])
            aif   =  csv_fields[3].lower() in ['true', '1']
        add_image(gname, aif, gid)
    nTableImgs = len(gx2_gname)
    fromTableNames = set(gx2_gname)
    if VERBOSE_LOAD_DATA:
        print('[ld2] * table specified %r images' % nTableImgs)
        # </LEGACY CODE>
        # Load Image Directory
        print('[ld2] * Loading image directory: %r' % img_dir)
    nDirImgs = 0
    nDirImgsAlready = 0
    for fname in os.listdir(img_dir):
        if len(fname) > 4 and fname[-4:].lower() in ['.jpg', '.png', '.tiff']:
            if fname in fromTableNames:
                nDirImgsAlready += 1
                continue
            add_image(fname, False, None)
            nDirImgs += 1
    if VERBOSE_LOAD_DATA:
        print('[ld2] * dir specified %r images' % nDirImgs)
        print('[ld2] * %r were already specified in the table' % nDirImgsAlready)
        print('[ld2] * Loaded %r images' % len(gx2_gname))
        print('[ld2] * Done loading images')
except IOError as ex:
    print('IOError: %r' % ex)
    print('[ld2.img] loading without image table')
    #raise
except Exception as ex:
    print('[ld2!.img] ERROR %r' % ex)
    #print('[ld2.img] ERROR image_tbl parsing: %s' % (''.join(cid_lines)))
    print('[ld2!.img] ERROR on line number:  %r' % (line_num))
    print('[ld2!.img] ERROR on line:         %r' % (csv_line))
    print('[ld2!.img] ERROR on fields:       %r' % (csv_fields))
    raise
    
#%%
header_csvformat_re = '# *ChipID,'
IS_VERSION_1_OR_2 = False
chip_csv_format = ['ChipID', 'ImgID',  'NameID',   'roi[tl_x  tl_y  w  h]',  'theta']
header_numdata = '# NumData '
v12_csv_format = ['instance_id', 'image_id', 'name_id', 'roi']
db_version = 'current'

try:
     # ------------------
     # --- READ CHIPS ---
     # ------------------
     print('[ld2] Loading chip table: %r' % chip_table)
     # Load Chip Table Header
     cid_lines = open(chip_table, 'r').readlines()
     num_data   = -1
     # Parse Chip Table Header
     for line_num, csv_line in enumerate(cid_lines):
         #print('[LINE %4d] %r' % (line_num, csv_line))
         csv_line = csv_line.strip('\n\r\t ')
         if len(csv_line) == 0:
             #print('[LINE %4d] BROKEN' % (line_num))
             continue
         csv_line = csv_line.strip('\n')
         if csv_line.find('#') != 0:
             #print('[LINE %4d] BROKEN' % (line_num))
             break  # Break after header
         if re.search(header_csvformat_re, csv_line) is not None:
             #print('[LINE %4d] SEARCH' % (line_num))
             # Specified Header Variables
             if IS_VERSION_1_OR_2:
                 #print(csv_line)
                 end_ = csv_line.find('-')
                 if end_ != -1:
                     end_ = end_ - 1
                     #print('end_=%r' % end_)
                     fieldname = csv_line[5:end_]
                 else:
                     fieldname = csv_line[5:]
                 #print(fieldname)
                 chip_csv_format += [fieldname]

             else:
                 chip_csv_format = [_.strip() for _ in csv_line.strip('#').split(',')]
             #print('[ld2] read chip_csv_format: %r' % chip_csv_format)
         if csv_line.find(header_numdata) == 0:
             #print('[LINE %4d] NUM_DATA' % (line_num))
             num_data = int(csv_line.replace(header_numdata, ''))
     if IS_VERSION_1_OR_2 and len(chip_csv_format) == 0:
         chip_csv_format = v12_csv_format
     if VERBOSE_LOAD_DATA:
         print('[ld2] * num_chips: %r' % num_data)
         print('[ld2] * chip_csv_format: %r ' % chip_csv_format)
     #print('[ld2.chip] Header Columns: %s\n    ' % '\n   '.join(chip_csv_format))
     cid_x   = tryindex(chip_csv_format, 'ChipID', 'imgindex', 'instance_id')
     gid_x   = tryindex(chip_csv_format, 'ImgID', 'image_id')
     nid_x   = tryindex(chip_csv_format, 'NameID', 'name_id')
     roi_x   = tryindex(chip_csv_format, 'roi[tl_x  tl_y  w  h]', 'roi')
     theta_x = tryindex(chip_csv_format, 'theta')
     # new fields
     gname_x = tryindex(chip_csv_format, 'Image', 'original_filepath')
     name_x  = tryindex(chip_csv_format, 'Name', 'animal_name')
     required_x = [cid_x, gid_x, gname_x, nid_x, name_x, roi_x, theta_x]
     # Hotspotter Chip Tables
     cx2_cid   = []
     cx2_nx    = []
     cx2_gx    = []
     cx2_roi   = []
     cx2_theta = []
     # x is a csv field index in this context
     # get csv indexes which are unknown properties
     prop_x_list  = np.setdiff1d(range(len(chip_csv_format)), required_x).tolist()
     px2_prop_key = [chip_csv_format[x] for x in prop_x_list]
     prop_dict = {}
     for prop in iter(px2_prop_key):
         prop_dict[prop] = []
     if VERBOSE_LOAD_DATA:
         print('[ld2] * num_user_properties: %r' % (len(prop_dict.keys())))
     # Parse Chip Table
     for line_num, csv_line in enumerate(cid_lines):
         csv_line = csv_line.strip('\n\r\t ')
         if len(csv_line) == 0 or csv_line.find('#') == 0:
             continue
         csv_fields = [_.strip(' ') for _ in csv_line.strip('\n\r ').split(',')]
         #
         # Load Chip ID
         try:
             cid = int(csv_fields[cid_x])
         except ValueError:
             print('[ld2!] cid_x = %r' % cid_x)
             print('[ld2!] csv_fields = %r' % csv_fields)
             print('[ld2!] csv_fields[cid_x] = %r' % csv_fields[cid_x])
             print(chip_csv_format)
             raise
         #
         # Load Chip ROI Info
         if roi_x != -1:
             roi_str = csv_fields[roi_x].strip('[').strip(']')
             roi = [int(round(float(_))) for _ in roi_str.split()]
         #
         # Load Chip theta Info
         if theta_x != -1:
             theta = float(csv_fields[theta_x])
         else:
             theta = 0
         #
         # Load Image ID/X
         if gid_x != -1:
             gid = int(csv_fields[gid_x])
             gx  = gid2_gx[gid]
         elif gname_x != -1:
             gname = csv_fields[gname_x]
             if db_version == 'stripespotter':
                 if not exists(gname):
                     gname = 'img-%07d.jpg' % cid
                     gpath = join(db_dir, 'images', gname)
                     w, h = Image.open(gpath).size
                     roi = [1, 1, w, h]
             try:
                 gx = gx2_gname.index(gname)
             except ValueError:
                 gx = len(gx2_gname)
                 gx2_gname.append(gname)
         #
         # Load Name ID/X
         if nid_x != -1:
             #print('namedbg csv_fields=%r' % csv_fields)
             #print('namedbg nid_x = %r' % nid_x)
             nid = int(csv_fields[nid_x])
             #print('namedbg %r' % nid)
             nx = nid2_nx[nid]
         elif name_x != -1:
             name = csv_fields[name_x]
             try:
                 nx = nx2_name.index(name)
             except ValueError:
                 nx = len(nx2_name)
                 nx2_name.append(name)
         # Append info to cid lists
         cx2_cid.append(cid)
         cx2_gx.append(gx)
         cx2_nx.append(nx)
         cx2_roi.append(roi)
         cx2_theta.append(theta)
         for px, x in enumerate(prop_x_list):
             prop = px2_prop_key[px]
             prop_val = csv_fields[x]
             prop_dict[prop].append(prop_val)
except Exception as ex:
    print('[chip.ld2] ERROR %r' % ex)
    #print('[chip.ld2] ERROR parsing: %s' % (''.join(cid_lines)))
    print('[chip.ld2] ERROR reading header:  %r' % (line_num))
    print('[chip.ld2] ERROR on line number:  %r' % (line_num))
    print('[chip.ld2] ERROR on line:         %r' % (csv_line))
    print('[chip.ld2] ERROR on fields:       %r' % (csv_fields))
    raise

if VERBOSE_LOAD_DATA:
    print('[ld2] * Loaded: %r chips' % (len(cx2_cid)))
    print('[ld2] * Done loading chip table')
    
#%%
hs_tables = ds.HotspotterTables()
hs_tables.init(gx2_gname, gx2_aif,
           nx2_name,
           cx2_cid, cx2_nx, cx2_gx,
           cx2_roi, cx2_theta, prop_dict)

#%%
def make_csv_table(column_labels=None, column_list=[], header='', column_type=None):
    if len(column_list) == 0:
        print('[ld2] No columns')
        return header
    column_len = [len(col) for col in column_list]
    num_data = column_len[0]
    if num_data == 0:
        print('[ld2.make_csv_table()] No data. (header=%r)' % (header,))
        return header
    if any([num_data != clen for clen in column_len]):
        print('[lds] column_labels = %r ' % (column_labels,))
        print('[lds] column_len = %r ' % (column_len,))
        print('[ld2] inconsistent column lengths')
        return header

    if column_type is None:
        column_type = [type(col[0]) for col in column_list]

    csv_rows = []
    csv_rows.append(header)
    csv_rows.append('# NumData %r' % num_data)

    column_maxlen = []
    column_str_list = []

    if column_labels is None:
        column_labels = [''] * len(column_list)

    def _toint(c):
        try:
            if np.isnan(c):
                return 'nan'
        except TypeError as ex:
            print('------')
            print('[ld2] TypeError %r ' % ex)
            print('[ld2] _toint(c) failed')
            print('[ld2] c = %r ' % c)
            print('[ld2] type(c) = %r ' % type(c))
            print('------')
            raise
        return ('%d') % int(c)

    for col, lbl, coltype in iter(zip(column_list, column_labels, column_type)):
        if tools.is_list(coltype):
            col_str  = [str(c).replace(',', ' ').replace('.', '') for c in iter(col)]
        elif tools.is_float(coltype):
            col_str = [('%.2f') % float(c) for c in iter(col)]
        elif tools.is_int(coltype):
            col_str = [_toint(c) for c in iter(col)]
        elif tools.is_str(coltype):
            col_str = [str(c) for c in iter(col)]
        else:
            col_str  = [str(c) for c in iter(col)]
        col_lens = [len(s) for s in iter(col_str)]
        max_len  = max(col_lens)
        max_len  = max(len(lbl), max_len)
        column_maxlen.append(max_len)
        column_str_list.append(col_str)

    _fmtfn = lambda maxlen: ''.join(['%', str(maxlen + 2), 's'])
    fmtstr = ','.join([_fmtfn(maxlen) for maxlen in column_maxlen])
    csv_rows.append('# ' + fmtstr % tuple(column_labels))
    for row in zip(*column_str_list):
        csv_rows.append('  ' + fmtstr % row)

    csv_text = '\n'.join(csv_rows)
    return csv_text

def get_num_chips(hs_tables):
    return len(hs_tables.cx2_cid)

def get_valid_cxs(hs_tables):
    valid_cxs = np.where(hs_tables.cx2_cid > 0)[0]
    return valid_cxs

def get_valid_gxs(hs_tables):
    valid_gxs = np.where(hs_tables.gx2_gname != '')[0]
    return valid_gxs

def get_valid_nxs(hs_tables, unknown=True):
    x = 2 * (not unknown)
    valid_nxs = np.where(hs_tables.nx2_name[x:] != '')[0] + x
    return valid_nxs

def make_chip_csv(hs_tables):
    'returns an chip table csv string'
    valid_cx = get_valid_cxs(hs_tables)

    if len(valid_cx) == 0:
        return ''
    # Valid chip tables
    cx2_cid   = hs_tables.cx2_cid[valid_cx]
    # Use the indexes as ids (FIXME: Just go back to g/n-ids)
    cx2_gx   = hs_tables.cx2_gx[valid_cx] + 1  # FIXME
    cx2_nx   = hs_tables.cx2_nx[valid_cx]   # FIXME
    try:
        cx2_roi = hs_tables.cx2_roi[valid_cx]
    except IndexError as ex:
        # THIS IS VERY WEIRD TO ME.
        # I can use empty indexes in non-shaped arrays
        cx2_roi = np.array([])
    cx2_theta = hs_tables.cx2_theta[valid_cx]
    prop_dict = {propkey: [cx2_propval[cx] for cx in valid_cx]
                 for (propkey, cx2_propval) in hs_tables.prop_dict.items()}
    # Turn the chip indexes into a DOCUMENTED csv table
    header = '# chip table'
    column_labels = ['ChipID', 'ImgID', 'NameID', 'roi[tl_x  tl_y  w  h]', 'theta']
    column_list   = [cx2_cid, cx2_gx, cx2_nx, cx2_roi, cx2_theta]
    column_type   = [int, int, int, list, float]
    if not prop_dict is None:
        for key, val in prop_dict.items():
            column_labels.append(key)
            column_list.append(val)
            column_type.append(str)

    chip_table = make_csv_table(column_labels, column_list, header, column_type)
    return chip_table

def make_image_csv(hs_tables):
    'return an image table csv string'
    valid_gx = get_valid_gxs(hs_tables)

    gx2_gid   = valid_gx + 1  # FIXME
    gx2_gname = hs_tables.gx2_gname[valid_gx]
    try:
        gx2_aif   = hs_tables.gx2_aif[valid_gx]
    except Exception as ex:
        print(ex)
        #gx2_aif = np.zeros(len(gx2_gid), dtype=np.uint32)
    # Make image_table.csv
    header = '# image table'
    column_labels = ['gid', 'gname', 'aif']  # do aif for backwards compatibility
    column_list   = [gx2_gid, gx2_gname, gx2_aif]
    image_table = make_csv_table(column_labels, column_list, header)
    return image_table

def make_name_csv(hs_tables):
    'returns an name table csv string'
    valid_nx = get_valid_nxs(hs_tables)
    nx2_name  = hs_tables.nx2_name[valid_nx]
    # Make name_table.csv
    header = '# name table'
    column_labels = ['nid', 'name']
    column_list   = [valid_nx[2:], nx2_name[2:]]  # dont write ____ for backcomp
    name_table = make_csv_table(column_labels, column_list, header)
    return name_table
#%%
# =============================================================================
# 
# =============================================================================
'Saves the tables to disk'
print('[ld2] Writing csv tables')

# csv strings
chip_table  = make_chip_csv(hs_tables)
image_table = make_image_csv(hs_tables)
name_table  = make_name_csv(hs_tables)
# csv filenames
chip_table_fpath  = join(internal_dir, CHIP_TABLE_FNAME)
name_table_fpath  = join(internal_dir, NAME_TABLE_FNAME)
image_table_fpath = join(internal_dir, IMAGE_TABLE_FNAME)
# write csv files
helpers.write_to(chip_table_fpath, chip_table)
helpers.write_to(name_table_fpath, name_table)
helpers.write_to(image_table_fpath, image_table)

#%%
# =============================================================================
# 
# =============================================================================
img_dir = join(db_dir, RDIR_IMG)

def gx2_gname(hs_tables, gx_input, full=False, prefix=None):
    gx2_gname_ = hs_tables.gx2_gname
    gname_list = [gx2_gname_[gx] for gx in gx_input]
    if full or prefix is not None:
        gname_list = [join(img_dir, gname) for gname in gname_list]
    return gname_list


def compute_uniform_area_chip_sizes(roi_list, sqrt_area=None):
    'Computes a normalized chip size to rescale to'
    if not (sqrt_area is None or sqrt_area <= 0):
        target_area = sqrt_area ** 2

        def _resz(w, h):
            try:
                ht = np.sqrt(target_area * h / w)
                wt = w * ht / h
                return (int(round(wt)), int(round(ht)))
            except Exception:
                msg = '[cc2.2] Your csv tables have an invalid ROI.'
                print(msg)
                warnings.warn(msg)
                return (1, 1)
        chipsz_list = [_resz(float(w), float(h)) for (x, y, w, h) in roi_list]
    else:  # no rescaling
        chipsz_list = [(int(w), int(h)) for (x, y, w, h) in roi_list]
    return chipsz_list

def build_transform(x, y, w, h, w_, h_, theta, homogenous=False):
    sx = (w_ / w)  # ** 2
    sy = (h_ / h)  # ** 2
    cos_ = np.cos(-theta)
    sin_ = np.sin(-theta)
    tx = -(x + (w / 2))
    ty = -(y + (h / 2))
    T1 = np.array([[1, 0, tx],
                   [0, 1, ty],
                   [0, 0, 1]], np.float64)

    S = np.array([[sx, 0,  0],
                  [0, sy,  0],
                  [0,  0,  1]], np.float64)

    R = np.array([[cos_, -sin_, 0],
                  [sin_,  cos_, 0],
                  [   0,     0, 1]], np.float64)

    T2 = np.array([[1, 0, (w_ / 2)],
                   [0, 1, (h_ / 2)],
                   [0, 0, 1]], np.float64)
    M = T2.dot(R.dot(S.dot(T1)))
    #.dot(R)#.dot(S).dot(T2)

    if homogenous:
        transform = M
    else:
        transform = M[0:2, :] / M[2, 2]
        
    return transform


# RCOS TODO: Parametarize interpolation method
INTERPOLATION_TYPES = {
    'nearest': cv2.INTER_NEAREST,
    'linear':  cv2.INTER_LINEAR,
    'area':    cv2.INTER_AREA,
    'cubic':   cv2.INTER_CUBIC,
    'lanczos': cv2.INTER_LANCZOS4
}

cv2_flags = INTERPOLATION_TYPES['lanczos']
cv2_borderMode  = cv2.BORDER_CONSTANT
cv2_warp_kwargs = {'flags': cv2_flags, 'borderMode': cv2_borderMode}

def extract_chip(img_fpath, roi, theta, new_size):
    'Crops chip from image ; Rotates and scales; Converts to grayscale'
    # Read parent image
    #printDBG('[cc2] reading image')
    imgBGR = io.imread(img_fpath)
    #printDBG('[cc2] building transform')
    # Build transformation
    (rx, ry, rw, rh) = roi
    (rw_, rh_) = new_size
    Aff = build_transform(rx, ry, rw, rh, rw_, rh_, theta)
    #printDBG('[cc2] rotate and scale')
    # Rotate and scale
    imgBGR = cv2.warpAffine(imgBGR, Aff, (rw_, rh_), **cv2_warp_kwargs)
    #printDBG('[cc2] return extracted')
    return imgBGR

def compute_chip(img_fpath, chip_fpath, roi, theta, new_size, filter_list, force_gray=False):
    '''Extracts Chip; Applies Filters; Saves as png'''
    #printDBG('[cc2] extracting chip')
    chipBGR = extract_chip(img_fpath, roi, theta, new_size)
    #printDBG('[cc2] extracted chip')
    for func in filter_list:
        #printDBG('[cc2] computing filter: %r' % func)
        chipBGR = func(chipBGR)
    cv2.imwrite(chip_fpath, chipBGR)
    return True

#%%
# =============================================================================
#     
# =============================================================================
cx_list=None
cx_list = get_valid_cxs(hs_tables) if cx_list is None else cx_list
if not np.iterable(cx_list):
    cx_list = [cx_list]
cx_list = np.array(cx_list)  # HACK

try:
    gx_list    = hs_tables.cx2_gx[cx_list]
    cid_list   = hs_tables.cx2_cid[cx_list]
    theta_list = hs_tables.cx2_theta[cx_list]
    roi_list   = hs_tables.cx2_roi[cx_list]
    #gname_list = hs.tables.gx2_gname[gx_list]
except IndexError as ex:
    print(repr(ex))
    print(hs_tables)
    print('cx_list=%r' % (cx_list,))
    raise
# Get ChipConfig Parameters
sqrt_area = 750

#---------------------------
# ___Normalized Chip Args___
#---------------------------
# Full Image Paths: where to extract the chips from
gfpath_list = gx2_gname(hs_tables,gx_list, full=True)
# Chip Paths: where to write extracted chips to
chip_uid = 'sz%r' % sqrt_area
# chip_uid = '_CHIP(sz750)'
chip_uid = '_CHIP(' +chip_uid + ')'

chip_idr = join(internal_dir,'computed','chips')

_cfname_fmt = 'cid%d' + chip_uid + '.png'
_cfpath_fmt = join(chip_idr, _cfname_fmt)
cfpath_list = [_cfpath_fmt  % cid for cid in cid_list]
# Normalized Chip Sizes: ensure chips have about sqrt_area squared pixels
chipsz_list = compute_uniform_area_chip_sizes(roi_list, sqrt_area)

#--------------------------
# EXTRACT AND RESIZE CHIPS
#--------------------------
filter_list = []
pcc_kwargs = {
    'arg_list': [gfpath_list, cfpath_list, roi_list, theta_list, chipsz_list],
    'lazy': not False,
    'num_procs': 8,
    'common_args': [filter_list]
}

# Compute all chips with paramatarized filters
parallel_compute(compute_chip, **pcc_kwargs)

    
