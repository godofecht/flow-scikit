# flow-scikit Demos

Each demo runs from the terminal via `./flow run examples/<name>.flow`. The gifs below show the expected terminal output.

## Table of Contents

1. [Iris Classification](#iris-classification)
2. [Regression Demo](#regression-demo)
3. [Grid Search Demo](#grid-search-demo)
4. [Full API Demo](#full-api-demo)
5. [New Modules Demo](#new-modules-demo)
6. [Clustering Demo](#clustering-demo)
7. [Ensemble Comparison](#ensemble-comparison)
8. [SVM Demo](#svm-demo)
9. [Preprocessing Demo](#preprocessing-demo)

---

## Iris Classification

Trains a LogisticRegression on synthetic iris-like data. Shows the predict/decide split, structured classification report, and Pipeline with clone-in-init.

```bash
./flow run examples/iris_classification.flow
```

![Iris Classification](gifs/iris_classification.gif)

**What it shows:**
- `train_test_split` with auto-stratify
- `StandardScaler` preprocessing
- `LogisticRegression` with `predict_proba` (probabilities) and `decide` (classes)
- `classification_report` with structured output
- `Pipeline` with clone-in-init

---

## Regression Demo

Fits a `LinearRegression` with polynomial `TermSpec` on synthetic data. Prints MSE, RMSE, MAE, and R2.

```bash
./flow run examples/regression_demo.flow
```

![Regression Demo](gifs/regression_demo.gif)

**What it shows:**
- `TermSpec` for polynomial features
- Regression metrics (MSE, RMSE, MAE, R2)
- `StandardScaler` in a pipeline
- Weight printing

---

## Grid Search Demo

Runs `GridSearchCV` over hyperparameter grid with the `ConsoleProgress` capability for a live progress bar.

```bash
./flow run examples/grid_search_demo.flow
```

![Grid Search Demo](gifs/grid_search_demo.gif)

**What it shows:**
- `GridSearchCV` with progress effect system
- `ConsoleProgress` capability (progress bar)
- `SilentProgress` capability (no output)
- Best params and best score output

---

## Full API Demo

End-to-end pipeline covering preprocessing, PCA, feature selection, train/test split, multi-class logistic, confusion matrix, decision tree, random forest, gradient boosting, Gaussian NB, LinearSVC, KMeans, DBSCAN, regression, and learning curve.

```bash
./flow run examples/full_demo.flow
```

![Full API Demo](gifs/full_demo.gif)

**What it shows:**
- `StandardScaler` + `PCA` dimensionality reduction
- `SelectKBest` feature selection
- `MultiClassLogisticRegression` (softmax)
- `ConfusionMatrix` with formatted printing
- `DecisionTree`, `RandomForest`, `GradientBoosting`, `GaussianNB`, `LinearSVC`
- `KMeans` and `DBSCAN` clustering
- Ridge, Lasso, `GradientBoostingRegressor`
- `learning_curve` with progress reporting
- Cohen's kappa and balanced accuracy

---

## New Modules Demo

Showcases the newer modules: IsotonicRegression, KernelRidge (RBF and linear), PLSRegression, NMF, TSNE, and extended metrics.

```bash
./flow run examples/new_modules_demo.flow
```

![New Modules Demo](gifs/new_modules_demo.gif)

**What it shows:**
- `IsotonicRegression` with monotonic fitting
- `KernelRidge` with RBF and linear kernels
- `PLSRegression` (NIPALS algorithm) for multi-target
- `NMF` with reconstruction error
- `TSNE` dimensionality reduction
- `median_absolute_error`, `max_error`, `mean_squared_log_error`

---

## Clustering Demo

Compares KMeans, MiniBatchKMeans, DBSCAN, and AgglomerativeClustering on 3 Gaussian blobs. Prints cluster labels and silhouette score.

```bash
./flow run examples/clustering_demo.flow
```

![Clustering Demo](gifs/clustering_demo.gif)

**What it shows:**
- `KMeans` with inertia and centroid printing
- `MiniBatchKMeans` with mini-batch updates
- `DBSCAN` with noise point detection
- `AgglomerativeClustering` with single linkage
- `silhouette_score` for cluster quality

---

## Ensemble Comparison

Trains six classifiers on the same dataset and prints a summary table comparing accuracy.

```bash
./flow run examples/ensemble_comparison.flow
```

![Ensemble Comparison](gifs/ensemble_comparison.gif)

**What it shows:**
- `DecisionTreeClassifier` (baseline)
- `RandomForestClassifier`
- `GradientBoostingClassifier`
- `AdaBoostClassifier`
- `BaggingClassifier`
- `VotingClassifier`
- Summary table with all accuracies

---

## SVM Demo

Demonstrates LinearSVC, KernelSVC with RBF kernel, and LinearSVR. Prints weights, support vectors, and hinge loss.

```bash
./flow run examples/svm_demo.flow
```

![SVM Demo](gifs/svm_demo.gif)

**What it shows:**
- `LinearSVC` with weight and bias printing
- `KernelSVC` with RBF kernel and support vector count
- `LinearSVR` for regression with R2
- `hinge_loss` metric

---

## Preprocessing Demo

Walks through every preprocessing transformer with before/after output.

```bash
./flow run examples/preprocessing_demo.flow
```

![Preprocessing Demo](gifs/preprocessing_demo.gif)

**What it shows:**
- `StandardScaler` with mean/std
- `MinMaxScaler` with min/max
- `RobustScaler` with median
- `MaxAbsScaler`
- `Normalizer` (L2)
- `Binarizer`
- `KBinsDiscretizer`
- `PolynomialFeatures` (shape change)
- `LabelEncoder`
- `SimpleImputer` (before/after)

---

## Recording Gifs

The gifs referenced above live in `gifs/`. To record them:

```bash
# Using asciinema
asciinema rec gifs/iris_classification.cast --command "./flow run examples/iris_classification.flow"
# Then convert to gif:
agg gifs/iris_classification.cast gifs/iris_classification.gif

# Or using terminalizer
terminalizer record -k "./flow run examples/iris_classification.flow" -o gifs/iris_classification.yml
terminalizer render gifs/iris_classification.yml -o gifs/iris_classification.gif
```

Each gif should be 800x600 or smaller, under 5 MB, and loop seamlessly.
