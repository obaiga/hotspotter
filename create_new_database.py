# -*- coding: utf-8 -*-
"""
Created on Thu Apr  8 12:14:40 2021
@author: obaiga

------------------
Create own database
Replace Hotspotter function: create new database; add images; add chips; modify ID name
------------------

Please before running the program, modify Initilization part 
'dpath', 'new_db', 'image_dpath'
Now, default 'annotation_dpath' is 'image_dpath'
default chip size is original image size.

If you want to extract ROI, set 'Flag_add_chip_software' = True and 'chip_dpath'
modify function 'Read_ROI_data' based on your ROI formate.

"""
#%%
from __future__ import division, print_function
from os.path import join, expanduser,split, exists
import numpy as np
import xml.dom.minidom as minidom
import sys 
import matplotlib.image as image
import shutil

### from Hotspotter
from hscom import helpers
from hscom import argparse2
from hscom import params
from hscom import fileio as io
from hscom import __common__
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
new_db = 'left_diff_cats'
### Full path: dapth + new_db

### Whether add a new database
Flag_new_db = False
### Whether add new images 
Flag_add_img = False
img_dpath = 'C:\Users\95316\code1\Snow leopard\RepresentativeTests_right_Cat1'


### whether add new chips 
Flag_add_chip = False
Flag_add_chip_software = False     ## True: chip size created by Rectle;
                                 ## False: full orginal image size 
chip_dpath = join(img_dpath,'annotation')
#chip_dpath = 'C:\Users\95316\code1\Snow leopard\RepresentativeTests_right_diff_cats\annotation'
### Chip (read xml files)
seg_class_name = 'Leopard'

### whether add new ID name (only works on already having chips)
Flag_chip_ID = True
#chip_ID_lis = ['Cat'+str(i) for i in range(6)]

chip_ID_lis = ['Cat'+str(i) for i in range(9)]

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
        if helpers.inIPython() or '--cmd' in sys.argv:
            args.nosteal = True
    params.args = args
    # Preload process args
    if args.delete_global:
        io.delete_global_cache()
    return args

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

def open_database(db_dir=None):
    # File -> Open Database
    try:
        # Use the same args in a new (opened) database
        args = params.args
        #args = back.params.args

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

def Read_ROI_data(polygon_dir='', type_name = 'Leopard',Flag_add_chip_software=False):
    if Flag_add_chip_software == True:
        domTree = minidom.parse(polygon_dir)
        root = domTree.documentElement
        for ele in root.getElementsByTagName('size')[0].childNodes:
            if ele.nodeName == 'width':
                width = ele.childNodes[0].nodeValue
            if ele.nodeName == 'height':
                height = ele.childNodes[0].nodeValue
    
        obj_lis = root.getElementsByTagName('name')
        xy = []
        #     for i in range(len(obj_lis)):
        ### only record the bounding box coordinate of the FIRST 'Leopard' object
        if obj_lis[0].childNodes[0].nodeValue == type_name:
            for ele in root.getElementsByTagName('bndbox')[0].childNodes:
                if ele.nodeName != '#text':
                    xy.append(ele.childNodes[0].nodeValue)   ## xy coordinate
        
        ###------- function:[hsgui]-[guitools]-def select_roi():
        xm = int(xy[0])
        xM = int(xy[2])
        ym = int(xy[1])
        yM = int(xy[3])
        xywh = map(int, map(round, (xm, ym, xM - xm, yM - ym)))
        
    else: 
        img = image.imread(polygon_dir)
        [width,height,channel] = img.shape
        xm = int(1)
        xM = int(height)
        ym = int(1)
        yM = int(width)
        xywh = map(int, map(round, (xm, ym, xM - xm, yM - ym)))
        
    roi = np.array(xywh, dtype=np.int32)
    
    return roi

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

if Flag_new_db & 1:
    if exists(db_dir):
        shutil.rmtree(db_dir)

defaultdb = None
preload = False

args = parse_arguments(defaultdb, defaultdb == 'cache')
# --- Build HotSpotter API ---
hs = open_database(db_dir)


#%%
# =============================================================================
#     Initialization -  images  
# =============================================================================   
#-------function: [hsgui]-[guiback]-def import_images_from_dir(back):
if Flag_add_img & 1:
    print('[*back] selected %r' % img_dpath)
    fpath_list = helpers.list_images(img_dpath, fullpath=True)
    hs.add_images(fpath_list)
#        hs.add_templates(img_dpath)
    print('')
        

'''     
#------function def import_images_from_file(back):
# File -> Import Images From File
#hs.add_images(fpath_list)
'''

#%%
# =============================================================================
#     Initialization -  chips
# =============================================================================

if Flag_add_chip & 1:
    #-------function: [hsgui]-[guiback] - def add_chip(back):
    
    gx_lis = hs.get_valid_gxs()
    for gx in gx_lis:
        gname = hs.tables.gx2_gname[gx]
        
        if Flag_add_chip_software & 1:
            cname = gname[:-3] + 'xml'
            cdir = join(chip_dpath,cname)
            roi = Read_ROI_data(cdir,seg_class_name,Flag_add_chip_software)
        else:
            cdir = join(img_dpath,gname)
            roi = Read_ROI_data(cdir,Flag_add_chip_software)
        
        roi = np.array(roi,dtype=np.int32)
        
        cx = hs.add_chip(gx, roi)  # NOQA
#    #    back.select_gx(gx)
        print('')
#%%
# =============================================================================
#     Initialization -  new leopard ID name
# =============================================================================
if Flag_chip_ID == True & 1:
    #----function: [hsgui]-[guiback]- def change_chip_property(back, cid, key, val):
    key = 'name'
    # Table Edit -> Change Chip Property
    cx_lis = hs.get_valid_cxs()
    for cx,val in zip(cx_lis,chip_ID_lis):
        key, val = map(str, (key, val))
        print('[*back] change_chip_property(%r, %r, %r)' % (cx, key, val))
        if key in ['name', 'matching_name']:
            hs.change_name(cx, val)
        else:
            hs.change_property(cx, key, val)
        print('')        
#%%  
# =============================================================================
#     Update database
# =============================================================================        
hs.save_database()

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