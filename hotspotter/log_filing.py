''' Saves HotSpotter preferences to a log file and loads parameters from existing log
    Written by Ross Hartley
    2/11/18
'''

import os
from os.path import join, exists
import csv
from hscom.Preferences import Pref
from datetime import datetime
first_write = int(1)
column_labels = ['exclusion_factor', 'stopping_criterion',
    'self_loop_weight', 'same_image_score', 'same_set_boost', 'maximum_time_delta', 'minimum_same_set_weight',
    'inflation_factor', 'maximum_iterations', 'expansion_factor', 'multiplication_factor',
    'autochip_runtime', 'autoquery_runtime', 'clustering_runtime', 'Date/Time']

def add_to_log(hs):
    # Store path to log file
    log_path = join(hs.dirs.internal_dir, "hs_log.csv")
    # Get current parameters
    chip_params = hs.prefs.autochip_cfg
    autoquery_params = hs.prefs.autoquery_cfg
    cluster_params = hs.prefs.cluster_cfg
    # Open log file
    with open(log_path, 'a') as hs_log:
        writer = csv.writer(hs_log)
        # If log file hasn't been written to yet, give each column a label
        if(os.stat(log_path).st_size == 0):
            writer.writerow(column_labels)
        # Once columns have labels, append a row of parameters
        column_list = [[chip_params.exclusion_factor], [chip_params.stopping_criterion],
            [autoquery_params.self_loop_weight], [autoquery_params.same_image_score], [autoquery_params.same_set_boost], [autoquery_params.maximum_time_delta], [autoquery_params.minimum_same_set_weight],
            [cluster_params.inflation_factor], [cluster_params.maximum_iterations], [cluster_params.expansion_factor], [cluster_params.multiplication_factor],
            [hs.getACruntime()], [hs.getAQruntime()], [hs.getMCLruntime()], [str(datetime.now())]]
        writer.writerow(column_list)
'''
def load_from_log(hs):
    # Store path to log file
    log_path = join(hs.dirs.internal_dir, "hs_log.csv")
    # If no log file exists, let user know
    if(not(exists(log_path))):
        print("[log] hs_log.csv doesn't exist yet, cannot load preferences")
    else:
        # If log file was found, proceed to load parameters
        print("[log] hs_log.csv found, loading parameters")
        with open(log_path, 'r') as hs_log:
            reader = csv.DictReader(hs_log)
            for


def isLast(iter):
    old = itr.next()
    for new in itr:
        yield False, old
        old = new
yield True, old
'''
