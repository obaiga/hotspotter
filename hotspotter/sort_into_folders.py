''' Copies images into seperate folders based on HotSpotter output
    Written by Ross Hartley
    1/29/18
    Updated on: 2/13/2018
'''

import os
from os.path import exists, join, split, relpath
import shutil
from shutil import copy
import csv
from collections import OrderedDict

def sort_into_folders(hs):
    name_path = join(hs.dirs.internal_dir, "cluster_table.csv")
    dest_path = join(hs.dirs.db_dir, "Sorted_Images")
    img_path = hs.dirs.img_dir


    # TODO:
    #   Put some images into the "Unkown" folder
    #   TL;DR- This code needs to be integrated with HotSpotter, have the API call it and whatnot.

    if(not exists(name_path)):
        print('[hs.sort_images] Clustering has not been completed, cannot sort images.')
    else:
        # If the "Sorted_Images" folder doesn't exist, create it
        if(not exists(dest_path)):
            os.mkdir(dest_path)
        else:
            # If the "Sorted_Images" folder does exist, delete it & its contents,
            #   then remake it
            shutil.rmtree(dest_path)
            os.mkdir(dest_path)
        # Once "Sorted Images" has been created, start parsing
        #  through "cluster_table.csv"
        with open(name_path, 'r') as names:
            #reader = csv.reader(names)
            #next(reader)
            #next(reader)
            reader = csv.DictReader(names)
            keys = reader.fieldnames
            r =  csv.reader(names)
            idDictList = [OrderedDict(zip(keys, row)) for row in r]
            sortedIDlist = sorted(idDictList, key=lambda k: k['Image Name'])
            prevgname = ''
            prevID = ''
            # Next, walk through sortedIDlist and see if an image is matched
            #   with multiple cats, and change it's Cat ID to 'Unknown' if so.
            for index in range(len(sortedIDlist)):
                newgname = sortedIDlist[index]['Image Name']
                newID = sortedIDlist[index]['Cat ID']
                if(newgname == prevgname):
                    print("[sif] %(new)s == %(prev)s" % {"new": newID, "prev": prevID})
                    if(newID != prevID):
                        print("[sif] Found an image with two or more IDs")
                        sortedIDlist[index - 1]['Cat ID'] = 'Unknown'
                        sortedIDlist[index]['Cat ID'] = 'Unknown'
                prevID = newID
                prevgname = newgname
        for row in sortedIDlist:
            print(row["Cat ID"])
            # Make a path for the specific destingation
            sp_dest = join(dest_path, row["Cat ID"])
            # Find path for the original image
            sp_src = join(img_path, row["Image Name"])
            # If the row contains a cat which doesn't have a folder, make it one
            if(not(os.path.isdir(sp_dest))):
                os.mkdir(sp_dest)
                print('[hs.sort_images] Made a directory named %r' % sp_dest)
            # Copy image to correct folder
            copy(sp_src,sp_dest)
            print('[hs.sort_images] Copied %(src)s to %(dst)r' % {"src": sp_src, "dst": sp_dest})
        print('[hs.sort_images] Done sorting images')
        if(exists(dest_path)):
            print('[hs.sort_images] Sorted images are located in: %r' % dest_path)
