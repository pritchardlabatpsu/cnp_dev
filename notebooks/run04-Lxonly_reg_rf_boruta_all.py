# Runs genome-wide inference models given Lx as the features
# the x (number of landmark genes) is provided as the first positional argument

from ceres_infer.session import workflow
from ceres_infer.models import model_infer_ens_custom
import sys
import logging
logging.basicConfig(level=logging.INFO)

Lx = sys.argv[1]  # number of landmark genes

params = {
    # directories
    'outdir_run': f'../out/20.0909 Lx/L{Lx}only_reg_rf_boruta_all/',  # output dir for the run
    'outdir_modtmp': f'../out/20.0909 Lx/L{Lx}only_reg_rf_boruta_all/model_perf/',  # intermediate files for each model
    'indir_dmdata_Q3': '../out/20.0817 proc_data/gene_effect/dm_data.pkl',  # pickled preprocessed DepMap Q3 data
    'indir_dmdata_Q4': '../out/20.0817 proc_data/gene_effect/dm_data_Q4.pkl',  # pickled preprocessed DepMap Q4 data
    'indir_genesets': '../data/gene_sets/',
    'indir_landmarks': f'../out/19.1013 tight cluster/landmarks_n{Lx}_k{Lx}.csv',  # csv file of landmarks [default: None]

    # notes
    'session_notes': f'L{Lx} landmarks only; regression with random forest-boruta; predicting whole-genome',

    # data
    'opt_scale_data': False,  # scale input data True/False
    'opt_scale_data_types': '\[(?:RNA-seq|CN)\]',  # data source types to scale; in regexp
    'model_data_source': ['CERES_Lx'],
    'anlyz_set_topN': 10,  # for analysis set how many of the top features to look at
    'perm_null': 1000,  # number of samples to get build the null distribution, for corr
    'useGene_dependency': False,  # whether to use CERES gene dependency (true) or gene effect (false)
    'scope': 'all',  # scope for which target genes to run on; list of gene names, or 'all', 'differential'

    # model
    'model_name': 'rf',
    'model_params': {'n_estimators': 1000, 'max_depth': 15, 'min_samples_leaf': 5, 'max_features': 'log2'},
    'model_paramsgrid': {},
    'model_pipeline': model_infer_ens_custom,
    'pipeline_params': {'sf_iterThresholds': [], 'sf_topK': 30},
    
    # pipeline
    'parallelize': True,  # parallelize workflow
    'processes': 8,  # number of cpu processes to use
    
    # analysis
    'metric_eval': 'score_test',  # metric in model_results to evaluate, e.g. score_test, score_oob
    'thresholds': {'score_rd10': 0.1,  # score of reduced model - threshold for filtering
                   'recall_rd10': 0.95},  # recall of reduced model - threshold for filtering
    'min_gs_size': 4  # minimum gene set size, to be derived
}

wf = workflow(params)
pipeline = ['load_processed_data', 'infer', 'analyze', 'analyze_filtered', 'derive_genesets']
wf.create_pipe(pipeline)
wf.run_pipe()
