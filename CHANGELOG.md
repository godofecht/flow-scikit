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
