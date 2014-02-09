from __future__ import division, print_function

vsmany_2 = {
    'query_type':      ['vsmany'],
    'checks':          [1024],  # , 8192],
    'K':               [5],  # 5, 10],
    'Knorm':           [1],  # 2, 3],
    'Krecip':          [0],  # , 5, 10],
    'roidist_weight':  [0],  # 1,]
    'recip_weight':    [0],  # 1,]
    'bursty_weight':   [0],  # 1,]
    'ratio_weight':    [0, 1],  # 1,]
    'lnbnn_weight':    [0, 1],  # 1,]
    'lnrat_weight':    [0, 1],  # 1,]
    'roidist_thresh':  [None],  # .5,]
    'recip_thresh':    [0],  # 0
    'bursty_thresh':   [None],  #
    'ratio_thresh':    [None],  # 1.2, 1.6
    'lnbnn_thresh':    [None],  #
    'lnrat_thresh':    [None],  #
    'nShortlist':      [1000],
    'sv_on':           [True],  # True, False],
    'score_method':    ['csum'],
    'max_alts':        [1000],
}

vsone_1 = {
    'query_type':      ['vsone'],
    'checks':          [256],  # , 8192],
    'K':               [1],  # 5, 10],
    'Knorm':           [1],  # 2, 3],
    'Krecip':          [0],  # , 5, 10],
    'roidist_weight':  [0],  # 1,]
    'recip_weight':    [0],  # 1,]
    'bursty_weight':   [0],  # 1,]
    'ratio_weight':    [1],  # 1,]
    'lnbnn_weight':    [0],  # 1,]
    'lnrat_weight':    [0],  # 1,]
    'roidist_thresh':  [None],  # .5,]
    'recip_thresh':    [0],  # 0
    'bursty_thresh':   [None],  #
    'ratio_thresh':    [1.5],  # 1.2, 1.6
    'lnbnn_thresh':    [None],  #
    'lnrat_thresh':    [None],  #
    'nShortlist':      [1000],
    'sv_on':           [True],  # True, False],
    'score_method':    ['csum'],  # , 'pl'],  #, 'nsum', 'borda', 'topk', 'nunique']
    'max_alts':        [500],
}

vsone_std = {
    'query_type':    'vsone',
    'checks':        256,
    'K':             1,
    'Knorm':         1,
    'Krecip':        0,
    'ratio_weight':  1,
    'lnbnn_weight':  0,
    'ratio_thresh':  1.5,
}

vsmany_scoremethod = {
    'query_type':      ['vsmany'],
    'checks':          [1024],  # , 8192],
    'K':               [5],  # 5, 10],
    'Knorm':           [1],  # 2, 3],
    'Krecip':          [0],  # , 5, 10],
    'roidist_weight':  [0],  # 1,]
    'recip_weight':    [0],  # 1,]
    'bursty_weight':   [0],  # 1,]
    'ratio_weight':    [0],  # 1,]
    'lnbnn_weight':    [1],  # 1,]
    'lnrat_weight':    [0],  # 1,]
    'roidist_thresh':  [None],  # .5,]
    'recip_thresh':    [0],  # 0
    'bursty_thresh':   [None],  #
    'ratio_thresh':    [None],  # 1.2, 1.6
    'lnbnn_thresh':    [None],  #
    'lnrat_thresh':    [None],  #
    'nShortlist':      [1000],
    'sv_on':           [True],  # True, False],
    'score_method':    ['csum', 'pl', 'plw', 'borda'],  # 'bordaw', 'topk', 'topkw'],  # , 'nsum', 'borda', 'topk', 'nunique']
    'max_alts':        [1000],
}

vsmany_best = {
    'query_type':      ['vsmany'],
    'checks':          [1024],  # , 8192],
    'K':               [4],  # 5, 10],
    'Knorm':           [1],  # 2, 3],
    'Krecip':          [0],  # , 5, 10],
    'roidist_weight':  [0],  # 1,]
    'recip_weight':    [0],  # 1,]
    'bursty_weight':   [0],  # 1,]
    'ratio_weight':    [0],  # 1,]
    'lnbnn_weight':    [1],  # 1,]
    'lnrat_weight':    [0],  # 1,]
    'roidist_thresh':  [None],  # .5,]
    'recip_thresh':    [0],  # 0
    'bursty_thresh':   [None],  #
    'ratio_thresh':    [None],  # 1.2, 1.6
    'lnbnn_thresh':    [None],  #
    'lnrat_thresh':    [None],  #
    'xy_thresh':       [.002],
    'nShortlist':      [1000],
    'sv_on':           [True],  # True, False],
    'score_method':    ['csum'],  # 'bordaw', 'topk', 'topkw'],  # , 'nsum', 'borda', 'topk', 'nunique']
    'max_alts':        [1000],
}
best = vsmany_best

overnight = vsmany_best.copy()
overnight.update({
    #'K':                   [5, 7, 10, 20],
    #'Knorm':               [1, 3, 5, 10],
    #'normalizer_rule':     ['name', 'last'],
    #'use_adaptive_scale':  [True, False],
    #'score_method':        ['pl', 'csum'],  # , 'pl'],  #, 'nsum', 'borda', 'topk', 'nunique']
})

overnight_huge = vsmany_best.copy()
overnight_huge.update({
    'K':                   [5, 7, 10, 20],
    'Knorm':               [1, 3, 5],
    'normalizer_rule':     ['name', 'last'],
    'use_adaptive_scale':  [False, True],
    #'scale_min': [0, 10, 20],
    #'score_method':        ['pl', 'csum'],  # , 'pl'],  #, 'nsum', 'borda', 'topk', 'nunique']
})


overnight_k = vsmany_best.copy()
overnight_k.update({
    'K': [1, 3, 5, 7, 10, 20],
    'Knorm': [1, 3, 5, 7, 10],
})

k_small = vsmany_best.copy()
k_small.update({
    'K': [2, 5],
    'Knorm': [1],
})

k_big = vsmany_best.copy()
k_big.update({
    'K': [3, 4, 5, 7, 10, 15],
    'Knorm': [1, 2, 3],
})

adaptive_test = vsmany_best.copy()
adaptive_test.update({
    'K': [4, 5],
    'use_adaptive_scale': [True, False],
})

normrule = vsmany_best.copy()
normrule.update({
    'K': [5, 10, 3],
    'Knorm': [1, 3, 5, 10, 20],
    'normalizer_rule': ['name', 'last'],
})

vsmany_kenya = vsmany_best.copy()
#vsmany_kenya.update({
    #'K': [2, 3, 4, 5],
    #'xy_thresh': [.05, .01, .002, .001],
#})
#vsmany_kenya.update({
    #'xy_thresh': [.01],
    #'lnbnn_weight': [1, .01],
#})

vsmany_kenya.update({
    'scale_min': [10, 20],
    'scale_max': [30, 50],
})


vsmany_score = vsmany_best.copy()
vsmany_score.update({
    'score_method': ['csum', 'pl', 'plw', 'borda', 'bordaw'],
})

vsmany_nosv = vsmany_best.copy()
vsmany_nosv.update({
    'sv_on': [False]
})

vsmany_sv = vsmany_best.copy()
vsmany_sv.update({
    'xy_thresh': [None, .1, .01, .001, .002]
})

vsmany_k = vsmany_best.copy()
vsmany_k.update({
    'K': [2, 5, 10, 30]
})


vsmany_big_social = vsmany_best.copy()
vsmany_big_social.update({
    'K':                [5, 10, 20],
    'Knorm':            [1, 3],
    'Krecip':           [0],
    'lnbnn_weight':     [1],
    'score_method':     ['pl', 'plw', 'csum', 'borda', 'bordaw'],
})


vsmany_1 = {
    'query_type':      ['vsmany'],
    'checks':          [1024],  # , 8192],
    'K':               [5],  # 5, 10],
    'Knorm':           [1],  # 2, 3],
    'Krecip':          [0],  # , 5, 10],
    'roidist_weight':  [0],  # 1,]
    'recip_weight':    [0],  # 1,]
    'bursty_weight':   [0],  # 1,]
    'ratio_weight':    [0],  # 1,]
    'lnbnn_weight':    [1],  # 1,]
    'lnrat_weight':    [0],  # 1,]
    'roidist_thresh':  [None],  # .5,]
    'recip_thresh':    [0],  # 0
    'bursty_thresh':   [None],  #
    'ratio_thresh':    [None],  # 1.2, 1.6
    'lnbnn_thresh':    [None],  #
    'lnrat_thresh':    [None],  #
    'nShortlist':      [1000],
    'sv_on':           [True],  # True, False],
    'score_method':    ['csum'],  # , 'nsum', 'borda', 'topk', 'nunique']
    'max_alts':        [1000],
}
