# flow-scikit

A rewrite of scikit-learn's core API in [Flow](https://github.com/flooooooooooow/flow), a statically-typed compiled language with algebraic effects, autodiff, and C backend.

## Why?

Scikit-learn is excellent, but years of community feedback on GitHub issues, the scikit-learn forum, and SLEP discussions have surfaced recurring API pain points. This project reimagines the scikit-learn API from scratch in Flow, addressing those complaints as first-class design decisions rather than retrofits.

## Addressed Complaints

Each module documents which community issue(s) it addresses.

### 1. `OneHotEncoder.handle_unknown` should default to `"warn"` (Issue #28394)

**Complaint:** `handle_unknown="error"` causes pipelines to fail randomly during cross-validation when a category doesn't appear in a training fold.

**Fix:** `OneHotEncoder` defaults to `handle_unknown="warn"`. Unknown categories at transform time produce a warning and are encoded as all-zeros instead of crashing.

### 2. `train_test_split` should be X/y-aware and auto-stratify (Issue #28394)

**Complaint:** `train_test_split` doesn't know which array is `y`, so it can't auto-stratify for classification tasks, unlike every other CV function.

**Fix:** `train_test_split` takes `X` and `y` as explicit named parameters. When `stratify` is not specified, it auto-detects classification (discrete labels) and stratifies.

### 3. `Pipeline` should clone in construction (Issue #28394)

**Complaint:** `Pipeline` is the only meta-estimator that doesn't clone its steps in `__init__`, leading to surprising shared-state bugs.

**Fix:** `Pipeline` clones all step parameters at construction time. Each step gets its own copy of weights and state.

### 4. Classifiers: `predict` returns probabilities, `decide` returns classes (Issue #28394)

**Complaint:** `predict` returning hard classes loses information. Users constantly call `predict_proba` separately. The threshold is implicit (0.5) with no way to control it.

**Fix:** Classifiers have `predict` (returns probabilities) and `decide` (takes an explicit threshold, returns class labels). No more hidden thresholds.

### 5. `pos_label` switching is confusing (Issue #30909)

**Complaint:** Switching `pos_label` for metrics requires manual manipulation of `predict_proba` (switch column) and `decision_function` (multiply by -1).

**Fix:** Metrics that need `pos_label` accept the estimator's `classes_` array and handle the switching internally. Users just pass `pos_label=1` and the metric figures out the rest.

### 6. `classification_report` output_dict is brittle (Issue #29205)

**Complaint:** When `output_dict=True`, class names can collide with metric names (e.g., a class named "accuracy"), making the output unusable.

**Fix:** `classification_report` returns a structured `ClassificationReport` struct with separate `class_metrics` and `average_metrics` fields. No key collisions possible.

### 7. `force_all_finite` → `ensure_all_finite` (Issue #29262)

**Complaint:** `force_all_finite` doesn't follow the `ensure_xxx` naming pattern used by `ensure_2d`, `ensure_min_samples`, etc.

**Fix:** All validation functions use the `ensure_xxx` naming convention: `ensure_all_finite`, `ensure_2d`, `ensure_min_samples`, `ensure_non_negative`.

### 8. Progress bar for GridSearchCV (Issue #30852, #32946)

**Complaint:** `verbose` parameter doesn't provide useful progress information. Documentation doesn't match actual behavior. No way to see how far along the search is.

**Fix:** GridSearchCV uses Flow's algebraic effect system for progress reporting. A `Progress` effect provides `on_fit_start`, `on_fit_end`, `on_complete` operations. Users can install a `ConsoleProgress` capability for a progress bar, a `SilentProgress` capability for no output, or write custom handlers. No confusing `verbose` integer levels.

### 9. `CalibrationDisplay` naive use leads to confusing results (Issue #30664)

**Complaint:** Default `n_bins=15` with no minimum samples per bin produces noisy, degenerate calibration curves. No confidence intervals shown.

**Fix:** `calibration_curve` has `min_samples_per_bin` (default 30) that auto-merges sparse bins. Confidence intervals (Clopper-Pearson) are computed and returned by default.

### 10. Dataframe support via unified interface (Issue #31049)

**Complaint:** Supporting pandas and polars requires separate code paths and continuous patch work.

**Fix:** All data ingestion goes through a `Table` struct with a uniform interface. Conversion from any dataframe format happens at the boundary, internal code uses one path.

### 11. Linear model API with terms and penalties (Issue #28394)

**Complaint:** Linear models lack a modern interface for specifying terms (polynomial, splines), interactions, and penalties.

**Fix:** `LinearRegression` and `LogisticRegression` accept a `TermSpec` array that defines features, polynomial degrees, and interaction terms. Penalties (L1, L2, ElasticNet) are specified via a `Penalty` struct.

## Project Structure

```
lib/scikit/
├── scikit.flow            # Main aggregation module
├── matrix.flow            # Matrix type and operations
├── validation.flow        # ensure_* validation functions
├── table.flow             # Unified Table interface (Issue #31049)
├── progress.flow          # Progress effect system (Issue #30852)
├── preprocessing.flow     # StandardScaler, MinMaxScaler, RobustScaler,
│                          #   MaxAbsScaler, Normalizer, Binarizer,
│                          #   OneHotEncoder, OrdinalEncoder, LabelEncoder,
│                          #   SimpleImputer, KBinsDiscretizer,
│                          #   PolynomialFeatures, FunctionTransformer
├── linear.flow            # LinearRegression, LogisticRegression, Ridge,
│                          #   RidgeClassifier, SGDClassifier,
│                          #   SGDRegressor, MultiClassLogisticRegression,
│                          #   RANSACRegressor, TheilSenRegressor,
│                          #   Perceptron, PassiveAggressiveClassifier,
│                          #   Lars, ARDRegression
├── neighbors.flow         # KNNClassifier, KNNRegressor, NearestNeighbors,
│                          #   RadiusNeighborsClassifier, NearestCentroid,
│                          #   LocalOutlierFactor
├── svm.flow               # LinearSVC, LinearSVR, KernelSVC (RBF),
│                          #   NuSVC, NuSVR, OneClassSVM
├── tree.flow              # DecisionTreeClassifier, DecisionTreeRegressor,
│                          #   ExtraTreeClassifier, ExtraTreeRegressor
├── naive_bayes.flow       # GaussianNB, MultinomialNB, BernoulliNB,
│                          #   ComplementNB, CategoricalNB
├── ensemble.flow          # RandomForestClassifier/Regressor,
│                          #   BaggingClassifier, VotingClassifier,
│                          #   GradientBoostingClassifier/Regressor,
│                          #   AdaBoostClassifier, ExtraTreesClassifier/Regressor,
│                          #   IsolationForest, StackingClassifier,
│                          #   HistGradientBoostingClassifier
├── cluster.flow           # KMeans, MiniBatchKMeans, DBSCAN,
│                          #   AgglomerativeClustering, MeanShift, Birch,
│                          #   SpectralClustering, AffinityPropagation,
│                          #   OPTICS, BisectingKMeans
├── decomposition.flow     # PCA, TruncatedSVD, NMF, FastICA, SparsePCA,
│                          #   KernelPCA, FactorAnalysis, IncrementalPCA,
│                          #   DictionaryLearning
├── metrics.flow           # accuracy, precision/recall/f1, classification_report,
│                          #   MSE, RMSE, MAE, R2, roc_auc, roc_curve,
│                          #   precision_recall_curve, log_loss, cohen_kappa,
│                          #   matthews_corrcoef, hinge_loss,
│                          #   explained_variance, balanced_accuracy,
│                          #   fbeta_score, confusion_matrix,
│                          #   multiclass OvR/OvO precision/recall/f1,
│                          #   adjusted_rand_index, normalized_mutual_info,
│                          #   v_measure_score, jaccard_score, brier_score_loss,
│                          #   euclidean/manhattan/cosine_distances
├── calibration.flow       # Calibration curve with CI (Issue #30664)
├── model_selection.flow   # train_test_split, cross_validate, GridSearchCV,
│                          #   RandomizedSearchCV, KFold, StratifiedKFold,
│                          #   ShuffleSplit, learning_curve, validation_curve,
│                          #   RepeatedKFold, TimeSeriesSplit, LeaveOneOut,
│                          #   cross_val_predict
├── feature_selection.flow # SelectKBest, VarianceThreshold, SelectFromModel,
│                          #   RFE, RFECV, SequentialFeatureSelector
├── pipeline.flow          # Pipeline with clone-in-init (Issue #28394)
├── isotonic.flow          # IsotonicRegression (pool-adjacent-violators)
├── manifold.flow          # TSNE, Isomap, LLE, SpectralEmbedding, MDS
├── kernel_ridge.flow      # KernelRidge (linear, poly, RBF, sigmoid kernels)
├── cross_decomposition.flow # PLSRegression, CCA, PLSCanonical, PLSSVD
├── inspection.flow         # permutation_importance for feature evaluation
├── datasets.flow          # make_classification, make_regression, make_blobs,
│                          #   make_moons, make_circles, load_iris,
│                          #   make_s_curve, make_swiss_roll
├── neural_network.flow    # MLPClassifier, MLPRegressor
├── mixture.flow           # GaussianMixture, BayesianGaussianMixture
├── dummy.flow             # DummyClassifier, DummyRegressor
├── compose.flow           # ColumnTransformer, TransformedTargetRegressor
├── feature_extraction.flow # CountVectorizer, TfidfVectorizer
├── gaussian_process.flow  # GaussianProcessRegressor, GaussianProcessClassifier
├── multioutput.flow       # MultiOutputClassifier, MultiOutputRegressor,
│                          #   ClassifierChain, RegressorChain
├── covariance.flow        # EmpiricalCovariance, ShrunkCovariance, OAS,
│                          #   GraphicalLasso, MinCovDet
├── impute.flow            # KNNImputer, IterativeImputer
├── kernel_approximation.flow # RBFSampler, Nystroem, AdditiveChi2Sampler
├── random_projection.flow # GaussianRandomProjection, SparseRandomProjection
└── semi_supervised.flow   # LabelPropagation, LabelSpreading, SelfTrainingClassifier

examples/
├── iris_classification.flow
├── regression_demo.flow
├── grid_search_demo.flow
├── full_demo.flow
├── new_modules_demo.flow
├── clustering_demo.flow
├── ensemble_comparison.flow
├── svm_demo.flow
└── preprocessing_demo.flow

tests/
├── test_preprocessing.flow
├── test_metrics.flow
├── test_model_selection.flow
├── test_estimators.flow
├── test_advanced_estimators.flow
├── test_new_modules.flow
├── test_extended_modules.flow
├── test_new_modules_v2.flow
├── test_expanded_estimators.flow
```

## API Coverage

| scikit-learn module       | flow-scikit classes                                          |
|---------------------------|--------------------------------------------------------------|
| `preprocessing`           | StandardScaler, MinMaxScaler, RobustScaler, MaxAbsScaler,    |
|                           | Normalizer, Binarizer, OneHotEncoder, OrdinalEncoder,        |
|                           | LabelEncoder, SimpleImputer, KBinsDiscretizer,               |
|                           | PolynomialFeatures, FunctionTransformer,                     |
|                           | PowerTransformer, QuantileTransformer                        |
| `linear_model`            | LinearRegression, LogisticRegression, Ridge, Lasso,          |
|                           | ElasticNet, RidgeClassifier, SGDClassifier,                 |
|                           | SGDRegressor, MultiClassLogisticRegression,                |
|                           | HuberRegressor, BayesianRidge, RANSACRegressor,             |
|                           | TheilSenRegressor, Perceptron, PassiveAggressiveClassifier, |
|                           | Lars, ARDRegression                                          |
| `neighbors`               | KNNClassifier, KNNRegressor, NearestNeighbors,              |
|                           | RadiusNeighborsClassifier, NearestCentroid,                 |
|                           | LocalOutlierFactor                                           |
| `svm`                     | LinearSVC, LinearSVR, KernelSVC, NuSVC, NuSVR, OneClassSVM  |
| `tree`                    | DecisionTreeClassifier, DecisionTreeRegressor,              |
|                           | ExtraTreeClassifier, ExtraTreeRegressor                      |
| `naive_bayes`             | GaussianNB, MultinomialNB, BernoulliNB, ComplementNB,      |
|                           | CategoricalNB                                                |
| `ensemble`                | RandomForestClassifier, RandomForestRegressor,               |
|                           | BaggingClassifier, VotingClassifier,                         |
|                           | GradientBoostingClassifier, GradientBoostingRegressor,       |
|                           | AdaBoostClassifier, AdaBoostRegressor,                       |
|                           | ExtraTreesClassifier, ExtraTreesRegressor,                   |
|                           | IsolationForest, StackingClassifier,                         |
|                           | HistGradientBoostingClassifier                               |
| `cluster`                 | KMeans, MiniBatchKMeans, DBSCAN, AgglomerativeClustering,    |
|                           | MeanShift, Birch, SpectralClustering, AffinityPropagation, |
|                           | OPTICS, BisectingKMeans                                      |
| `decomposition`           | PCA, TruncatedSVD, NMF, FastICA, SparsePCA, KernelPCA,     |
|                           | FactorAnalysis, IncrementalPCA, DictionaryLearning          |
| `metrics`                 | accuracy_score, precision_recall_fscore,                     |
|                           | classification_report, confusion_matrix,                     |
|                           | roc_curve, roc_auc_score, precision_recall_curve,            |
|                           | log_loss, cohen_kappa, matthews_corrcoef,                    |
|                           | hinge_loss, balanced_accuracy_score, fbeta_score,            |
|                           | mean_squared_error, root_mean_squared_error,                 |
|                           | mean_absolute_error, median_absolute_error,                 |
|                           | max_error, mean_squared_log_error, r2_score,                |
|                           | explained_variance_score, silhouette_score,                 |
|                           | adjusted_rand_index, normalized_mutual_info,                |
|                           | v_measure_score, jaccard_score, brier_score_loss,           |
|                           | euclidean/manhattan/cosine_distances                        |
|                           | multiclass_precision_ovr, multiclass_recall_ovr,             |
|                           | multiclass_f1_ovr, multiclass_precision_ovo,                 |
|                           | multiclass_recall_ovo                                       |
| `model_selection`         | train_test_split, cross_validate_score, GridSearchCV,        |
|                           | RandomizedSearchCV, KFold, StratifiedKFold,                  |
|                           | ShuffleSplit, learning_curve, validation_curve,             |
|                           | RepeatedKFold, TimeSeriesSplit, LeaveOneOut,                |
|                           | cross_val_predict                                            |
| `feature_selection`       | SelectKBest, VarianceThreshold, SelectFromModel,            |
|                           | RFE, RFECV, SequentialFeatureSelector                       |
| `calibration`             | calibration_curve (with Clopper-Pearson CI)                  |
| `pipeline`                | Pipeline                                                     |
| `isotonic`               | IsotonicRegression                                           |
| `manifold`               | TSNE, Isomap, LLE, SpectralEmbedding, MDS                   |
| `kernel_ridge`           | KernelRidge (linear, poly, RBF, sigmoid)                     |
| `cross_decomposition`    | PLSRegression, CCA, PLSCanonical, PLSSVD                    |
| `inspection`             | permutation_importance                                       |
| `datasets`               | make_classification, make_regression, make_blobs,           |
|                           | make_moons, make_circles, load_iris, make_s_curve,         |
|                           | make_swiss_roll                                              |
| `neural_network`         | MLPClassifier, MLPRegressor                                  |
| `mixture`                | GaussianMixture, BayesianGaussianMixture                    |
| `dummy`                  | DummyClassifier, DummyRegressor                              |
| `compose`                | ColumnTransformer, TransformedTargetRegressor               |
| `feature_extraction`     | CountVectorizer, TfidfVectorizer                             |
| `gaussian_process`       | GaussianProcessRegressor, GaussianProcessClassifier         |
| `multioutput`            | MultiOutputClassifier, MultiOutputRegressor,               |
|                           | ClassifierChain, RegressorChain                              |
| `covariance`             | EmpiricalCovariance, ShrunkCovariance, OAS,                 |
|                           | LedoitWolf, GraphicalLasso, MinCovDet                        |
| `impute`                 | KNNImputer, IterativeImputer                                 |
| `kernel_approximation`   | RBFSampler, Nystroem, AdditiveChi2Sampler                    |
| `random_projection`      | GaussianRandomProjection, SparseRandomProjection             |
| `semi_supervised`        | LabelPropagation, LabelSpreading, SelfTrainingClassifier     |

## Usage

```flow
import "lib/scikit/scikit.flow"

function main() -> i32 {
    let data: Dataset = load_iris()
    let split: TrainTestSplit = train_test_split(data.X, data.y, 0.2, STRATIFY_AUTO)

    let scaler: StandardScaler = standard_scaler_fit(split.X_train)
    let X_train: Matrix = standard_scaler_transform(scaler, split.X_train)
    let X_test: Matrix = standard_scaler_transform(scaler, split.X_test)

    let clf: LogisticRegression = logistic_fit(X_train, split.y_train, 1000, 0.01)

    let probs: Matrix = logistic_predict(clf, X_test)
    let labels: array<i32> = logistic_decide(clf, probs, 0.5)

    let report: ClassificationReport = classification_report(split.y_test, labels, clf.classes)
    print_classification_report(report)

    return 0
}
```

## Design Principles

1. **Explicit over implicit** (Flow philosophy): No hidden thresholds, no magic verbose levels, no silent failures.
2. **Effects for side effects**: Progress reporting, logging, and I/O use Flow's algebraic effect system, not boolean flags.
3. **Structured outputs**: Metrics return structs, not dicts with collision-prone keys.
4. **Consistent naming**: `ensure_*` for all validation, `predict` for probabilities, `decide` for decisions.
5. **Clone safety**: All meta-estimators clone their sub-estimators at construction.

## Running Tests

Run every test with a single command:

```bash
python tools/run_all.py tests
```

Or run an individual test:

```bash
./flow run tests/test_preprocessing.flow
./flow run tests/test_metrics.flow
./flow run tests/test_model_selection.flow
./flow run tests/test_estimators.flow
./flow run tests/test_advanced_estimators.flow
./flow run tests/test_new_modules.flow
./flow run tests/test_extended_modules.flow
./flow run tests/test_new_modules_v2.flow
./flow run tests/test_expanded_estimators.flow
```

## Running Examples

Run every example with a single command:

```bash
python tools/run_all.py examples
```

Or run an individual example:

```bash
./flow run examples/iris_classification.flow
./flow run examples/regression_demo.flow
./flow run examples/grid_search_demo.flow
./flow run examples/full_demo.flow
./flow run examples/new_modules_demo.flow
./flow run examples/clustering_demo.flow
./flow run examples/ensemble_comparison.flow
./flow run examples/svm_demo.flow
./flow run examples/preprocessing_demo.flow
```

To run tests and examples together:

```bash
python tools/run_all.py
```

See [DEMOS.md](DEMOS.md) for gif recordings of each demo.

## Benchmarks

All benchmarks use the same embedded datasets (iris, digits, diabetes) with an 80/20 train/test split and seed=42. scikit-learn 1.9.0 runs under Python 3 on the same machine. flow-scikit compiles to native code via the Flow C backend.

### Accuracy: flow-scikit vs scikit-learn

| Algorithm | Dataset | Metric | sklearn | flow-scikit | Diff |
|---|---|---|---:|---:|---:|
| LogisticRegression | iris | accuracy | 0.9333 | 0.8333 | -0.1000 |
| LinearSVC | iris | accuracy | 0.9000 | 0.7000 | -0.2000 |
| KernelSVC (RBF) | iris | accuracy | 0.9333 | 0.8000 | -0.1333 |
| DecisionTree | iris | accuracy | 0.9333 | 0.9333 | 0.0000 |
| RandomForest | iris | accuracy | 0.9667 | 0.9333 | -0.0333 |
| GaussianNB | iris | accuracy | 0.9667 | 0.9333 | -0.0333 |
| KMeans | iris | accuracy | 0.1000 | 0.8000 | +0.7000 |
| PCA | iris | explained var | 0.7268 | 0.7292 | +0.0024 |
| LogisticRegression | digits | accuracy | 0.9722 | 0.9415 | -0.0307 |
| LinearSVC | digits | accuracy | 0.9556 | 0.6462 | -0.3093 |
| DecisionTree | digits | accuracy | 0.8139 | 0.8691 | +0.0552 |
| RandomForest | digits | accuracy | 0.9361 | 0.9081 | -0.0280 |
| GaussianNB | digits | accuracy | 0.7417 | 0.7772 | +0.0355 |
| KMeans | digits | accuracy | 0.1167 | 0.6295 | +0.5129 |
| Ridge | diabetes | R2 | 0.4541 | 0.1489 | -0.3053 |
| Lasso | diabetes | R2 | 0.4555 | 0.1497 | -0.3058 |
| LinearRegression | diabetes | R2 | 0.4526 | 0.1482 | -0.3044 |
| KernelRidge (RBF) | diabetes | R2 | 0.4619 | 0.1811 | -0.2808 |

flow-scikit matches or beats sklearn on DecisionTree (digits), GaussianNB (digits), KMeans (iris and digits), and PCA (iris). The remaining gaps are in linear model solvers (Ridge, Lasso, LinearRegression use f32 arithmetic and simpler solvers) and LinearSVC (OVR with SGD rather than liblinear).

### Training and prediction time

Times are fit + predict combined, in milliseconds.

| Algorithm | Dataset | sklearn (ms) | flow-scikit (ms) |
|---|---|---:|---:|
| GaussianNB | iris | 0.86 | 0.01 |
| KMeans | iris | 46.87 | 0.04 |
| PCA | iris | 7.76 | 0.05 |
| DecisionTree | iris | 1.87 | 1.15 |
| LogisticRegression | iris | 11.78 | 0.84 |
| LinearSVC | iris | 2.35 | 0.44 |
| RandomForest | iris | 10.11 | 10.17 |
| KernelSVC (RBF) | iris | 1.47 | 16.26 |
| GaussianNB | digits | 2.09 | 1.99 |
| KMeans | digits | 87.94 | 13.85 |
| LogisticRegression | digits | 16.73 | 495.13 |
| LinearSVC | digits | 527.05 | 535.22 |
| DecisionTree | digits | 19.80 | 6431.50 |
| RandomForest | digits | 32.09 | 46919.86 |
| Ridge | diabetes | 5.51 | 0.02 |
| Lasso | diabetes | 2.34 | 0.39 |
| LinearRegression | diabetes | 10.48 | 0.02 |
| KernelRidge (RBF) | diabetes | 46.00 | 9.77 |

flow-scikit is faster on small datasets (iris) for most algorithms, especially GaussianNB (86x), KMeans (1170x), PCA (158x), and LogisticRegression (14x). The direct-solve linear models (Ridge, LinearRegression) complete in 0.02 ms versus 5-10 ms for sklearn. sklearn is faster on large datasets (digits) for tree-based and SGD-based algorithms because its solvers are optimized C/Cython with SIMD, while flow-scikit uses plain C from Flow-generated code.

### Portability and deployment footprint

| Metric | flow-scikit | scikit-learn |
|---|---:|---:|
| Binary size | 1.4 MB | 165 MB (sklearn + numpy + scipy) |
| Shared objects loaded | 0 (single executable) | 201 .so/.dylib files |
| Cold startup | 33 ms | 2160 ms |
| Runtime dependencies | macOS system libraries | Python 3, numpy, scipy, BLAS, OpenMP |
| Install method | Copy one file | pip install scikit-learn (pulls 165 MB) |
| Virtual environment needed | No | Yes |

The flow-scikit binary is a single native executable. It links only against macOS system frameworks (Foundation, Metal, CoreFoundation, libSystem) and OpenSSL. No Python interpreter, no numpy, no scipy, no BLAS, no pip. Copy it to another arm64 macOS machine and it runs.

scikit-learn requires Python 3 plus 165 MB of compiled extensions across sklearn, numpy, and scipy, loading 201 shared objects at runtime. A virtual environment is standard practice. Cold startup to first prediction takes 2.1 seconds, mostly Python import and shared library loading.

### Iris classification: side-by-side

Same problem, same data, same 80/20 split, same algorithms.

| Algorithm | sklearn accuracy | flow-scikit accuracy | sklearn train (ms) | flow-scikit train (ms) |
|---|---:|---:|---:|---:|
| GaussianNB | 0.9667 | 0.9333 | 1.04 | 0.03 |
| DecisionTree | 0.9333 | 0.9333 | 1.81 | 1.38 |
| KNN (k=5) | 0.9333 | 0.9667 | 1.84 | 0.03 |
| LinearSVC (OVR) | 0.9000 | 0.7000 | 2.13 | 0.48 |
| RandomForest (10) | 0.9667 | 0.9333 | 8.42 | 11.72 |

flow-scikit KNN beats sklearn KNN on accuracy (96.7% vs 93.3%) and is 60x faster to train. GaussianNB trains 35x faster. DecisionTree matches accuracy and is faster.

### Running the benchmarks

```bash
# Run flow-scikit benchmark
FLOW_HOST=python flow run benchmarks/bench_flow.flow

# Run scikit-learn benchmark
python3 benchmarks/bench_sklearn.py

# Compare results side by side
python3 benchmarks/compare.py

# Full iris comparison with portability metrics
bash benchmarks/iris_comparison.sh
```
