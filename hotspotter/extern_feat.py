from __future__ import division, print_function
from hscom import __common__
(print, print_, print_on, print_off,
 rrr, profile) = __common__.init(__name__, '[extern_feat]')
# Standard
import os
import sys
from os.path import dirname, realpath, join, expanduser
# Scientific
import numpy as np
import pdb

OLD_HESAFF = False or '--oldhesaff' in sys.argv
if '--newhesaff' in sys.argv:
    OLD_HESAFF = False


def reload_module():
    import imp
    import sys
    imp.reload(sys.modules[__name__])

EXE_EXT = {'win32': '.exe', 'darwin': '.mac', 'linux2': '.ln'}[sys.platform]

if not '__file__' in vars():
    __file__ = os.path.realpath('extern_feat.py')
EXE_PATH = realpath(dirname(__file__))
if not os.path.exists(EXE_PATH):
    EXE_PATH = realpath('tpl/extern_feat')
if not os.path.exists(EXE_PATH):
    EXE_PATH = realpath('hotspotter/tpl/extern_feat')

HESAFF_EXE = join(EXE_PATH, 'hesaff' + EXE_EXT)
INRIA_EXE  = join(EXE_PATH, 'compute_descriptors' + EXE_EXT)

KPTS_DTYPE = np.float64
DESC_DTYPE = np.uint8


# Get directory to hesaff repo
# ASSUME it lives in ~/code/hesaff
hesaffDir = join(expanduser('~'), 'code/hesaff')
# add it to path for finding modules later
sys.path.append(hesaffDir)

#---------------------------------------
# Define precompute functions
def precompute(rchip_fpath, feat_fpath, dict_args, compute_fn):
    kpts, desc = compute_fn(rchip_fpath, dict_args)
    np.savez(feat_fpath, kpts, desc)
    return kpts, desc


def precompute_hesaff(rchip_fpath, feat_fpath, dict_args):
    return precompute(rchip_fpath, feat_fpath, dict_args, compute_hesaff)


#---------------------------------------
# Work functions which call the external feature detectors
# Helper function to call commands
try:        # NOTE: pyhesaff lives in ~/code/hesaff as of 4/21/17
    from hstpl.extern_feat import pyhesaff
    #import pyhesaff # Replaces line above

    def detect_kpts_new(rchip_fpath, dict_args):
        print('using new')
        #kpts, desc = pyhesaff.detect_kpts(rchip_fpath, **dict_args)
        kpts, desc = pyhesaff.detect_feats(rchip_fpath, **dict_args)    # Replaces line above

        return kpts, desc
    #print('[extern_feat] new hessaff is available')
    print('[extern_feat] got newest hesaff from hesaff repo')
except ImportError as ex:
    #print('[extern_feat] new hessaff is not available: %r' % ex)
    print('[extern_feat] could not import hesaff: %r' % ex)
    if '--strict' in sys.argv:
        raise

try:
    from hstpl.extern_feat import pyhesaffexe

    def detect_kpts_old(rchip_fpath, dict_args):
        print ('using old')
        kpts, desc = pyhesaffexe.detect_kpts(rchip_fpath, **dict_args)
        return kpts, desc
    print('[extern_feat] old hessaff is available')
    OLD_HESAFF = True
except ImportError as ex:
    print('[extern_feat] old hessaff is not available: %r' % ex)
    if '--strict' in sys.argv:
        raise


if OLD_HESAFF:
    detect_kpts = detect_kpts_old
    print('[extern_feat] using: old hessian affine')
    
else:
    detect_kpts = detect_kpts_new
    print('[extern_feat] using: new pyhesaff')


#----
def compute_hesaff(rchip_fpath, dict_args):
    return detect_kpts(rchip_fpath, dict_args)
