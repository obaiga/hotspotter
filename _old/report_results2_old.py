import drawing_functions2 as df2
import load_data2
from Printable import DynStruct
import subprocess
import params
import helpers
import numpy as np
import textwrap
import os
import sys
from os.path import realpath, join

# reloads this module when I mess with it
def reload_module():
    import imp
    import sys
    imp.reload(sys.modules[__name__])

def printDBG(msg):
    #print(msg)
    pass

'''
Stem Plot of ranks
Output the false matches which score higher than the true matches
the number of ground truth images. The ranks of each. 
The hard pairs
For each Chip: 
    All Good Matches
    All Bad  Matches
Lowest Scoring Correct Matches
Highest Scoring Incorrect Matches
Disparity between the two. 
'''

# exec(helpers.get_exec_src(experiments.run_experiment))
def dump_all(hs, qcx2_res, 
             matrix=True,
             summary=True, 
             problems=True,
             ttbttf=True,
             ranks=True,
             oxford=False):
    if matrix:
        write_matrix_results(hs, qcx2_res, SV=True)
        viz_score_matrix(hs, qcx2_res, SV=True)
    if ranks:
        write_rank_results(hs, qcx2_res, SV=True)
        write_rank_results(hs, qcx2_res, SV=False)
    if oxford:
        write_oxsty_mAP_results(hs, qcx2_res, SV=True)
        write_oxsty_mAP_results(hs, qcx2_res, SV=False)
    if summary:
        plot_summary_visualizations(hs, qcx2_res)
    if problems: 
        dump_problems(hs, qcx2_res)
    if ttbttf: 
        dump_qcx_tt_bt_tf(hs, qcx2_res)

#df2.reset()
#df2.reload_module()

class OrganizedResult(DynStruct):
    def __init__(self):
        super(DynStruct, self).__init__()
        self.qcxs   = []
        self.cxs    = []
        self.scores = []
        self.ranks  = []
    def append(self, qcx, cx, rank, score):
        self.qcxs.append(qcx)
        self.cxs.append(cx)
        self.scores.append(score)
        self.ranks.append(rank)

def compile_results(hs, qcx2_res):
    '''
    Organizes results into a data structure so different "types"
    of results can be visualized
    '''
    SV = True
    true          = OrganizedResult()
    false         = OrganizedResult()
    top_true      = OrganizedResult()
    top_false     = OrganizedResult()
    bot_true      = OrganizedResult()
    problem_true  = OrganizedResult()
    problem_false = OrganizedResult()
    for qcx in hs.test_sample_cx:
        res = qcx2_res[qcx]
        true_tup, false_tup = get_matches_true_and_false(hs, res, SV)
        topx = 0
        last_rank     = -1
        skipped_ranks = set([])
        # Iterate through true matches
        for cx, score, rank in zip(*true_tup):
            true.append(qcx, cx, rank+1, score)
            if rank - last_rank > 1:
                skipped_ranks.add(rank-1)
                problem_true.append(qcx, cx, rank+1, score)
            last_rank = rank
            if topx == 0:
                top_true.append(qcx, cx, rank+1, score)
            topx += 1
        if topx > 1: # only do this if there is a bot
            bot_true.append(qcx, cx, rank+1, score)
        topx = 0
        # Iterate through false matches
        for cx, score, rank in zip(*false_tup):
            false.append(qcx, cx, rank+1, score)
            if rank in skipped_ranks:
                problem_false.append(qcx, cx, rank+1, score)
            if topx == 0:
                top_false.append(qcx, cx, rank+1, score)
            topx += 1
    all_results = DynStruct()
    all_results.true          = true
    all_results.false         = false
    all_results.top_true      = top_true
    all_results.top_false     = top_false
    all_results.bot_true      = bot_true
    all_results.problem_true  = problem_true
    all_results.problem_false = problem_false
    return all_results

def __score_matrix_data(hs, qcx2_res, SV=True):
    cx2_nx = hs.tables.cx2_nx
    # Build name-to-chips dict
    nx2_cxs = {}
    for cx, nx in enumerate(cx2_nx):
        if not nx in nx2_cxs.keys():
            nx2_cxs[nx] = []
        nx2_cxs[nx].append(cx)
    # Sort names by number of chips
    nx_list = nx2_cxs.keys()
    nx_size = []
    for nx in nx_list:
        nx_size.append(len(nx2_cxs[nx]))
    nx_sorted = [x for (y,x) in sorted(zip(nx_size, nx_list))]
    # Build sorted chip list
    cx_sorted = []
    test_cx_set = set(hs.test_sample_cx)
    for nx in iter(nx_sorted):
        cxs = nx2_cxs[nx]
        cx_sorted.extend(sorted(cxs))
    # get matrix data rows
    row_label_cx = []
    row_scores = []
    for qcx in iter(cx_sorted):
        if not qcx in test_cx_set: continue
        res = qcx2_res[qcx]
        cx2_score = res.cx2_score_V if SV else res.cx2_score
        row_label_cx.append(qcx)
        row_scores.append(cx2_score[cx_sorted])
    col_label_cx = cx_sorted
    # convert to numpy matrix array
    score_matrix = np.array(row_scores)
    # Fill diagonal with -1's
    np.fill_diagonal(score_matrix, -np.ones(len(row_label_cx)))
    return score_matrix, col_label_cx, row_label_cx

def find_std_inliers(data, m=2):
    return abs(data - np.mean(data)) < m * np.std(data)

def viz_score_matrix(hs, qcx2_res, SV=True):
    SV = True
    (score_matrix, col_label_cx, row_label_cx) =\
            __score_matrix_data(hs, qcx2_res, SV=True)
    inliers = find_std_inliers(score_matrix)
    max_inlier = score_matrix[inliers].max()
    # Truncate outliers
    score_matrix[score_matrix > max_inlier] = max_inlier
    dim = 0 # None
    score_img = helpers.norm_zero_one(score_matrix, dim=dim)
    df2.imshow(score_img)


def matrix_results(hs, qcx2_res, SV=True):
    # Build nx2_cxs
    cx2_gx = hs.tables.cx2_gx
    gx2_gname = hs.tables.gx2_gname
    def cx2_gname(cx):
        return [os.path.splitext(gname)[0] for gname in gx2_gname[cx2_gx]]
    (score_matrix, col_label_cx, row_label_cx) =\
            __score_matrix_data(hs, qcx2_res, SV=True)
    col_label_gname = cx2_gname(col_label_cx)
    row_label_gname = cx2_gname(row_label_cx)
    timestamp =  helpers.get_timestamp(format='comment')+'\n'
    header = '\n'.join(
        ['# Result score matrix',
         '# Generated on: '+timestamp,
         '# Format: rows separated by newlines, cols separated by commas',
         '# num_queries  / rows = '+repr(len(row_label_gname)),
         '# num_database / cols = '+repr(len(col_label_gname)),
         '# row_labels = '+repr(row_label_gname),
         '# col_labels = '+repr(col_label_gname)])
    row_strings = []
    for row in score_matrix:
        row_str = map(lambda x: '%5.2f' % x, row)
        row_strings.append(', '.join(row_str))
    body = '\n'.join(row_strings)
    matrix_str = '\n'.join([header,body])
    return matrix_str

def stem_plot(hs, qcx2_res):
    all_results = compile_results(hs, qcx2_res)
    true = all_results.true
    SV = True
    SV_aug = ['_SVOFF','_SVon'][SV] #TODO: SV should go into params
    query_uid = params.get_query_uid().strip('_')+SV_aug
    fignum = 9000 + SV*900
    result_dir = hs.dirs.result_dir
    summary_dir = join(result_dir, 'summary_vizualizations')
    helpers.ensurepath(summary_dir)
    # Visualize rankings with the stem plot
    title = 'Rankings Stem Plot\n'+query_uid
    df2.figure(fignum=1+fignum, doclf=True, title=title)
    df2.draw_stems(true.qcxs, true.ranks)
    slice_num = int(np.ceil(np.log10(len(hs.test_sample_cx))))
    df2.set_xticks(hs.test_sample_cx[::slice_num])
    df2.set_xlabel('query chip indeX (qcx)')
    df2.set_ylabel('groundtruth chip ranks')
    df2.save_figure(fpath=join(summary_dir, title))
    #df2.set_yticks(list(seen_ranks))


def dump_problems(hs, qcx2_res):
    all_results = compile_results(hs, qcx2_res)
    top_true = all_results.top_true
    top_false = all_results.top_false
    bot_true = all_results.bot_true
    problem_false = all_results.top_false
    problem_true = all_results.bot_true
    SV = True
    SV_aug = ['_SVOFF','_SVon'][SV] #TODO: SV should go into params
    query_uid = params.get_query_uid().strip('_')+SV_aug
    result_dir = hs.dirs.result_dir
    # Dump problem cases
    problem_true_dump_dir  = join(result_dir, 'problem_true'+query_uid)
    problem_false_dump_dir = join(result_dir, 'problem_false'+query_uid)
    top_true_dump_dir      = join(result_dir, 'top_true'+query_uid)
    bot_true_dump_dir      = join(result_dir, 'bot_true'+query_uid)
    top_false_dump_dir     = join(result_dir, 'top_false'+query_uid)

    dump_matches(hs, problem_true_dump_dir, problem_true, qcx2_res, SV)
    dump_matches(hs, problem_false_dump_dir, problem_false, qcx2_res, SV)
    dump_matches(hs, top_true_dump_dir, top_true, qcx2_res, SV)
    dump_matches(hs, bot_true_dump_dir, bot_true, qcx2_res, SV)
    dump_matches(hs, top_false_dump_dir, top_false, qcx2_res, SV)

def dump_matches(hs, dump_dir, organized_result, qcx2_res, SV):
    helpers.ensurepath(dump_dir)
    cx2_gx = hs.tables.cx2_gx
    gx2_gname = hs.tables.gx2_gname
    # Get lists out of compiled results
    qcx_list   = organized_result.qcxs
    cx_list    = organized_result.cxs
    rank_list  = organized_result.ranks
    score_list = organized_result.scores
    # loop over each query / result of interest
    for qcx, cx, score, rank in zip(qcx_list, cx_list, score_list, rank_list):
        query_gname, _  = os.path.splitext(gx2_gname[cx2_gx[qcx]])
        result_gname, _ = os.path.splitext(gx2_gname[cx2_gx[cx]])
        df2.close_all_figures()
        res = qcx2_res[qcx]
        big_title = 'score=%.2f_rank=%d_q=%s_r=%s' % (score, rank,
                                                      query_gname,
                                                      result_gname)
        df2.show_matches3(res, hs, cx, False, fignum=qcx, plotnum=121)
        df2.show_matches3(res, hs, cx,  True, fignum=qcx, plotnum=122)
        df2.set_figtitle(big_title)
        fig_fpath = join(dump_dir, big_title)
        df2.save_figure(qcx, fig_fpath+'.png')


def plot_summary_visualizations(hs, qcx2_res):
    '''Plots (and outputs data): 
        rank stem plot
        rank histogram '''
    all_results = compile_results(hs, qcx2_res)
    true        = all_results.true
    false       = all_results.false
    top_true    = all_results.top_true
    top_false   = all_results.top_false
    bot_true    = all_results.bot_true

    SV = True
    SV_aug = ['_SVOFF','_SVon'][SV] #TODO: SV should go into params
    query_uid = params.get_query_uid().strip('_')+SV_aug
    fignum = 9000 + SV*900
    result_dir = hs.dirs.result_dir
    summary_dir = join(result_dir, 'summary_vizualizations')
    helpers.ensurepath(summary_dir)

    # Visualize rankings with the stem plot
    title = 'Rankings Stem Plot\n'+query_uid
    fig = df2.figure(fignum=1+fignum, doclf=True, title=title)
    df2.draw_stems(true.qcxs, true.ranks)
    slice_num = int(np.ceil(np.log10(len(hs.test_sample_cx))))
    df2.set_xticks(hs.test_sample_cx[::slice_num])
    df2.set_xlabel('query chip indeX (qcx)')
    df2.set_ylabel('groundtruth chip ranks')
    df2.save(fig, fpath=join(summary_dir, title))
    #df2.set_yticks(list(seen.ranks))

    # Draw true rank histogram
    title = 'True Match Rankings Histogram\n'+query_uid
    df2.figure(fignum=2+fignum, doclf=True, title=title)
    df2.draw_histpdf(true.ranks, label=('P(rank | true match)'))
    df2.set_xlabel('ground truth ranks')
    df2.set_ylabel('frequency')
    df2.legend()
    df2.save_figure(fpath=join(summary_dir, title))

    # Draw true score pdf
    title = 'True Match Score Frequencies\n'+query_uid
    df2.figure(fignum=3+fignum, doclf=True, title=title)
    df2.draw_pdf(true.scores, label=('P(score | true match)'), colorx=0)
    df2.variation_trunctate(true.scores)
    df2.set_xlabel('score')
    df2.set_ylabel('frequency')
    df2.save_figure(fpath=join(summary_dir, title))
    df2.legend()

    # Draw false score pdf
    title = 'False Match Score Frequencies\n'+query_uid
    df2.figure(fignum=4+fignum, doclf=True, title=title)
    df2.draw_pdf(false.scores, label=('P(score | false match)'), colorx=.2)
    #df2.variation_trunctate(false.scores)
    df2.set_xlabel('score')
    df2.set_ylabel('frequency')
    df2.legend()
    df2.save_figure(fpath=join(summary_dir, title))

    # Draw top true score pdf
    title = 'Top True Match Score Frequencies\n'+query_uid
    df2.figure(fignum=5+fignum, doclf=True, title=title)
    df2.draw_pdf(top_true.scores, label=('P(score | top true match)'), colorx=.4)
    df2.set_xlabel('score')
    df2.set_ylabel('frequency')
    df2.legend()
    df2.save_figure(fpath=join(summary_dir, title))

    # Draw bot true score pdf
    title = 'Top True Match Score Frequencies\n'+query_uid
    df2.figure(fignum=6+fignum, doclf=True, title=title)
    df2.draw_pdf(bot_true.scores, label=('P(score | bot true match)'), colorx=.6)
    df2.set_xlabel('score')
    df2.set_ylabel('frequency')
    df2.legend()
    df2.save_figure(fpath=join(summary_dir, title))

    # Draw top false score pdf
    title = 'Top False Match Score Frequencies\n'+query_uid
    df2.figure(fignum=7+fignum, doclf=True, title=title)
    df2.draw_pdf(top_false.scores, label=('P(score | top false match)'), colorx=.9)
    df2.set_xlabel('score')
    df2.set_ylabel('frequency')
    df2.legend()
    df2.save_figure(fpath=join(summary_dir, title))

    # Draw matrix scores 
    title = 'Score Matrix\n'+query_uid
    df2.figure(fignum=8+fignum, doclf=True, title=title)
    viz_score_matrix(hs, qcx2_res, SV=True)
    df2.set_xlabel('database')
    df2.set_ylabel('queries')
    df2.save_figure(fpath=join(summary_dir, title))


# ========================================================
# Driver functions (reports results for entire experiment)
# ========================================================

def write_matrix_results(hs, qcx2_res, SV=True):
    matrix_str = matrix_results(hs, qcx2_res, SV)
    __write_report(hs, matrix_str, 'score_matrix', SV)

def write_rank_results(hs, qcx2_res, SV=True):
    rankres_str = rank_results(hs, qcx2_res, SV)
    __write_report(hs, rankres_str, 'rank', SV)

def write_oxsty_mAP_results(hs, qcx2_res, SV=True):
    oxsty_map_csv = oxsty_mAP_results(hs, qcx2_res, SV)
    __write_report(hs, oxsty_map_csv, 'oxsty-mAP', SV)

def dump_qcx_tt_bt_tf(hs, qcx2_res):
    print(textwrap.dedent('''
    =============================
    Dumping results
    ============================='''))
    dump_dir = join(hs.dirs.result_dir, 'tt_bt_tf')
    helpers.ensurepath(dump_dir)
    if '--vd' in sys.argv:
        helpers.vd(dump_dir)
    for qcx in hs.test_sample_cx:
        df2.close_all_figures()
        res = qcx2_res[qcx]
        visualize_res_tt_bt_tf(hs, res)
        fig_fname = 'ttbttf_qcx' + str(qcx) + '--' + params.get_query_uid() + '.jpg'
        fig_fpath = join(dump_dir, fig_fname)
        print fig_fpath
        df2.save_figure(qcx, fig_fpath)
    df2.close_all_figures()
    return dump_dir

def __write_report(hs, report_str, report_type, SV):
    result_dir    = hs.dirs.result_dir
    timestamp_dir = join(result_dir, 'timestamped_results')
    helpers.ensurepath(timestamp_dir)
    helpers.ensurepath(result_dir)
    timestamp = helpers.get_timestamp()
    query_uid = params.get_query_uid()
    SV_aug = ['_SVOFF_','_SVon_'][SV] #TODO: SV should go into params
    csv_timestamp_fname = report_type+query_uid+SV_aug+timestamp+'.csv'
    csv_timestamp_fpath = join(timestamp_dir, csv_timestamp_fname)
    csv_fname  = report_type+query_uid+SV_aug+'.csv'
    csv_fpath = join(result_dir, csv_fname)
    helpers.write_to(csv_fpath, report_str)
    helpers.write_to(csv_timestamp_fpath, report_str)
    if '--gvim' in sys.argv:
        helpers.gvim(csv_fpath)

def train_zebraness_descriptor(hs, qcx2_res):
    hs.feats.cx2_desc
    pass

def rank_results(hs, qcx2_res, SV):
    'Builds csv files showing the cxs/scores/ranks of the query results'
    cx2_cid  = hs.tables.cx2_cid
    #---
    qcx2_num_groundtruth = np.zeros(len(cx2_cid)) - 100
    #---
    qcx2_top_true_rank   = np.zeros(len(cx2_cid)) - 100
    qcx2_top_true_score  = np.zeros(len(cx2_cid)) - 100
    qcx2_top_true_cx     = np.zeros(len(cx2_cid)) - 100
    #---
    qcx2_bot_true_rank   = np.zeros(len(cx2_cid)) - 100
    qcx2_bot_true_score  = np.zeros(len(cx2_cid)) - 100
    qcx2_bot_true_cx     = np.zeros(len(cx2_cid)) - 100
    #---
    qcx2_top_false_rank   = np.zeros(len(cx2_cid)) - 100
    qcx2_top_false_score  = np.zeros(len(cx2_cid)) - 100
    qcx2_top_false_cx     = np.zeros(len(cx2_cid)) - 100
    #---
    test_sample_cx = hs.test_sample_cx
    db_sample_cx   = hs.database_sample_cx
    for qcx in iter(test_sample_cx):
        res = qcx2_res[qcx]
        cx2_score = res.cx2_score_V if SV else res.cx2_score
        # The score is the sum of the feature scores
        top_cx = np.argsort(cx2_score)[::-1]
        top_score = cx2_score[top_cx]
        # Get true postiive ranks
        true_tup, false_tup = get_matches_true_and_false(hs, res, SV)
        (true_cxs,  true_scores,  true_ranks)  = true_tup
        (false_cxs, false_scores, false_ranks) = false_tup
        nth_true  = lambda n: (true_cxs[n],  true_ranks[n],  true_scores[n])
        nth_false = lambda n: (false_cxs[n], false_ranks[n], false_scores[n])
        # Find statitics about the true positives (and negatives)
        num_groundtruth = len(true_ranks)
        if num_groundtruth == 0:
            tt_cx, tt_r, tt_s = (np.nan, np.nan, np.nan)
            bt_cx, bt_r, bt_s = (np.nan, np.nan, np.nan)
        else:
            tt_cx, tt_r, tt_s = nth_true(0)
            if num_groundtruth == 1:
                # if there is only one ground truth dont report bot
                bt_cx, bt_r, bt_s = (np.nan, np.nan, np.nan)
            else:
                bt_cx, bt_r, bt_s = nth_true(-1)
        tf_cx, tf_r, tf_s = nth_false(0)
        # Append stats to output
        qcx2_num_groundtruth[qcx] = num_groundtruth
        #
        qcx2_top_true_rank[qcx]   = tt_r
        qcx2_top_true_score[qcx]  = tt_s
        qcx2_top_true_cx[qcx]     = tt_cx
        #
        qcx2_bot_true_rank[qcx]   = bt_r
        qcx2_bot_true_score[qcx]  = bt_s
        qcx2_bot_true_cx[qcx]     = bt_cx
        #
        qcx2_top_false_rank[qcx]  = tf_r
        qcx2_top_false_score[qcx] = tf_s
        qcx2_top_false_cx[qcx]    = tf_cx
    # Easy to digest results
    num_chips = len(test_sample_cx)
    num_nonquery = len(np.setdiff1d(db_sample_cx, test_sample_cx))
    num_with_gtruth = (1 - np.isnan(qcx2_top_true_rank[test_sample_cx])).sum()
    num_rank_less5 = (qcx2_top_true_rank[test_sample_cx] < 5).sum()
    num_rank_less1 = (qcx2_top_true_rank[test_sample_cx] < 1).sum()
    # Output ranking results
    # TODO: mAP score
    # Build the experiment csv metadata
    SV_aug = ['_SVOFF_','_SVon_'][SV] #TODO: SV should go into params
    query_uid = params.get_query_uid()+SV_aug
    header = '# Experiment Settings (params.query_uid):'+query_uid+'\n'
    header +=  helpers.get_timestamp(format='comment')+'\n'
    scalar_summary = '# Num Query Chips: %d \n' % num_chips
    scalar_summary += '# Num Query Chips with at least one match: %d \n' % num_with_gtruth
    scalar_summary += '# Num NonQuery Chips: %d \n' % num_nonquery
    scalar_summary += '# Ranks <= 5: %d / %d\n' % (num_rank_less5, num_with_gtruth)
    scalar_summary += '# Ranks <= 1: %d / %d\n\n' % (num_rank_less1, num_with_gtruth)
    header += scalar_summary
    print scalar_summary
    #---
    header += '# Full Parameters: \n' + helpers.indent(params.param_string(),'#') + '\n\n'
    #---
    header += textwrap.dedent('''
    # Rank Result Metadata:
    #   QCX  = Query chip-index
    # QGNAME = Query images name
    # NUMGT  = Num ground truth matches
    #    TT  = top true  
    #    BT  = bottom true
    #    TF  = top false''').strip()
    # Build the experiemnt csv header
    test_sample_gx = hs.tables.cx2_gx[test_sample_cx]
    test_sample_gname = hs.tables.gx2_gname[test_sample_gx]
    test_sample_gname = [g.replace('.jpg','') for g in test_sample_gname]

    column_labels = ['QCX',
                     'NUM GT',
                     'TT CX', 
                     'BT CX', 
                     'TF CX',
                     'TT SCORE',
                     'BT SCORE', 
                     'TF SCORE', 
                     'TT RANK',
                     'BT RANK', 
                     'TF RANK',
                     'QGNAME',
                    ]
    column_list = [
        test_sample_cx, 
        qcx2_num_groundtruth[test_sample_cx],
        qcx2_top_true_cx[test_sample_cx],
        qcx2_bot_true_cx[test_sample_cx],
        qcx2_top_false_cx[test_sample_cx],
        qcx2_top_true_score[test_sample_cx],
        qcx2_bot_true_score[test_sample_cx],
        qcx2_top_false_score[test_sample_cx],
        qcx2_top_true_rank[test_sample_cx],
        qcx2_bot_true_rank[test_sample_cx],
        qcx2_top_false_rank[test_sample_cx],
        test_sample_gname,
    ]
    column_type = [int,
                   int,
                   int,
                   int,
                   int,
                   float, 
                   float, 
                   float,
                   int, 
                   int, 
                   int, 
                   str,
                  ]
    rankres_str = load_data2.make_csv_table(column_labels, column_list, header, column_type)
    return rankres_str

def print_top_qcx_scores(hs, qcx2_res, qcx, view_top=10, SV=False):
    res = qcx2_res[qcx]
    print_top_res_scores(hs, res, view_top, SV)

def print_top_res_scores(hs, res, view_top=10, SV=False):
    qcx = res.qcx
    cx2_score = res.cx2_score_V if SV else res.cx2_score
    lbl = ['(assigned)', '(assigned+V)'][SV]
    cx2_nx     = hs.tables.cx2_nx
    nx2_name   = hs.tables.nx2_name
    qnx        = cx2_nx[qcx]
    other_cx   = hs.get_other_cxs(qcx)
    top_cx     = cx2_score.argsort()[::-1]
    top_scores = cx2_score[top_cx] 
    top_nx     = cx2_nx[top_cx]
    view_top   = min(len(top_scores), np.uint32(view_top))
    print('---------------------------------------')
    print('Inspecting matches of qcx=%d name=%s' % (qcx, nx2_name[qnx]))
    print(' * Matched against %d other chips' % len(cx2_score))
    print(' * Ground truth chip indexes:\n   other_cx=%r' % other_cx)
    print('The ground truth scores '+lbl+' are: ')
    for cx in iter(other_cx):
        score = cx2_score[cx]
        print('--> cx=%4d, score=%6.2f' % (cx, score))
    print('---------------------------------------')
    print(('The top %d chips and scores '+lbl+' are: ') % view_top)
    for topx in xrange(view_top):
        tscore = top_scores[topx]
        tcx    = top_cx[topx]
        if tcx == qcx: continue
        tnx    = cx2_nx[tcx]
        _mark = '-->' if tnx == qnx else '  -'
        print(_mark+' cx=%4d, score=%6.2f' % (tcx, tscore))
    print('---------------------------------------')
    print('---------------------------------------')

# OXFORD STUFF
def oxsty_mAP_results(hs, qcx2_res, SV):
    # Check directorys where ranked lists of images names will be put
    SV_aug = ['_SVOFF_','_SVON_'][SV] #TODO: SV should go into params
    qres_dir  = hs.dirs.qres_dir
    query_uid = params.get_query_uid()
    oxsty_qres_dname = 'oxsty_qres' + query_uid + SV_aug
    oxsty_qres_dpath = join(qres_dir, oxsty_qres_dname)
    helpers.ensure_path(oxsty_qres_dpath)
    # Get the mAP scores using philbins program
    query_mAP_list = []
    query_mAP_cx   = []
    for qcx in (hs.test_sample_cx):
        res = qcx2_res[qcx]
        mAP = get_oxsty_mAP_score_from_res(hs, res, SV, oxsty_qres_dpath)
        query_mAP_list.append(mAP)
        query_mAP_cx.append(qcx)
    # Calculate the total mAP score for the experiemnt
    total_mAP = np.mean(np.array(query_mAP_list))
    # build a CSV file with the results
    header  = '# Oxford Style Map Scores'
    header  = '# total mAP score = %r ' % total_mAP
    header +=  helpers.get_timestamp(format='comment')+'\n'
    header += '# Full Parameters: \n#' + params.param_string().replace('\n','\n#')+'\n\n'
    column_labels = ['QCX', 'mAP']
    column_list   = [query_mAP_cx, query_mAP_list]
    oxsty_map_csv = load_data2.make_csv_table(column_labels, column_list, header)
    return oxsty_map_csv

def get_oxsty_mAP_score_from_res(hs, res, SV, oxsty_qres_dpath):
    # find oxford ground truth directory
    cwd = os.getcwd()
    oxford_gt_dir = join(hs.dirs.db_dir, 'oxford_style_gt')
    # build groundtruth query
    qcx = res.qcx
    qnx = hs.tables.cx2_nx[qcx]
    cx2_oxnum = hs.tables.prop_dict['oxnum']
    qoxnum = cx2_oxnum[qcx]
    qname  = hs.tables.nx2_name[qnx]
    # build ranked list
    cx2_score = res.cx2_score_V if SV else res.cx2_score
    top_cx = cx2_score.argsort()[::-1]
    top_gx = hs.tables.cx2_gx[top_cx]
    top_gname = hs.tables.gx2_gname[top_gx]
    # build mAP args
    ground_truth_query = qname+'_'+qoxnum
    # build ranked list of gnames (remove duplicates)
    seen = set([])
    ranked_list = []
    for gname in iter(top_gname):
        gname_ = gname.replace('.jpg','')
        if not gname_ in seen: 
            seen.add(gname_)
            ranked_list.append(gname_)
    ranked_list2 = [gname.replace('.jpg','') for gname in top_gname]
    # Write the ranked list of images names
    cx_aug = 'qcx_'+str(qcx)
    ranked_list_fname = 'ranked_list_' + cx_aug + ground_truth_query + '.txt'
    ranked_list_fpath = join(oxsty_qres_dpath, ranked_list_fname)
    helpers.write_to(ranked_list_fpath, '\n'.join(ranked_list))
    # execute external mAP code: 
    # ./compute_ap [GROUND_TRUTH] [RANKED_LIST]
    os.chdir(oxford_gt_dir)
    args = ('../compute_ap', ground_truth_query, ranked_list_fpath)
    cmdstr  = ' '.join(args)
    print('Executing: %r ' % cmdstr)
    PIPE = subprocess.PIPE
    proc = subprocess.Popen(args, stdout=PIPE, stderr=PIPE)
    (out, err) = proc.communicate()
    return_code = proc.returncode
    os.chdir(cwd)
    mAP = float(out.strip())
    return mAP

# NEW STUFF
def get_top_matches_cx_and_scores(hs, res, SV):
    cx2_score = res.cx2_score_V if SV else res.cx2_score
    qcx = res.qcx
    # get top chip indexes which were in the database
    db_sample_cx = range(len(cx2_desc)) if hs.database_sample_cx is None \
                               else hs.database_sample_cx
    unfilt_top_cx = np.argsort(cx2_score)[::-1]
    top_cx = np.array(helpers.intersect_ordered(unfilt_top_cx, db_sample_cx))
    top_score = cx2_score[top_cx]
    return top_cx, top_score

def __get_top_matches_true_and_false(hs, res, top_cx, top_score):
    qcx    = res.qcx
    top_nx = hs.tables.cx2_nx[top_cx]
    qnx    = hs.tables.cx2_nx[qcx]
    true_ranks  = np.where(np.logical_and(top_nx == qnx, top_cx != qcx))[0]
    false_ranks = np.where(np.logical_and(top_nx != qnx, top_cx != qcx))[0]
    return true_ranks, false_ranks

def get_matches_true_and_false(hs, res, SV):
    top_cx, top_score = get_top_matches_cx_and_scores(hs, res, SV)
    true_ranks, false_ranks = __get_top_matches_true_and_false(hs, res, top_cx, top_score)
    # Get true score / cx
    true_scores = top_score[true_ranks]
    true_cxs    = top_cx[true_ranks]
    # Get false score / cx
    false_scores = top_score[false_ranks]
    false_cxs    = top_cx[false_ranks]
    # Put them in tuple and return
    true_tup  = (true_cxs, true_scores, true_ranks)
    false_tup = (false_cxs, false_scores, false_ranks)
    return true_tup, false_tup

# OLD STUFF
def get_tt_bt_tf_cxs(hs, res, SV):
    'Returns the top and bottom true positives and top false positive'
    qcx = res.qcx
    true_tup, false_tup = get_matches_true_and_false(hs, res, SV)
    true_cxs,  true_scores,  true_ranks  = true_tup
    false_cxs, false_scores, false_ranks = false_tup
    nth_true = lambda n: (true_cxs[n], true_ranks[n], true_scores[n])
    nth_false = lambda n: (false_cxs[n], false_ranks[n], false_scores[n])
    if len(true_ranks) == 0:
        tt_cx, tt_r, tt_s = (np.nan, np.nan, np.nan)
        bt_cx, bt_r, bt_s = (np.nan, np.nan, np.nan)
    else:
        tt_cx, tt_r, tt_s = nth_true(0)
        bt_cx, bt_r, bt_s = nth_true(-1)
    tf_cx, tf_r, tf_s = nth_false(0)

    titles = ('best True rank='+str(tt_r)+' ',
              'worst True rank='+str(bt_r)+' ',
              'best False rank='+str(tf_r)+' ')
    cxs = (tt_cx, bt_cx, tf_cx)
    return cxs, titles

def visualize_res_tt_bt_tf(hs, res):
    #print('Visualizing result: ')
    #res.printme()
    SV = False
    qcx = res.qcx
    _fn = qcx
    cxs, titles = get_tt_bt_tf_cxs(hs, res, SV)
    df2.show_matches3(res, hs, cxs[0], SV, fignum=_fn, plotnum=231, title_aug=titles[0])
    df2.show_matches3(res, hs, cxs[1], SV, fignum=_fn, plotnum=232, title_aug=titles[1])
    df2.show_matches3(res, hs, cxs[2], SV, fignum=_fn, plotnum=233, title_aug=titles[2])
    SV = True
    cxsV, titlesV = get_tt_bt_tf_cxs(hs, res, SV)
    df2.show_matches3(res, hs, cxsV[0], SV, fignum=_fn, plotnum=234, title_aug=titlesV[0])
    df2.show_matches3(res, hs, cxsV[1], SV, fignum=_fn, plotnum=235, title_aug=titlesV[1])
    df2.show_matches3(res, hs, cxsV[2], SV, fignum=_fn, plotnum=236, title_aug=titlesV[2])
    fig_title = 'fig '+str(_fn)+' -- ' + params.get_query_uid()
    df2.set_figtitle(fig_title)
    #df2.set_figsize(_fn, 1200,675)
    return _fn, fig_title

if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support()
    import match_chips2 as mc2
    import load_data2
    import imp
    #imp.reload(df2)
    #imp.reload(mc2)
    # --- CHOOSE DATABASE --- #
    db_dir = load_data2.DEFAULT
    hs = load_data2.HotSpotter(db_dir)
    qcx2_res = mc2.run_matching(hs)
    df2.close_all_figures()

    def dinspect(qcx, cx=None, SV=True, reset=True):
        df2.reload_module()
        if reset:
            print('reseting')
            df2.reset()
        if cx is None:
            visualize_res_tt_bt_tf(hs, qcx2_res[qcx])
        else: 
            df2.show_matches3(qcx2_res[qcx], hs, cx, fignum=qcx, SV=SV)
        df2.present(wh=(900,600))
    def dinspect2(qcx, cx=None):
        df2.show_all_matches(qcx2_res[qcx])
        df2.present()
    write_rank_results(hs, qcx2_res)
    if '--stem' in sys.argv:
        stem_plot(hs, qcx2_res)
        df2.present()
    if '--summary' in sys.argv:
        plot_summary_visualizations(hs, qcx2_res)
    if '--dump-old' in sys.argv:
        dump_qcx_tt_bt_tf(hs, qcx2_res)
    if '--dump-problems' in sys.argv:
        dump_problems(hs, qcx2_res)
    if '--dump' in sys.argv or '--dump-problems' in sys.argv:
        dump_all(hs, qcx2_res)
    #dinspect(18)

    #except Exception as ex:
        #print(repr(ex))
        #raise

    # Execing df2.present does an IPython aware plt.show()
    exec(df2.present(wh=(900,600)))