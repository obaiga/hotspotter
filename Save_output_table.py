# -*- coding: utf-8 -*-
"""
Created on Mon Apr 12 16:26:53 2021
@author: obaiga

------------------
Function: Save number of matched keypoints for image pairs 
        & Save image similarity score for image pairs

Query function: Hotspotter 1vs1

Please before running the program, modify Initilization part 
------------------
"""
#%%
import numpy as np
import os 
import pandas as pd
#from collections import Counter
from os.path import join,exists
from os import makedirs

np.set_printoptions(precision = 2)
#%%
# =============================================================================
#  Initialization (User needs to modify the below contens )
# =============================================================================

### New database path
dpath = 'C:\\Users\\95316\\code1\\Snow leopard'
###Database name
new_db = 'left_diff_cats'

#%%
# =============================================================================
#   Initilization
# =============================================================================
db_dir = join(dpath,new_db)
table_dir = join(db_dir,'flat_table.csv')
table = pd.read_csv(table_dir,header=2)
#path = join(db_dir,'table.csv')
#table.to_csv(path,index=0)
#table = pd.read_csv(path,skipinitialspace=True)

img_idx = list(np.array((table['#   ChipID']),dtype=int))
                          
flag = 'vsone'   ## flag = 'vsone' or 'vsmany'
if flag=='vsone':
    pre_file = 'res_yl}@``k]tbl~_%o`_qcid='
    pre_save = 'vsone_'
elif flag =='vsmany':
    pre_file = 'res_w1=@2,y0es`5;[=]_qcid='
    pre_save = 'vsmany_'
    
result_dir = join(db_dir,'_hsdb/computed/query_results')
kpts_dir = join(db_dir,'_hsdb/computed/feats')
chipname = 'cid%d_FEAT(hesaff+sift,0_9001)_CHIP(sz750).npz'

res_dir = join(db_dir,'results')
if not exists(res_dir):
    makedirs(res_dir)
#%%
# =============================================================================
#   Save number of keypoints for each image
# =============================================================================

num_kpts = []
for i_img in img_idx:
    i_chip = ''.join(chipname%i_img)
    i_path = os.path.join(kpts_dir,i_chip)
    try:
        npz = np.load(i_path,mmap_mode=None)
        kpts = npz['arr_0']
        desc = npz['arr_1']
        num_kpts.append(len(kpts))
    except IOError:
        print('Idx:%r'%i_img)


data = np.array([img_idx,num_kpts],dtype=np.int32)
data = data.T
df = pd.DataFrame(data)


sentence = join(res_dir,'Kpts_Hotspotter.xlsx')
df.to_excel(sentence, index=False, header=False)



#%%
# =============================================================================
#   Save number of mathced keypoints for each image 
#   & Image similarity score matrix
# =============================================================================

num = len(img_idx)
score_array = np.zeros([num,num])
matched_kpts_array = np.zeros([num,num])
for i,i_name in enumerate(img_idx):
    file = pre_file+str(i_name)+'.npz'
    try: 
        data = np.load(os.path.join(result_dir,file))
        #__slots__ = ['true_uid', 'qcx', 'query_uid', 'uid', 'title', 'nn_time',
             #'weight_time', 'filt_time', 'build_time', 'verify_time',
             #'cx2_fm', 'cx2_fs', 'cx2_fk', 'cx2_score']
        # print(lis(data.keys()))
        score = data['cx2_score']
        matched_kpts = data['cx2_fm']
        score_array[i,:] = score
        for j,i_matched in enumerate(matched_kpts):
            matched_kpts_array[i,j] = len(i_matched)
    except:
        print(file)

df = pd.DataFrame(score_array)
sentence = join(res_dir,'Image_Similarity_Score_HS.xlsx')
df.to_excel(sentence, index=False, header=False)

df = pd.DataFrame(matched_kpts_array)
sentence = join(res_dir,'Matched_Kpts_HS.xlsx')
df.to_excel(sentence, index=False, header=False)
