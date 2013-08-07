import sys
import fnmatch
from os.path import join, relpath
import collections
import helpers
import load_data2
import numpy as np
import os
import parse
from PIL import Image

# what I think needs to be done:
# all images become chips
# just read the query images
# use philbins thing to compute ap

# It looks like images can have multiple labels. 
# in oxford its either 5 of the same or 10 of two. 

def __oxgtfile2_oxsty_gttup(gt_fname):
    # num is an id not a number of chips
    '''parases the groundtruth filename for: groundtruth name, quality_lbl, and num'''
    gt_format = '{}_{:d}_{:D}.txt'
    name, num, quality = parse.parse(gt_format, gt_fname)
    return (name, num, quality)

def __read_oxsty_gtfile(gt_fpath, name, quality, img_dpath, corrupted_gname_set):
    oxsty_chip_info_list = []
    # read the individual ground truth file
    with open(gt_fpath,'r') as file:
        line_list = file.read().splitlines()
        for line in line_list:
            if line == '': continue
            fields = line.split(' ')
            gname = fields[0].replace('oxc1_','')+'.jpg'
            # >:( Because PARIS just cant keep paths consistent
            if gname.find('paris_') >= 0: 
                paris_hack = gname[6:gname.rfind('_')]
                gname = join(paris_hack, gname)
            if gname in corrupted_gname_set: continue
            if len(fields) > 1: # if has roi
                roi =  map(int, map(round, map(float, fields[1:])))
            else: 
                gpath = os.path.join(img_dpath, gname)
                (w,h) = Image.open(gpath).size
                roi = [0,0,w,h]
            oxsty_chip_info = (gname, roi)
            oxsty_chip_info_list.append(oxsty_chip_info)
    return oxsty_chip_info_list

def matches_image(fname):
    fname_ = fname.lower()
    return any([fnmatch.fnmatch(fname_, pat) for pat in ['*.jpg', '*.png']])

#db_dir = load_data2.PARIS
db_dir = load_data2.OXFORD
def convert_from_oxford_style(db_dir):
    # Get directories for the oxford groundtruth
    oxford_gt_dpath      = join(db_dir, 'oxford_style_gt')
    # Check for corrupted files (Looking at your Paris Buildings Dataset)
    corrupted_file_fpath = join(oxford_gt_dpath, 'corrupted_files.txt')
    corrupted_gname_set = set([])
    if helpers.checkpath(corrupted_file_fpath):
        with open(corrupted_file_fpath) as f:
            corrupted_gname_list = f.read().splitlines()
        corrupted_gname_set = set(corrupted_gname_list)

    # Recursively get relative path of all files in img_dpath
    print('Loading Oxford Style Images from: '+db_dir)
    img_dpath  = join(db_dir, 'images')
    gname_list_ = [join(relpath(root, img_dpath), fname).replace('\\','/').replace('./','')\
                    for (root,dlist,flist) in os.walk(img_dpath)
                    for fname in iter(flist)]
    gname_list = [gname for gname in iter(gname_list_) 
                  if not gname in corrupted_gname_set and matches_image(gname)]
    print(' * num_images = %d ' % len(gname_list))

    # Read the Oxford Style Groundtruth files
    print('Loading Oxford Style Names and Chips')
    gt_fname_list = os.listdir(oxford_gt_dpath)
    num_gt_files = len(gt_fname_list)
    query_chips  = []
    gname2_chips_raw = collections.defaultdict(list)

    name_set = set([])
    print(' * num_gt_files = %d ' % num_gt_files)
    sys.stdout.write('parsed: 0000/%4d' % (num_gt_files))
    for gtx, gt_fname in enumerate(gt_fname_list):
        sys.stdout.write(('\b'*9)+'%4d/%4d' % (gtx+1, num_gt_files))
        if gtx % 10 - 1 == 0: sys.stdout.flush()
        if gt_fname == 'corrupted_files.txt': continue
        #Get name, quality, and num from fname
        (name, num, quality) = __oxgtfile2_oxsty_gttup(gt_fname)
        gt_fpath = join(oxford_gt_dpath, gt_fname)
        name_set.add(name)
        oxsty_chip_info_sublist = __read_oxsty_gtfile(gt_fpath, name,
                                                      quality, img_dpath, 
                                                     corrupted_gname_set)
        if quality == 'query':
            for (gname, roi) in iter(oxsty_chip_info_sublist):
                query_chips.append((gname, roi, name, num))
        else:
            for (gname, roi) in iter(oxsty_chip_info_sublist):
                gname2_chips_raw[gname].append((name, roi, quality))
    sys.stdout.write('\n')

    print(' * num_query images = %d ' % len(query_chips))

    # Remove duplicates img.jpg : (*1.txt, *2.txt, ...) -> (*.txt)
    gname2_chips     = collections.defaultdict(list)
    multinamed_gname_list = []
    for gname, val in gname2_chips_raw.iteritems():
        val_repr = map(repr, val)
        unique_reprs = set(val_repr)
        unique_indexes = [val_repr.index(urep) for urep in unique_reprs]
        for ux in unique_indexes:
            gname2_chips[gname].append(val[ux])
        if len(gname2_chips[gname]) > 1:
            multinamed_gname_list.append(gname)

    # print some statistics
    query_gname_list = [tup[0] for tup in query_chips]
    gname_with_groundtruth_list = gname2_chips.keys()

    gname_without_groundtruth_list = np.setdiff1d(gname_list, gname_with_groundtruth_list)
    print(' * num_images = %d ' % len(gname_list))
    print(' * images with groundtruth    = %d ' % len(gname_with_groundtruth_list))
    print(' * images without groundtruth = %d ' % len(gname_without_groundtruth_list))
    print(' * images with multi-groundtruth = %d ' % len(multinamed_gname_list))

    #make sure all queries have ground truth and there are no duplicate queries
    assert len(query_gname_list) == len(np.intersect1d(query_gname_list, gname_with_groundtruth_list))
    assert len(query_gname_list) == len(set(query_gname_list))

    # build hotspotter tables
    print('adding to table: ')
    gx2_gname = gname_list
    nx2_name  = ['____', '____'] + list(name_set)
    nx2_nid   = [1, 1]+range(2,len(name_set)+2)
    gx2_gid   = range(1,len(gx2_gname)+1)

    cx2_cid     = []
    cx2_theta   = []
    cx2_quality = []
    cx2_roi     = []
    cx2_nx      = []
    cx2_gx      = []
    cx2_oxnum   = []
  
    cid = [1] # bad solution to non-local scope problem
    def add_to_hs_tables(gname, name, roi, quality, num=''):
        nx = nx2_name.index(name)
        gx = gx2_gname.index(gname)
        cx2_cid.append(cid[0])
        cx2_roi.append(roi)
        cx2_quality.append(quality)
        cx2_nx.append(nx)
        cx2_gx.append(gx)
        cx2_theta.append(0)
        cx2_oxnum.append(num)
        cid[0] += 1
        sys.stdout.write(('\b'*10)+'cid = %4d' % cid[0])
        
    for gname, roi, name, num in query_chips:
        add_to_hs_tables(gname, name, roi, 'query', num)

    for gname in gname2_chips.keys():
        if len(gname2_chips[gname]) == 1:
            (name, roi, quality) = gname2_chips[gname][0]
            add_to_hs_tables(gname, name, roi, quality)
        else:
            # just take the first name. This is foobar
            names, rois, qualities = zip(*gname2_chips[gname])
            add_to_hs_tables(gname, names[0], rois[0], qualities[0])

    for gname in gname_without_groundtruth_list:
        gpath = os.path.join(img_dpath, gname)
        (w,h) = Image.open(gpath).size
        roi = [0, 0, w, h]
        add_to_hs_tables(gname, '____', roi, 'unknown')

    cx2_nid = np.array(nx2_nid)[cx2_nx]
    cx2_gid = np.array(gx2_gid)[cx2_gx]

    # Make chip_table.csv
    header = '# chip table'
    column_labels = ['ChipID', 'ImgID', 'NameID', 'roi[tl_x  tl_y  w  h]', 'theta', 'oxnum']
    column_list   = [cx2_cid, cx2_gid, cx2_nid, cx2_roi, cx2_theta, cx2_oxnum]
    chip_table = load_data2.make_csv_table(column_labels, column_list, header)

    # Make name_table.csv
    column_labels = ['nid', 'name']
    column_list   = [nx2_nid[2:], nx2_name[2:]] # dont write ____ for backcomp
    header = '# name table'
    name_table = load_data2.make_csv_table(column_labels, column_list, header)

    # Make image_table.csv 
    column_labels = ['gid', 'gname', 'aif'] # do aif for backwards compatibility
    gx2_aif = np.ones(len(gx2_gid), dtype=np.uint32)
    column_list   = [gx2_gid, gx2_gname, gx2_aif]
    header = '# image table'
    image_table = load_data2.make_csv_table(column_labels, column_list, header)

    test_sample_cx  = range(0, len(query_chips))
    train_sample_cx = range(len(query_chips), len(cx2_cid))
    database_sample_cx = range(len(query_chips), len(cx2_cid))

    chip_table_fname  = join(db_dir, '.hs_internals',  'chip_table.csv')
    name_table_fname  = join(db_dir, '.hs_internals',  'name_table.csv')
    image_table_fname = join(db_dir, '.hs_internals', 'image_table.csv')
    
    test_sample_fname     = join(db_dir, '.hs_internals', 'test_sample.txt')
    train_sample_fname    = join(db_dir, '.hs_internals', 'train_sample.txt')
    database_sample_fname = join(db_dir, '.hs_internals', 'database_sample.txt')

    helpers.write_to(chip_table_fname, chip_table)
    helpers.write_to(name_table_fname, name_table)
    helpers.write_to(image_table_fname, image_table)

    helpers.write_to(test_sample_fname,     repr(test_sample_cx))
    helpers.write_to(train_sample_fname,    repr(train_sample_cx))
    helpers.write_to(database_sample_fname, repr(database_sample_cx))

if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support()
    # --- LOAD DATA --- #
    #db_dir = load_data2.OXFORD
    #convert_from_oxford_sytle(db_dir)
    convert_from_oxford_style(load_data2.PARIS)
    convert_from_oxford_style(load_data2.OXFORD)