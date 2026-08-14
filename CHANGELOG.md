# Changelog

## Unreleased

### Algorithmic depth improvements

- Replaced KernelRidge gradient descent with Cholesky decomposition.
  The previous 1000-iteration gradient descent with fixed learning rate
  was unreliable and might not converge. Now solves (K + alpha*I) * x = y
  directly via Cholesky factorization and forward/backward substitution.
- Rewrote NuSVC with proper SMO optimization. The previous implementation
  used fixed-step gradient updates and never updated the bias term. Now
  uses SMO with the nu constraint (sum(y_i * alpha_i) = 0, upper bound
  C/nu), second-order working set selection, and proper bias updates.
  Also detects classes from data instead of hardcoding 0/1.
- Added deflation and convergence checks to manifold power iteration
  (isomap_fit, lle_fit, spectral_embedding_fit). Previously ran 100
  fixed iterations without deflation, so all components found the same
  dominant eigenvector. Now orthogonalizes against previously found
  eigenvectors and breaks on convergence (max change < 1e-6).
- Added convergence check to PLS NIPALS. Previously ran 100 fixed
  iterations. Now breaks when weight vector change drops below 1e-6.

### Bug fixes and depth improvements

- Added multi-class KernelSVC (KernelSVCMulti) via one-vs-rest. Trains
  one binary kernel SVM per class with y_dual set directly (+1/-1),
  avoiding the class-ordering dependency in kernel_svc_fit. Prediction
  uses argmax over decision function scores. Iris accuracy: 1.0.
- Fixed Nystroem eigendecomposition: replaced the incorrect diagonal-only
  eigenvalue approximation with power iteration and deflation. The
  transform now projects through eigenvectors and normalizes by
  sqrt(eigenvalue), matching the standard Nystroem approximation.
- Fixed CalibratedClassifierCV isotonic calibration: the non-Platt
  fallback was a no-op (a=1, b=0). Now runs PAVA on (pred, y) sorted
  by prediction value, then fits a sigmoid to the isotonic curve.
- Fixed AdditiveChi2Sampler transform: the formula was mathematically
  wrong (x * cos(t) / sqrt(x)). Now uses the correct deterministic
  Fourier feature map: cos(t_k * log(x)) / sqrt(x).
- Fixed _rbf_kernel name collision between gaussian_process.flow and
  svm.flow. The Flow compiler only emits one definition when two
  non-exported functions share a name across modules (Flow issue #465).
  Renamed the GP versions to _gp_rbf_kernel, _gp_linear_kernel, _gp_kernel.
- Bumped all struct array allocations from 64 to 128 bytes per element.
  KernelSVC is ~80 bytes and was overflowing at 64. Updated AGENTS.md
  guidance accordingly.
- Fixed CCA dead code: removed `s = s + matrix_at(Xc, i, j) * 0.0`
  line in cross_decomposition.flow that multiplied by zero.
- Fixed factor_analysis_fit: all n_components are now properly
  initialized and stored. Previously only component 0 was stored.
  Covariance is restored at the start of each EM iteration and
  deflated per-component within each iteration.
- Fixed empirical_covariance_get_precision: replaced the incorrect
  diagonal-only approximation with full Gaussian elimination with
  partial pivoting on the augmented [cov | I] matrix.
- Implemented mutual information scoring in select_k_best_fit for
  SCORE_MUTUAL_INFO. Discretizes each feature into 10 bins and
  computes MI between binned features and class labels.
- Implemented missing_indicator_fit to scan data and track which
  features have missing values. The transform now respects the
  features parameter (ALL, MISSING, NON_MISSING). Uses ptr<i32>
  for the has_missing array because Flow silently drops ptr<bool>
  fields from generated C structs.

### Histogram-based Gradient Boosting

- Replaced the simplified HistGradientBoosting implementation (which
  used DecisionTreeRegressor instances) with a proper histogram-based
  tree builder. Features are quantile-binned into at most 256 bins.
  Gradient and hessian histograms are accumulated per feature and node.
  Splits are found by scanning cumulative bin sums with regularized
  gain. Trees are built recursively with a shared node counter to
  avoid struct-by-value issues in Flow.
- Both classifier (logistic loss) and regressor (squared error)
  variants use the new histogram trees.
- Added structs: HistNode, HistTree, BinnedData, HistPair,
  SplitResult, SplitSamplesResult.
- Added helpers: _compute_bin_thresholds, _bin_value, _bin_features,
  _build_hist, _find_best_hist_split, _split_samples,
  _compute_leaf_value, _build_hist_tree, _hist_tree_build_recursive.

### f64 internal precision

- LinearSVC dual coordinate descent now uses f64 for weight
  accumulation, alpha updates, and bias computation. Reduces float
  error on datasets with many features.
- KernelSVC SMO error computation (E_i, E_j) now accumulates in f64.
- LDA digamma approximation now computes in f64.

### Sparse-aware estimators

- Added linear_svc_fit_sparse: trains LinearSVC from a CSR
  SparseMatrix. Only iterates over non-zero entries when computing
  Q_ii, w_dot_x, and weight updates.
- Added logistic_regression_fit_sparse: trains LogisticRegression
  from a CSR SparseMatrix. Gradient accumulation only touches
  non-zero entries.
- Sparse and dense produce identical weights on the same data.

### Multi-class LinearSVC (OVR)

- Added LinearSVCMulti struct and functions:
  linear_svc_multi_fit, linear_svc_multi_predict,
  linear_svc_multi_decision_function, linear_svc_multi_free.
- Trains one binary LinearSVC per class. Prediction uses argmax of
  decision function scores across all binary classifiers.
- Achieves 97.8% accuracy on iris (3 classes).

### Estimator-level save/load

- Added save_linear_svc / load_linear_svc: serializes a fitted
  LinearSVC to a single binary file (n_features, n_classes, bias,
  weights, classes).
- Added save_logistic_regression / load_logistic_regression:
  serializes a fitted LogisticRegression to a single binary file.
- Loaded models produce identical predictions to originals.

### Metrics audit and additions

- Added precision_score, recall_score, f1_score (binary, with
  pos_label parameter).
- Added precision_score_macro, recall_score_macro, f1_score_macro
  (macro-averaged across all classes).
- Fixed r2_score edge case: returns 1.0 when y_true is constant and
  predictions match, matching sklearn behavior.
- Audited accuracy_score, mean_squared_error, mean_absolute_error,
  r2_score, precision_score, recall_score, f1_score against known
  sklearn values. All match.

### Tests added

- tests/test_sparse_estimators.flow: sparse-aware LinearSVC and
  LogisticRegression, weight parity with dense.
- tests/test_multiclass_svm.flow: multi-class OVR LinearSVC on iris.
- tests/test_estimator_persistence.flow: estimator save/load round-trip.
- tests/test_metrics_audit.flow: metric formulas against known values.

### Real load_digits dataset

- Replaced synthetic load_digits (180 samples) with the actual digits
  dataset (1797 samples, 64 features, 10 classes). Real 8x8 pixel
  handwritten digit data from sklearn.datasets.load_digits().

### LARS-Lasso path algorithm

- Replaced coordinate descent in lasso_lars_fit with the actual
  LARS-Lasso algorithm from Efron et al. (2004). Computes the
  equiangular direction via Gaussian elimination on the active set
  Gram matrix. Includes the Lasso modification: removes variables
  from the active set when their coefficients cross zero.
- Linear solver uses f64 internally for numerical stability.
- Added helpers: _solve_linear_system, _gram_active, _centered_dot.

### LinearSVC dual coordinate descent

- Replaced SGD with dual coordinate descent for L2-regularized
  L1-loss SVM (Hsieh et al. 2008, used by liblinear). Solves the
  dual problem with projected gradient updates. Computes bias from
  free support vectors.

### Model persistence

- Added lib/scikit/persistence.flow with binary save/load for
  matrices, arrays, scalars, and integers. Uses C file I/O
  (fopen, fwrite, fread). Functions: save_matrix, load_matrix,
  save_array, load_array, save_scalar, load_scalar, save_int,
  load_int.
- Added tests/test_persistence.flow.

### f64 precision support

- Added f64 array functions to matrix.flow: array_new_f64,
  array_free_f64, array_copy_f64.
- LARS linear solver uses f64 internally for numerical stability.
  More algorithms can be converted to f64 internal precision as
  needed.

### Sparse matrix support

- Added lib/scikit/sparse.flow with CSR (Compressed Sparse Row)
  format. Mirrors scipy.sparse.csr_matrix.
- Functions: sparse_new, sparse_free, sparse_from_dense,
  sparse_to_dense, sparse_at, sparse_dot_row, sparse_dot_dense,
  sparse_density, sparse_nnz_per_row.
- Added tests/test_sparse.flow.

### Improved SMO convergence for KernelSVC

- Implemented proper SMO alternating pass strategy (Platt 1998).
  Alternates between full passes over all samples and non-boundary
  passes over samples with 0 < alpha < C. Non-boundary passes converge
  faster because those samples are more likely to violate KKT
  conditions.
- Convergence now stops when a full pass makes no changes, matching
  sklearn's SMO behavior.

### Real bundled datasets

- Replaced synthetic `load_iris` with the actual iris dataset (150
  samples, 4 features, 3 classes). Real flower measurements from
  sklearn.datasets.load_iris().
- Replaced synthetic `load_wine` with the actual wine dataset (178
  samples, 13 features, 3 classes). Real wine chemical analysis data.
- Replaced synthetic `load_breast_cancer` with the actual breast cancer
  dataset (569 samples, 30 features, 2 classes). Real diagnostic data
  from sklearn.datasets.load_breast_cancer().
- Replaced synthetic `load_diabetes` with the actual diabetes dataset
  (442 samples, 10 features, regression). Real diabetes progression
  data from sklearn.datasets.load_diabetes().
- `load_digits` remains synthetic (180 samples instead of 1797) due to
  the large size of the real 8x8 digit dataset.
- Created `lib/scikit/datasets_real.flow` (3400 lines) containing the
  real data. `datasets.flow` imports it and delegates.

### Improved algorithm implementations

- Replaced `lda_fit` simplified EM with proper variational Bayes EM from
  Blei, Ng, Jordan (2003). Uses digamma function approximation, variational
  phi/gamma updates, and sufficient statistics accumulation. Helper
  functions `_digamma_approx`, `_safe_exp`, `_lda_estep_doc`.
- Replaced `minibatch_dictionary_learning_fit` nearest-atom update with
  Orthogonal Matching Pursuit (OMP) sparse coding. Greedily selects atoms
  by correlation, computes least-squares coefficients, updates dictionary
  atoms weighted by code values. Helper `_omp_sparse_coding_update`.
- Replaced `lasso_lars_fit` post-hoc soft-thresholding with coordinate
  descent Lasso solver. Centers data, iterates soft-thresholded coordinate
  updates until convergence. Produces correct L1-regularized solutions.
  Helpers `_col_means`, `_col_norms_sq`, `_centered_col_dot`,
  `_update_residual`, `_soft_threshold`.
- Improved `kernel_svc_fit` SMO with second-order working set selection.
  Scans all candidates to pick j maximizing |Ei - Ej| instead of
  pseudo-random selection. Helper `_svm_compute_ej`.
- Discovered Flow compiler limitation: functions with too many local
  variables or too much complexity produce bus errors at runtime.
  Worked around by extracting logic into small helper functions.

### Stub elimination and infrastructure modules

- Replaced `StackingRegressor` stub with real implementation: trains
  bootstrap-sampled DecisionTreeRegressor base estimators and a
  least-squares meta-learner on their predictions.
- Replaced `VotingRegressor` stub with real implementation: accepts
  pre-fitted DecisionTreeRegressor estimators and weights, averages
  predictions.
- Replaced `permutation_importance_regression` stub (returned zeros)
  with real implementation that permutes columns, re-predicts, and
  computes the R2 score drop. Added type-specific variants for
  DecisionTreeClassifier, RandomForestRegressor, and
  RandomForestClassifier.
- Replaced `kernel_density_score_samples` stub (used gaussian for all
  kernels) with real implementations for tophat, epanechnikov,
  exponential, linear, and cosine kernels.
- Replaced `spline_transformer_fit` stub (computed knots for first
  feature only) with per-feature knot computation using sorted
  quantiles.
- Replaced `adjusted_mutual_info_score` stub (used 1/n as EMI) with
  proper EMI approximation (R-1)(C-1)/(2(n-1)) from Vinh et al. 2009,
  plus direct MI and entropy computation.
- Added `lib/scikit/utils.flow` with `check_array`, `check_X_y`,
  `check_consistent_length`, `as_float_array`, `safe_indexing`,
  `resample`, `shuffle`, `check_random_state`, `gen_batches`,
  `gen_even_slices`, `tosequence`, `check_scalar`,
  `assert_all_finite`, `check_non_negative`, `check_symmetric`,
  `get_chunk_n_rows`, `compute_sample_weight`, `compute_class_weight`,
  `safe_mask`, `indices_to_mask`, `array_min`, `array_max`,
  `array_nnz`.
- Added `lib/scikit/exceptions.flow` with error codes for
  `NotFittedError`, `ConvergenceWarning`, `DataDimensionWarning`,
  `FitFailedWarning`, `UndefinedMetricWarning`, and helpers
  `check_fitted`, `check_convergence`, `check_n_iter`.
- Added `lib/scikit/config.flow` with `Config` struct,
  `config_default`, `set_config`, and `config_context_*` helpers
  mirroring sklearn's `config_context` and `set_config`.
- Worked around Flow issue #431 (arrays of structs produce invalid
  pointers) by replacing `BatchRange` struct arrays with separate
  start/end integer arrays in `gen_batches` and `gen_even_slices`.

### Final parity batch: 21 missing APIs

- Added `PoissonRegressor`, `GammaRegressor`, `TweedieRegressor` to
  `linear.flow`. Generalized linear models with canonical link functions
  (log, inverse, power) trained via gradient descent.
- Added `RandomTreesEmbedding` to `ensemble.flow`. Transforms data into
  sparse one-hot leaf indicator using an ensemble of random trees.
- Added `LabelBinarizer` to `preprocessing.flow`. Binarizes labels in
  one-vs-all fashion with configurable positive/negative labels and
  inverse transform.
- Added `chi2`, `f_classif`, `f_regression` to `feature_selection.flow`.
  Statistical test scorers returning `Chi2Result` / `FResult` structs with
  scores and p-values.
- Added `GroupShuffleSplit` to `model_selection.flow`. Shuffle-Group(s)-Out
  cross-validation iterator that holds out entire groups at random.
- Added `silhouette_samples` to `metrics.flow`. Per-sample silhouette
  coefficients.
- Added `rand_score` to `metrics.flow`. Unadjusted Rand Index.
- Added `estimate_bandwidth` to `cluster.flow`. Bandwidth estimator for
  MeanShift using pairwise distance quantiles.
- Added `kmeans_plusplus_init` to `cluster.flow`. K-Means++ cluster center
  initialization.
- Added `FeatureUnion` to `compose.flow`. Concatenates outputs of multiple
  transformers (StandardScaler, MinMaxScaler, passthrough, polynomial).
- Added `SkewedChi2Sampler` to `kernel_approximation.flow`. Monte Carlo
  approximation of the skewed chi-squared kernel feature map.
- Added `johnson_lindenstrauss_min_dim` to `random_projection.flow`.
  Computes the minimal embedding dimension for the Johnson-Lindenstrauss
  lemma.
- Added `MissingIndicator` to `impute.flow`. Binary indicator matrix for
  missing values.
- Added `load_digits`, `load_wine`, `load_breast_cancer`, `load_diabetes`
  to `datasets.flow`. Synthetic versions of the standard sklearn toy
  datasets with matching dimensions and class counts.

### Tooling

- Added `tools/run_all.py` to run every test and example with a single
  command. Closes #2.
- CI now runs all tests and examples via the runner, not just syntax
  validation.

### Sklearn parity fixes

- Added `feature_importances_` for DecisionTreeClassifier,
  DecisionTreeRegressor, RandomForestClassifier, RandomForestRegressor,
  GradientBoostingClassifier, GradientBoostingRegressor, and
  AdaBoostClassifier. Uses weighted impurity decrease, normalized to sum 1.
  Includes proper not-fitted check via the `fitted` field. Addresses sklearn
  #34472.
- Added AdaBoostRegressor (AdaBoost.R2 algorithm with linear loss and
  weighted median prediction). Includes `feature_importances_` weighted by
  estimator weights. Addresses sklearn #34472.
- Added LedoitWolf covariance estimator with analytical shrinkage intensity
  (Ledoit & Wolf 2004). Includes `ledoit_wolf_fit`, `ledoit_wolf_estimate`,
  and weighted variants `ledoit_wolf_fit_weighted` and
  `ledoit_wolf_estimate_weighted` that accept sample weights. Addresses
  sklearn #34660.
- Added `impurity` field to TreeNode for feature importance computation.
- Added `pow` to the extern declarations in matrix.flow.
- Added `tests/test_parity_fixes_v2.flow` with 8 tests.
- `explained_variance_score` now returns NaN and prints a warning for single-
  sample input or zero-variance y_true, instead of silently returning 0.0
  or 1.0. Addresses sklearn #34622.
- `OrdinalEncoder` now handles NaN as a missing value during fit (excluded
  from categories) and transform (encoded as `encoded_missing_value`), instead
  of treating it as an unknown category. Addresses sklearn #34387.
- Added `ensure_no_nan` and `validate_for_predict` to the validation module.
  These allow +inf / -inf at predict time for tree-based models, where
  decision rules `x <= threshold` are well-defined for inf. Only NaN is
  rejected. Addresses sklearn #34668.
- Added `onehot_encoder_fit_with_freq` to OneHotEncoder. Categories appearing
  fewer than `min_frequency` times are dropped from the encoding. Addresses
  sklearn #34649.
- `LabelPropagation` and `LabelSpreading` now assign uniform transition
  probabilities to zero-affinity rows, instead of clamping degree to 1e-10
  and producing all-zero distributions. Addresses sklearn #34351.
- `KMeans` now relocates empty-cluster centroids to the point farthest from
  its assigned centroid, instead of leaving the centroid in place. Addresses
  sklearn #34074.
- Closed 26 out-of-scope issues for components not implemented in flow-scikit.
- Added `tests/test_sklearn_parity_fixes.flow` with 7 tests.

### Runtime fixes

- Fixed `NearestNeighbors` heap corruption: `nearest_neighbors_kneighbors`
  allocated 16 bytes per `NeighborResult` instead of 24 (the struct is
  `ptr + ptr + i32` = 24 bytes with padding on arm64).
- Fixed `ExtraTreesClassifier` and `ExtraTreesRegressor` tree array
  allocation: was 8 bytes per `DecisionTreeClassifier`/`DecisionTreeRegressor`
  instead of 64. The structs are 40 and 24 bytes respectively.
- Fixed `MultiOutputClassifier` and `MultiOutputRegressor` model array
  allocation: was 8 bytes per `LogisticRegression`/`LinearRegression`
  instead of 64/32. The structs are 48 and 32 bytes respectively.
- Fixed `GaussianProcessRegressor` `_backward_sub`: the Flow transpiler
  generates a positive step for `for i in N-1 to 0`, producing a loop that
  never executes. Replaced with a `while` loop.
- Fixed `ColumnTransformer`: `column_transformer_fit` now returns the struct
  instead of mutating a by-value parameter. Flow passes structs by value, so
  `ct.n_output_features` was never visible to the caller.
- Rewrote `BayesianRidge` to use a closed-form solution (Gaussian elimination
  on `beta * XtX + alpha * I`) instead of gradient descent. Fixed `b_vec`
  indexing in the elimination (was using column index instead of row index).
- Rewrote `IsotonicRegression` PAV algorithm with a stack-based approach.
  The old `while changed` loop could oscillate. Used `while` instead of `for`
  to avoid the vectorization pragma producing incorrect codegen.
- Fixed `PipelineStep` allocation in `pipeline_new`: was 128 bytes per step
  instead of 256. The struct is 248 bytes.
- Fixed `ensemble_comparison` example: removed duplicate free of estimators
  and classes already freed by `voting_classifier_free`.
- Fixed `MultinomialNB` test data to use feature distributions that differ
  across classes. Multinomial NB distinguishes by feature proportions, not
  magnitudes.

### New estimators and metrics

- Added `SVC` and `SVR` with kernel support (RBF, linear, polynomial, sigmoid)
  via SMO algorithm. One-vs-rest for multi-class. `svc_fit`, `svc_predict`,
  `svc_decision_function`, `svr_fit`, `svr_predict`.
- Added `OrthogonalMatchingPursuit` with greedy atom selection and least
  squares refit on the active set.
- Added `QuantileRegressor` with pinball loss gradient descent.
- Added `MultiTaskLasso` and `MultiTaskElasticNet` with group soft-thresholding
  across tasks.
- Added `RadiusNeighborsRegressor` for radius-based regression prediction.
- Added `MiniBatchSparsePCA` with stochastic mini-batch gradient descent and
  soft-thresholding.
- Rewrote `HistGradientBoostingClassifier` to use real regression trees on
  gradients instead of the mean-gradient stub. Now accepts X and builds
  `DecisionTreeRegressor` instances per boosting iteration.
- Added `export_tree_text` and `export_tree_text_reg` for text-based tree
  visualization.
- Added metrics: `zero_one_loss`, `zero_one_loss_count`, `hamming_loss`,
  `dcg_score`, `ndcg_score`, `coverage_error`, `label_ranking_loss`.
- Added `tests/test_new_features.flow` with 45 tests covering all new
  estimators and metrics.

### Additional estimators and utilities

- Added `HistGradientBoostingRegressor` with squared error loss and
  regression tree boosting.
- Added `TargetEncoder` with smoothed mean encoding for categorical features.
- Added `export_graphviz` and `export_graphviz_reg` for DOT-format tree
  visualization.
- Added metrics: `average_precision_score`, `top_k_accuracy_score`,
  `mean_poisson_deviance`, `mean_gamma_deviance`, `d2_tweedie_score`,
  `class_likelihood_ratios`, `class_balance_accuracy`.
- Added model selection: `cross_val_score`, `repeated_k_fold`, `check_cv`,
  `permutation_test_score`.
- Added `HDBSCAN` with mutual reachability, MST, and single-linkage clustering.
- Added `FeatureAgglomeration` with correlation-based feature clustering.
- Added `GraphicalLassoCV` with alpha selection via log-likelihood.
- Added `BernoulliRBM` with contrastive divergence training.
- Added `CalibratedClassifierCV` with Platt scaling calibration.
- Added `partial_dependence` for tree models.
- Added `trustworthiness` for manifold learning evaluation.
- Added feature selection: `SelectPercentile`, `SelectFdr`, `SelectFpr`,
  `SelectFwe`, `GenericUnivariateSelect`, `mutual_info_classif`,
  `mutual_info_regression`.
- Filed Flow compiler bug #421: inline `exp()` in nested while loop causes
  bus error. Workaround: extract to helper function.
- Added linear model CV variants: `RidgeCV`, `LassoCV`, `ElasticNetCV`,
  `RidgeClassifierCV`, `PassiveAggressiveRegressor`.
- Added ensemble: `BaggingRegressor`, `VotingRegressor`, `StackingRegressor`.
- Added decomposition: `MiniBatchDictionaryLearning`, `LatentDirichletAllocation`.
- Added `KernelDensity` to neighbors.
- Added `MultiLabelBinarizer`, `SplineTransformer` to preprocessing.
- Added metrics: `mean_absolute_percentage_error`, `mean_tweedie_deviance`,
  `calinski_harabasz_score`, `davies_bouldin_score`, `homogeneity_score`,
  `completeness_score`, `fowlkes_mallows_score`.
- Added model selection: `LeavePOut`, `StratifiedShuffleSplit`, `GroupKFold`.
- Added linear model CV: `LogisticRegressionCV`, `LarsCV`, `LassoLars`,
  `LassoLarsCV`, `MultiTaskLassoCV`, `MultiTaskElasticNetCV`.
- Added `MiniBatchNMF` to decomposition.
- Added metrics: `adjusted_mutual_info_score`, `pair_confusion_matrix`,
  `mean_pinball_loss`, `d2_absolute_error_score`.
- Fixed integer overflow in test `_noise` helper (i32 to i64 promotion).
- Fixed KernelSVC SMO solver: rewrote for-loops as while-loops to avoid
  Flow for-loop variable scoping issues inside nested while blocks.
  Fixed direct return of function call in `kernel_svc_predict`.
  Fixed direct return of struct literal with function call in `kernel_svc_fit`.
  Extracted inline `exp()` to helper function `_rbf_exp`.
- Replaced all scientific notation literals in `cluster.flow` and `svm.flow`
  with decimal literals.
- Replaced all remaining scientific notation literals across all library,
  test, and example files with explicit decimal literals.
- Fixed direct returns of struct literals containing function calls in
  `gaussian_process.flow`, `neighbors.flow`, and `pipeline.flow` (#409).
- Added `KNeighborsTransformer`, `RadiusNeighborsTransformer` to neighbors.
- Added `RepeatedStratifiedKFold`, `LeaveOneGroupOut`, `LeavePGroupOut` to
  model_selection. Uses `GroupCVResult` struct with separate pointer arrays
  to work around Flow bug #431 (arrays of structs with pointer fields
  produce invalid pointers after function return).
- Filed Flow issue #431.

## 0.2.0

- Added IsotonicRegression (pool-adjacent-violators algorithm)
- Added TSNE (t-SNE with binary search for perplexity calibration)
- Added KernelRidge (linear, polynomial, RBF, sigmoid kernels)
- Added PLSRegression (NIPALS algorithm for cross decomposition)
- Added permutation_importance (inspection module)
- Added NMF (Non-Negative Matrix Factorization)
- Added silhouette_score, median_absolute_error, max_error, mean_squared_log_error metrics
- Added MiniBatchKMeans (mini-batch stochastic k-means)
- Added TruncatedSVD (truncated SVD for sparse data)
- Added MultinomialNB, BernoulliNB (naive Bayes for discrete features)
- Added RidgeClassifier (linear classification via ridge regression)
- Added NearestNeighbors (unsupervised k-nearest neighbors)
- Added version module
- Added Apache-2.0 license
- Private repository setup

## 0.1.0

- Initial release
- Preprocessing: StandardScaler, MinMaxScaler, RobustScaler, MaxAbsScaler,
  Normalizer, Binarizer, OneHotEncoder, OrdinalEncoder, LabelEncoder,
  SimpleImputer, KBinsDiscretizer, PolynomialFeatures, FunctionTransformer
- Linear models: LinearRegression, LogisticRegression, Ridge, Lasso,
  ElasticNet, SGDClassifier, SGDRegressor, MultiClassLogisticRegression
- Neighbors: KNNClassifier, KNNRegressor
- SVM: LinearSVC, LinearSVR, KernelSVC
- Tree: DecisionTreeClassifier, DecisionTreeRegressor
- Naive Bayes: GaussianNB
- Ensemble: RandomForest, Bagging, Voting, GradientBoosting, AdaBoost
- Clustering: KMeans, DBSCAN, AgglomerativeClustering
- Decomposition: PCA
- Metrics: accuracy, precision/recall/f1, classification_report,
  confusion_matrix, roc_curve, roc_auc, precision_recall_curve,
  log_loss, cohen_kappa, matthews_corrcoef, hinge_loss,
  balanced_accuracy, fbeta_score, MSE, RMSE, MAE, R2,
  explained_variance
- Model selection: train_test_split, cross_validate, GridSearchCV,
  RandomizedSearchCV, KFold, StratifiedKFold, ShuffleSplit,
  learning_curve, validation_curve
- Feature selection: SelectKBest, VarianceThreshold, SelectFromModel
- Calibration: calibration_curve with Clopper-Pearson CI
- Pipeline with clone-in-init
- Progress effect system for GridSearchCV
