# Changelog

## Unreleased

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
