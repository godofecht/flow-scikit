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
│                          #   Lasso, ElasticNet, SGDClassifier,
│                          #   SGDRegressor, MultiClassLogisticRegression
├── neighbors.flow         # KNNClassifier, KNNRegressor
├── svm.flow               # LinearSVC, LinearSVR, KernelSVC (RBF)
├── tree.flow              # DecisionTreeClassifier, DecisionTreeRegressor
├── naive_bayes.flow       # GaussianNB
├── ensemble.flow          # RandomForestClassifier/Regressor,
│                          #   BaggingClassifier, VotingClassifier,
│                          #   GradientBoostingClassifier/Regressor,
│                          #   AdaBoostClassifier
├── cluster.flow           # KMeans, DBSCAN, AgglomerativeClustering
├── decomposition.flow     # PCA
├── metrics.flow           # accuracy, precision/recall/f1, classification_report,
│                          #   MSE, RMSE, MAE, R2, roc_auc, roc_curve,
│                          #   precision_recall_curve, log_loss, cohen_kappa,
│                          #   matthews_corrcoef, hinge_loss,
│                          #   explained_variance, balanced_accuracy,
│                          #   fbeta_score, confusion_matrix
├── calibration.flow       # Calibration curve with CI (Issue #30664)
├── model_selection.flow   # train_test_split, cross_validate, GridSearchCV,
│                          #   RandomizedSearchCV, KFold, StratifiedKFold,
│                          #   ShuffleSplit, learning_curve, validation_curve
├── feature_selection.flow # SelectKBest, VarianceThreshold, SelectFromModel
├── pipeline.flow          # Pipeline with clone-in-init (Issue #28394)
├── isotonic.flow          # IsotonicRegression (pool-adjacent-violators)
├── manifold.flow          # TSNE (t-SNE with binary search for perplexity)
├── kernel_ridge.flow      # KernelRidge (linear, poly, RBF, sigmoid kernels)
└── cross_decomposition.flow # PLSRegression (NIPALS algorithm)

examples/
├── iris_classification.flow
├── regression_demo.flow
├── grid_search_demo.flow
└── full_demo.flow

tests/
├── test_preprocessing.flow
├── test_metrics.flow
├── test_model_selection.flow
├── test_estimators.flow
└── test_advanced_estimators.flow
```

## API Coverage

| scikit-learn module       | flow-scikit classes                                          |
|---------------------------|--------------------------------------------------------------|
| `preprocessing`           | StandardScaler, MinMaxScaler, RobustScaler, MaxAbsScaler,    |
|                           | Normalizer, Binarizer, OneHotEncoder, OrdinalEncoder,        |
|                           | LabelEncoder, SimpleImputer, KBinsDiscretizer,               |
|                           | PolynomialFeatures, FunctionTransformer                      |
| `linear_model`            | LinearRegression, LogisticRegression, Ridge, Lasso,          |
|                           | ElasticNet, SGDClassifier, SGDRegressor,                     |
|                           | MultiClassLogisticRegression                                 |
| `neighbors`               | KNNClassifier, KNNRegressor                                  |
| `svm`                     | LinearSVC, LinearSVR, KernelSVC                              |
| `tree`                    | DecisionTreeClassifier, DecisionTreeRegressor                |
| `naive_bayes`             | GaussianNB                                                   |
| `ensemble`                | RandomForestClassifier, RandomForestRegressor,               |
|                           | BaggingClassifier, VotingClassifier,                         |
|                           | GradientBoostingClassifier, GradientBoostingRegressor,       |
|                           | AdaBoostClassifier                                           |
| `cluster`                 | KMeans, DBSCAN, AgglomerativeClustering                      |
| `decomposition`           | PCA                                                          |
| `metrics`                 | accuracy_score, precision_recall_fscore,                     |
|                           | classification_report, confusion_matrix,                     |
|                           | roc_curve, roc_auc_score, precision_recall_curve,            |
|                           | log_loss, cohen_kappa, matthews_corrcoef,                    |
|                           | hinge_loss, balanced_accuracy_score, fbeta_score,            |
|                           | mean_squared_error, root_mean_squared_error,                 |
|                           | mean_absolute_error, r2_score, explained_variance_score      |
| `model_selection`         | train_test_split, cross_validate_score, GridSearchCV,        |
|                           | RandomizedSearchCV, KFold, StratifiedKFold,                  |
|                           | ShuffleSplit, learning_curve, validation_curve               |
| `feature_selection`       | SelectKBest, VarianceThreshold, SelectFromModel              |
| `calibration`             | calibration_curve (with Clopper-Pearson CI)                  |
| `pipeline`                | Pipeline                                                     |
| `isotonic`               | IsotonicRegression                                           |
| `manifold`               | TSNE                                                         |
| `kernel_ridge`           | KernelRidge (linear, poly, RBF, sigmoid)                     |
| `cross_decomposition`    | PLSRegression (NIPALS)                                       |
| `inspection`             | (planned)                                                    |

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

```bash
./flow run tests/test_preprocessing.flow
./flow run tests/test_metrics.flow
./flow run tests/test_model_selection.flow
./flow run tests/test_estimators.flow
./flow run tests/test_advanced_estimators.flow
```

## Running Examples

```bash
./flow run examples/iris_classification.flow
./flow run examples/regression_demo.flow
./flow run examples/grid_search_demo.flow
./flow run examples/full_demo.flow
```
