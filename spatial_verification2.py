from __future__ import division, print_function
import __builtin__
import sys
from helpers import printWARN, printINFO
import warnings
import cv2
import numpy.linalg as linalg
import numpy as np
import scipy 
import scipy.linalg
import scipy.sparse as sparse
import scipy.sparse.linalg as sparse_linalg
# skimage.transform
# http://stackoverflow.com/questions/11462781/fast-2d-rigid-body-transformations-in-numpy-scipy
# skimage.transform.fast_homography(im, H)
# Toggleable printing
print = __builtin__.print
print_ = sys.stdout.write
def print_on():
    global print, print_
    print =  __builtin__.print
    print_ = sys.stdout.write
def print_off():
    global print, print_
    def print(*args, **kwargs): pass
    def print_(*args, **kwargs): pass

# Dynamic module reloading
def reload_module():
    import imp, sys
    print('[sv2] reloading '+__name__)
    imp.reload(sys.modules[__name__])
rrr = reload_module

SV_DTYPE = np.float64

# Generate 6 degrees of freedom homography transformation
def compute_homog(x1_mn, y1_mn, x2_mn, y2_mn):
    '''Computes homography from normalized (0 to 1) point correspondences
    from 2 --> 1 '''
    num_pts = len(x1_mn)
    Mbynine = np.zeros((2*num_pts,9), dtype=SV_DTYPE)
    for ix in xrange(num_pts): # Loop over inliers
        # Concatinate all 2x9 matrices into an Mx9 matrix
        u2      = x2_mn[ix]
        v2      = y2_mn[ix]
        (d,e,f) = (   -x1_mn[ix],    -y1_mn[ix],  -1)
        (g,h,i) = ( v2*x1_mn[ix],  v2*y1_mn[ix],  v2)
        (j,k,l) = (    x1_mn[ix],     y1_mn[ix],   1)
        (p,q,r) = (-u2*x1_mn[ix], -u2*y1_mn[ix], -u2)
        Mbynine[ix*2]   = (0, 0, 0, d, e, f, g, h, i)
        Mbynine[ix*2+1] = (j, k, l, 0, 0, 0, p, q, r)
    # Solve for the nullspace of the Mbynine
    try:
        (u, s, v) = linalg.svd(Mbynine)
    except MemoryError as ex:
        printWARN('[sv2] Caught MemErr %r during full SVD. Trying sparse SVD.' % (ex))
        MbynineSparse = sparse.lil_matrix(Mbynine)
        (u, s, v) = sparse_linalg.svds(MbynineSparse)
    except linalg.LinAlgError as ex2:
        return np.eye(3)
    # Rearange the nullspace into a homography
    h = v[-1] # v = V.H # (transposed in matlab)
    H = np.vstack( ( h[0:3],  h[3:6],  h[6:9]  ) )
    return H

def calc_diaglen_sqrd(x_m, y_m):
    x_extent_sqrd = (x_m.max() - x_m.min()) ** 2
    y_extent_sqrd = (y_m.max() - y_m.min()) ** 2
    diaglen_sqrd = x_extent_sqrd + y_extent_sqrd
    return diaglen_sqrd

def split_kpts(kpts5xN):
    'breakup keypoints into position and shape'
    _xs   = np.array(kpts5xN[0], dtype=SV_DTYPE)
    _ys   = np.array(kpts5xN[1], dtype=SV_DTYPE)
    _acds = np.array(kpts5xN[2:5], dtype=SV_DTYPE)
    return _xs, _ys, _acds

def normalize_xy_points(x_m, y_m):
    'Returns a transformation to normalize points to mean=0, stddev=1'
    mean_x = x_m.mean() # center of mass
    mean_y = y_m.mean()
    std_x = x_m.std()
    std_y = y_m.std()
    sx = 1.0 / std_x if std_x > 0 else 1  # average xy magnitude
    sy = 1.0 / std_y if std_x > 0 else 1
    T = np.array([(sx, 0, -mean_x * sx),
                  (0, sy, -mean_y * sy),
                  (0,  0,  1)])
    x_norm = (x_m - mean_x) * sx
    y_norm = (y_m - mean_y) * sy
    return x_norm, y_norm, T

def homography_inliers(kpts1, kpts2, fm, 
                       xy_thresh,
                       max_scale,
                       min_scale,
                       diaglen_sqrd=None,
                       min_num_inliers=4,
                       just_affine=False):
    #if len(fm) < min_num_inliers:
        #return None
    # Not enough data
    # Estimate affine correspondence convert to SV_DTYPE
    fx1_m, fx2_m = fm[:, 0], fm[:, 1]
    x1_m, y1_m, acd1_m = split_kpts(kpts1[fx1_m, :].T)
    x2_m, y2_m, acd2_m = split_kpts(kpts2[fx2_m, :].T)
    # Get diagonal length
    if diaglen_sqrd is None:
        diaglen_sqrd = calc_diaglen_sqrd(x2_m, y2_m)
    xy_thresh_sqrd = diaglen_sqrd * xy_thresh
    Aff, aff_inliers = affine_inliers(x1_m, y1_m, acd1_m, fm[:, 0],
                                      x2_m, y2_m, acd2_m, fm[:, 1],
                                      xy_thresh_sqrd, 
                                      max_scale,
                                      min_scale)
    # Cannot find good affine correspondence
    if just_affine:
        #raise Exception('No affine inliers')
        return Aff, aff_inliers
    if len(aff_inliers) < min_num_inliers:
        return None
    # Get corresponding points and shapes
    (x1_ma, y1_ma, acd1_m) = (x1_m[aff_inliers], y1_m[aff_inliers],
                              acd1_m[:,aff_inliers])
    (x2_ma, y2_ma, acd2_m) = (x2_m[aff_inliers], y2_m[aff_inliers],
                              acd2_m[:,aff_inliers])
    # Normalize affine inliers
    x1_mn, y1_mn, T1 = normalize_xy_points(x1_ma, y1_ma)
    x2_mn, y2_mn, T2 = normalize_xy_points(x2_ma, y2_ma)
    # Compute homgraphy transform from 1-->2 using affine inliers
    H_prime = compute_homog(x1_mn, y1_mn, x2_mn, y2_mn)
    try: 
        # Computes ax = b # x = linalg.solve(a, b)
        H = linalg.solve(T2, H_prime).dot(T1) # Unnormalize
    except linalg.LinAlgError as ex:
        printWARN('[sv2] Warning 285 '+repr(ex), )
        #raise
        return None

    ((H11, H12, H13),
     (H21, H22, H23),
     (H31, H32, H33)) = H
    # Transform all xy1 matches to xy2 space
    x1_mt = H11*(x1_m) + H12*(y1_m) + H13
    y1_mt = H21*(x1_m) + H22*(y1_m) + H23
    z1_mt = H31*(x1_m) + H32*(y1_m) + H33
    # --- Find (Squared) Distance Error ---
    #scale_err = np.abs(np.linalg.det(H)) * det2_m / det1_m 
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        xy_err = (x1_mt/z1_mt - x2_m)**2 + (y1_mt/z1_mt - y2_m)**2 
    # Estimate final inliers
    inliers = np.where(xy_err < xy_thresh_sqrd)[0]
    return H, inliers
'''
fx1_m  = np.array( (1, 2, 3, 4, 5))
x1_m   = np.array( (1, 2, 1, 4, 5))
y1_m   = np.array( (1, 2, 1, 4, 5))
acd1_m = np.array(((1, 1, 1, 1, 1),
                   (0, 0, 0, 0, 0),
                   (1, 1, 1, 1, 1)))

fx2_m  = np.array( (1, 2, 3, 2, 5))
x2_m   = np.array( (1, 2, 1, 4, 5))
y2_m   = np.array( (1, 2, 1, 4, 5))
acd2_m = np.array(((1, 1, 1, 1, 1),
                   (0, 0, 0, 0, 0),
                   (1, 1, 1, 1, 1)))

acd1_m = array([[ 105.65855929,   69.88258445,   50.26711542,   47.0972872, 37.77338979,
                  80.37862456,   65.7670833 ,   52.42491175, 47.73791486,  47.73791486],
                  [  40.25470409,   33.37290799,  -14.38396778,    5.09841855, 8.36304015,  
                  9.40799471,   -0.22772558,   21.09104681, 33.6183116 ,   33.6183116 ],
                  [  85.21461723,   38.1541563 ,   49.27567372,   19.63477339, 24.12673413,  
                  34.08558994,   35.23499677,   19.37915367, 29.8612585 ,   29.8612585 ]])

acd2_m = array([[ 27.18315876,  40.44774347,  18.83472822,  46.03951988, 25.48597903,
                42.33150267,  34.53070584,  45.37374314, 42.9485725 ,  53.62149774],
                [ 11.08605802,  -7.47303884,  -9.39089399,  -6.87968738, 0.61334048,  
                15.89417442, -38.28506581,   5.9434218 , 25.10330357,  28.30194991],
                [ 14.73551714,  16.44658993,  33.51034403,  19.36112975, 39.17426044, 
                31.73842067,  27.55071888,  21.49176377, 21.40969283,  23.89992898]])

ai = acd1_m[0][0]
ci = acd1_m[1][0]
di = acd1_m[2][0]

aj = acd2_m[0][0]
cj = acd2_m[1][0]
dj = acd2_m[2][0]

Ai = np.array([[ai,0],[ci,di]])
Aj = np.array([[aj,0],[cj,dj]])

Ah = np.array([(ai, 0, 0),(ci, di, 0), (0,0,1)])
'''
#---
# Ensure that a feature doesn't have multiple assignments
# --------------------------------
# Linear algebra functions on lower triangular matrices
def det_acd(acd):
    'Lower triangular determinant'
    return acd[0] * acd[2]
def inv_acd(acd, det):
    'Lower triangular inverse'
    return np.array((acd[2], -acd[1], acd[0])) / det
def dot_acd(acd1, acd2): 
    'Lower triangular dot product'
    a = (acd1[0] * acd2[0])
    c = (acd1[1] * acd2[0]) + (acd1[2] * acd2[1])
    d = (acd1[2] * acd2[2])
    return np.array((a, c, d))
# --------------------------------
def affine_inliers(x1_m, y1_m, acd1_m, fx1_m,
                   x2_m, y2_m, acd2_m, fx2_m,
                   xy_thresh_sqrd, 
                   max_scale, min_scale):
    '''Estimates inliers deterministically using elliptical shapes
    1_m = img1_matches; 2_m = img2_matches
    x and y are locations, acd are the elliptical shapes. 
    fx are the original feature indexes (used for making sure 1 keypoint isn't assigned to 2)

    FROM PERDOCH 2009: 
        H = inv(Aj).dot(Rj.T).dot(Ri).dot(Ai)
        H = inv(Aj).dot(Ai)
        The input acd's are assumed to be 
        invA = ([a 0],[c d])

    REMEMBER our acd is actually inv(acd)
    We transform from 1->2
    '''
    #print(repr((acd1_m.T[0:10]).T))
    #print(repr((acd2_m.T[0:10]).T))
    #with helpers.Timer('enume all'):
    #fx1_uq, fx1_ui = np.unique(fx1_m, return_inverse=True)
    #fx2_uq, fx2_ui = np.unique(fx2_m, return_inverse=True)
    best_inliers = []
    num_best_inliers = 0
    best_mx  = None
    # Get keypoint scales (determinant)
    det1_m = det_acd(acd1_m)
    det2_m = det_acd(acd2_m)
    # Compute all transforms from kpts1 to kpts2 (enumerate all hypothesis)
    # HACK: Because what I thought was A is actually invA,  need to invert calculation
    #inv2_m = inv_acd(acd2_m, det2_m)
    inv1_m = inv_acd(acd1_m, det1_m)
    # The transform from kp1 to kp2 is given as:
    # A = inv(A2).dot(A1)
    # HACK: Because what I thought was A is actually invA,  need to invert calculation
    #Aff_list = dot_acd(inv2_m, acd1_m)
    Aff_list = dot_acd(acd2_m, inv1_m)
    # Compute scale change of all transformations 
    detAff_list = det_acd(Aff_list)
    # Test all hypothesis
    for mx in xrange(len(x1_m)):
        # --- Get the mth hypothesis ---
        Aa = Aff_list[0, mx]
        Ac = Aff_list[1, mx]
        Ad = Aff_list[2, mx]
        Adet = detAff_list[mx]
        x1_hypo = x1_m[mx]
        y1_hypo = y1_m[mx]
        x2_hypo = x2_m[mx]
        y2_hypo = y2_m[mx]
        # --- Transform from xy1 to xy2 ---
        x1_mt   = x2_hypo + Aa*(x1_m - x1_hypo)
        y1_mt   = y2_hypo + Ac*(x1_m - x1_hypo) + Ad*(y1_m - y1_hypo)
        # --- Find (Squared) Distance Error ---
        xy_err    = (x1_mt - x2_m)**2 + (y1_mt - y2_m)**2 
        # --- Find (Squared) Scale Error ---
        #scale_err = Adet * det2_m / det1_m 
        scale_err = Adet * det1_m / det2_m 
        # --- Determine Inliers ---
        xy_inliers_flag = xy_err < xy_thresh_sqrd 
        scale_inliers_flag = np.logical_and(scale_err > min_scale,
                                            scale_err < max_scale)
        hypo_inliers_flag = np.logical_and(xy_inliers_flag, scale_inliers_flag)
        #---
        #---------------------------------
        # TODO: More sophisticated scoring
        # Currently I'm using the number of inliers as a transformations'
        # goodness. Also the way I'm accoutning for multiple assignment
        # does not take into account any error reporting
        #---------------------------------
        '''
        unique_assigned1 = flag_unique(fx1_ui[hypo_inliers_flag])
        unique_assigned2 = flag_unique(fx2_ui[hypo_inliers_flag])
        unique_assigned_flag = np.logical_and(unique_assigned1,
                                              unique_assigned2)
        hypo_inliers = np.where(hypo_inliers_flag)[0][unique_assigned_flag]
        '''
        hypo_inliers = np.where(hypo_inliers_flag)[0]
        
        #---
        # Try to not double count inlier matches that are counted twice
        # probably need something a little bit more robust here.
        unique_hypo_inliers = np.unique(fx1_m[hypo_inliers])
        num_hypo_inliers = len(unique_hypo_inliers)
        # --- Update Best Inliers ---
        if num_hypo_inliers > num_best_inliers:
            best_mx = mx 
            best_inliers = hypo_inliers
            num_best_inliers = num_hypo_inliers
    if not best_mx is None: 
        (Aa, Ac, Ad) = Aff_list[:, best_mx]
        (x1, y1, x2, y2) = (x1_m[best_mx], y1_m[best_mx],
                            x2_m[best_mx], y2_m[best_mx])
        best_Aff = np.array([(Aa,  0,  x2-Aa*x1      ),
                             (Ac, Ad,  y2-Ac*x1-Ad*y1),
                             ( 0,  0,               1)])
    else: 
        best_Aff = np.eye(3)
    return best_Aff, best_inliers

def show_inliers(hs, qcx, cx, inliers, title='inliers', **kwargs):
    import load_data2 as ld2
    df2.show_matches2(rchip1, rchip2, kpts1, kpts2, fm[inliers], title=title, **kwargs_)

def test():
    import load_data2 as ld2
    import params
    import investigate_chip as ic2
    import match_chips3 as mc3
    import spatial_verification2 as sv2
    xy_thresh         = params.__XY_THRESH__
    max_scale = params.__SCALE_THRESH_HIGH__
    min_scale  = params.__SCALE_THRESH_LOW__
    qcx = helpers.get_arg_after('--qcx', type_=int, default=0)
    cx  = helpers.get_arg_after('--cx', type_=int)
    #cx  = 113
    if not 'hs' in vars():
        main_locals = ic2.main()
        exec(helpers.execstr_dict(main_locals, 'main_locals'))
        cx = hs.get_other_cxs(qcx)[0]
        res = mc3.query_groundtruth(hs, qcx, sv_on=False)
        fm = res.cx2_fm[cx]
        fs = res.cx2_fs[cx]
        score = res.cx2_score[cx]
        rchip1 = hs.get_chip(qcx)
        rchip2 = hs.get_chip(cx)
        # Get keypoints
        kpts1 = hs.get_kpts(qcx)
        kpts2 = hs.get_kpts(cx)
    args_ = [rchip1, rchip2, kpts1, kpts2]
    diaglen_srd= rchip2.shape[0]**2 + rchip2.shape[1]**2
    #with helpers.Timer('Computing inliers: '):
    H, inliers, Aff, aff_inliers = sv2.homography_inliers(kpts1, kpts2, fm,
                                                          xy_thresh,
                                                          max_scale,
                                                          min_scale,
                                                          diaglen_sqrd=diaglen_srd,
                                                          min_num_inliers=4,
                                                         just_affine=False)
    df2.show_matches2(*args_+[fm], fs=None,
                      all_kpts=False, draw_lines=True,
                      doclf=True, title='Assigned matches', plotnum=(1,3,1))

    df2.show_matches2(*args_+[fm[aff_inliers]], fs=None,
                      all_kpts=False, draw_lines=True, doclf=True,
                      title='Affine inliers', plotnum=(1,3,2))

    df2.show_matches2(*args_+[fm[aff_inliers]], fs=None,
                      all_kpts=False, draw_lines=True, doclf=True,
                      title='Homography inliers', plotnum=(1,3,3))

def test2(qcx, cx):
    import load_data2 as ld2
    import spatial_verification2 as sv2
    xy_thresh         = params.__XY_THRESH__
    max_scale = params.__SCALE_THRESH_HIGH__
    min_scale  = params.__SCALE_THRESH_LOW__
    qcx = 27
    cx  = 113
    with helpers.RedirectStdout():
        if not 'hs' in vars():
            (hs, qcx, cx, fm, fs, rchip1, rchip2, kpts1, kpts2) = ld2.get_sv_test_data(qcx, cx)
    args_ = [rchip1, rchip2, kpts1, kpts2]

    with helpers.Timer('Computing inliers: '+str(qcx)+' '+str(cx)):
        H, inliers, Aff, aff_inliers = sv2.homography_inliers(kpts1, kpts2, fm, 
                                                              xy_thresh,
                                                              max_scale,
                                                              min_scale,
                                                              min_num_inliers=4)

if __name__ == '__main__':
    import multiprocessing
    multiprocessing.freeze_support()
    import draw_func2 as df2
    import params
    import helpers
    import sys
    mp.freeze_support()
    print('[sc2] __main__ = spatial_verification2.py')
    test()
    exec(df2.present())
