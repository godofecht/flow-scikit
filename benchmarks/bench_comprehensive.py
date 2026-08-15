"""
Comprehensive scikit-learn benchmark covering all major algorithm families.

Compares scikit-learn (Python) against a Flow implementation.
Datasets: iris, digits (classification), diabetes (regression).

Output format: RESULT|{algorithm}|{dataset}|{metric}|{score:.6f}|{fit_time:.6f}|{pred_time:.6f}
"""

import time
import numpy as np

from sklearn.datasets import load_iris, load_digits, load_diabetes
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score,
    r2_score,
    adjusted_rand_score,
)

# Classification
from sklearn.linear_model import (
    LogisticRegression,
    RidgeClassifier,
    SGDClassifier,
    PassiveAggressiveClassifier,
    Perceptron,
)
from sklearn.svm import LinearSVC, SVC, SVR
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    AdaBoostClassifier,
    ExtraTreesClassifier,
    BaggingClassifier,
    RandomForestRegressor,
    GradientBoostingRegressor,
    AdaBoostRegressor,
)
from sklearn.naive_bayes import GaussianNB, BernoulliNB, MultinomialNB
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.discriminant_analysis import (
    LinearDiscriminantAnalysis,
    QuadraticDiscriminantAnalysis,
)
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.cluster import KMeans

# Regression
from sklearn.linear_model import (
    LinearRegression,
    Ridge,
    Lasso,
    ElasticNet,
    BayesianRidge,
    ARDRegression,
    HuberRegressor,
    RANSACRegressor,
    TheilSenRegressor,
    PassiveAggressiveRegressor,
    SGDRegressor,
    PoissonRegressor,
    TweedieRegressor,
    GammaRegressor,
)
from sklearn.kernel_ridge import KernelRidge

# Dimensionality reduction
from sklearn.decomposition import PCA, TruncatedSVD, NMF, FastICA

# Clustering
from sklearn.cluster import (
    AgglomerativeClustering,
    DBSCAN,
    SpectralClustering,
    MeanShift,
    Birch,
    AffinityPropagation,
    OPTICS,
)

from scipy.stats import kurtosis


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def time_fit(model, X, y):
    t0 = time.perf_counter()
    model.fit(X, y)
    fit_time = time.perf_counter() - t0
    return model, fit_time


def time_predict(model, X):
    t0 = time.perf_counter()
    pred = model.predict(X)
    pred_time = time.perf_counter() - t0
    return pred, pred_time


def emit(algorithm, dataset, metric, score, fit_time, pred_time):
    print(
        f"RESULT|{algorithm}|{dataset}|{metric}|{score:.6f}|{fit_time:.6f}|{pred_time:.6f}"
    )


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_classification_data(name):
    if name == "iris":
        data = load_iris()
    elif name == "digits":
        data = load_digits()
    else:
        raise ValueError(name)
    X = np.asarray(data.data, dtype=np.float32)
    y = np.asarray(data.target, dtype=np.int64)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train).astype(np.float32)
    X_test = scaler.transform(X_test).astype(np.float32)
    # Raw (non-scaled) split for MultinomialNB
    X_train_raw, X_test_raw, y_train_raw, y_test_raw = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    return {
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "X_train_raw": X_train_raw,
        "X_test_raw": X_test_raw,
        "y_train_raw": y_train_raw,
        "y_test_raw": y_test_raw,
        "X_full": X,
        "y_full": y,
    }


def load_regression_data():
    data = load_diabetes()
    X = np.asarray(data.data, dtype=np.float32)
    y = np.asarray(data.target, dtype=np.float32)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train).astype(np.float32)
    X_test = scaler.transform(X_test).astype(np.float32)
    return {
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "X_full": X,
        "y_full": y,
    }


# ---------------------------------------------------------------------------
# Classification benchmarks
# ---------------------------------------------------------------------------

def run_classification(dataset_name, data):
    X_train = data["X_train"]
    X_test = data["X_test"]
    y_train = data["y_train"]
    y_test = data["y_test"]

    is_iris = dataset_name == "iris"
    max_depth_tree = 5 if is_iris else 10
    max_depth_rf = 5 if is_iris else 10
    gamma_svc = 0.5 if is_iris else 0.001
    n_clusters_kmeans = 3 if is_iris else 10

    models = []

    # --- Linear models ---
    models.append(("LogisticRegression", LogisticRegression(max_iter=1000, C=1.0)))
    models.append(("LinearSVC", LinearSVC(max_iter=1000, C=1.0, dual="auto")))
    models.append(("SVC_RBF", SVC(kernel="rbf", C=1.0, gamma=gamma_svc, max_iter=1000)))
    models.append(("RidgeClassifier", RidgeClassifier()))
    models.append(("SGDClassifier", SGDClassifier(max_iter=1000, random_state=42)))
    models.append(
        (
            "PassiveAggressiveClassifier",
            PassiveAggressiveClassifier(max_iter=1000, random_state=42),
        )
    )
    models.append(("Perceptron", Perceptron(max_iter=1000, random_state=42)))

    # --- Tree-based ensembles ---
    models.append(
        (
            "DecisionTreeClassifier",
            DecisionTreeClassifier(max_depth=max_depth_tree, random_state=42),
        )
    )
    models.append(
        (
            "RandomForestClassifier",
            RandomForestClassifier(
                n_estimators=10, max_depth=max_depth_rf, random_state=42
            ),
        )
    )
    models.append(
        (
            "GradientBoostingClassifier",
            GradientBoostingClassifier(n_estimators=10, max_depth=3, random_state=42),
        )
    )
    models.append(
        ("AdaBoostClassifier", AdaBoostClassifier(n_estimators=10, random_state=42))
    )
    models.append(
        (
            "ExtraTreesClassifier",
            ExtraTreesClassifier(
                n_estimators=10, max_depth=max_depth_rf, random_state=42
            ),
        )
    )
    models.append(
        ("BaggingClassifier", BaggingClassifier(n_estimators=10, random_state=42))
    )

    # --- Naive Bayes ---
    models.append(("GaussianNB", GaussianNB()))
    models.append(("BernoulliNB", BernoulliNB()))

    # --- Neighbors ---
    models.append(("KNeighborsClassifier", KNeighborsClassifier(n_neighbors=5)))

    # --- Discriminant analysis ---
    models.append(("LinearDiscriminantAnalysis", LinearDiscriminantAnalysis()))
    models.append(("QuadraticDiscriminantAnalysis", QuadraticDiscriminantAnalysis()))

    # --- Neural network ---
    models.append(("MLPClassifier", MLPClassifier(max_iter=500, random_state=42)))

    # --- Dummy ---
    models.append(("DummyClassifier", DummyClassifier(strategy="most_frequent")))

    for name, model in models:
        try:
            model, fit_time = time_fit(model, X_train, y_train)
            pred, pred_time = time_predict(model, X_test)
            score = accuracy_score(y_test, pred)
            emit(name, dataset_name, "accuracy", score, fit_time, pred_time)
        except Exception as e:
            print(f"# ERROR {name} on {dataset_name}: {e}")

    # --- MultinomialNB (raw, non-scaled data) ---
    try:
        model = MultinomialNB()
        model, fit_time = time_fit(model, data["X_train_raw"], data["y_train_raw"])
        pred, pred_time = time_predict(model, data["X_test_raw"])
        score = accuracy_score(data["y_test_raw"], pred)
        emit("MultinomialNB", dataset_name, "accuracy", score, fit_time, pred_time)
    except Exception as e:
        print(f"# ERROR MultinomialNB on {dataset_name}: {e}")

    # --- KMeans as classifier (majority label per cluster) ---
    try:
        km = KMeans(n_clusters=n_clusters_kmeans, n_init=10, random_state=42)
        km, fit_time = time_fit(km, X_train, y_train)
        train_clusters = km.labels_
        # assign majority label to each cluster
        cluster_labels = {}
        for c in range(n_clusters_kmeans):
            mask = train_clusters == c
            if mask.sum() > 0:
                cluster_labels[c] = np.bincount(y_train[mask]).argmax()
            else:
                cluster_labels[c] = 0
        t0 = time.perf_counter()
        test_clusters = km.predict(X_test)
        pred = np.array([cluster_labels[c] for c in test_clusters])
        pred_time = time.perf_counter() - t0
        score = accuracy_score(y_test, pred)
        emit("KMeansClassifier", dataset_name, "accuracy", score, fit_time, pred_time)
    except Exception as e:
        print(f"# ERROR KMeansClassifier on {dataset_name}: {e}")


# ---------------------------------------------------------------------------
# Regression benchmarks
# ---------------------------------------------------------------------------

def run_regression(data):
    X_train = data["X_train"]
    X_test = data["X_test"]
    y_train = data["y_train"]
    y_test = data["y_test"]
    dataset_name = "diabetes"

    models = []

    # --- Linear models ---
    models.append(("LinearRegression", LinearRegression()))
    models.append(("Ridge", Ridge(alpha=1.0)))
    models.append(("Lasso", Lasso(alpha=0.1, max_iter=1000)))
    models.append(("ElasticNet", ElasticNet(alpha=0.1, max_iter=1000)))
    models.append(("BayesianRidge", BayesianRidge()))
    models.append(("ARDRegression", ARDRegression(max_iter=100)))
    models.append(("HuberRegressor", HuberRegressor()))
    models.append(("RANSACRegressor", RANSACRegressor(random_state=42)))
    models.append(("TheilSenRegressor", TheilSenRegressor(random_state=42)))
    models.append(
        (
            "PassiveAggressiveRegressor",
            PassiveAggressiveRegressor(max_iter=1000, random_state=42),
        )
    )
    models.append(("SGDRegressor", SGDRegressor(max_iter=1000, random_state=42)))
    models.append(("PoissonRegressor", PoissonRegressor(max_iter=100)))
    models.append(("TweedieRegressor", TweedieRegressor(max_iter=100)))
    models.append(("GammaRegressor", GammaRegressor(max_iter=100)))

    # --- Kernel methods ---
    models.append(
        ("KernelRidge", KernelRidge(alpha=1.0, kernel="rbf", gamma=0.1))
    )
    models.append(("SVR", SVR(kernel="rbf", C=1.0, gamma=0.1)))

    # --- Tree-based ensembles ---
    models.append(
        (
            "DecisionTreeRegressor",
            DecisionTreeRegressor(max_depth=5, random_state=42),
        )
    )
    models.append(
        (
            "RandomForestRegressor",
            RandomForestRegressor(n_estimators=10, max_depth=5, random_state=42),
        )
    )
    models.append(
        (
            "GradientBoostingRegressor",
            GradientBoostingRegressor(n_estimators=10, max_depth=3, random_state=42),
        )
    )
    models.append(
        ("AdaBoostRegressor", AdaBoostRegressor(n_estimators=10, random_state=42))
    )

    # --- Neighbors ---
    models.append(("KNeighborsRegressor", KNeighborsRegressor(n_neighbors=5)))

    # --- Neural network ---
    models.append(("MLPRegressor", MLPRegressor(max_iter=500, random_state=42)))

    # --- Dummy ---
    models.append(("DummyRegressor", DummyRegressor(strategy="mean")))

    for name, model in models:
        try:
            model, fit_time = time_fit(model, X_train, y_train)
            pred, pred_time = time_predict(model, X_test)
            score = r2_score(y_test, pred)
            emit(name, dataset_name, "r2", score, fit_time, pred_time)
        except Exception as e:
            print(f"# ERROR {name} on {dataset_name}: {e}")


# ---------------------------------------------------------------------------
# Dimensionality reduction benchmarks
# ---------------------------------------------------------------------------

def run_dim_reduction(data):
    X = data["X_full"]
    y = data["y_full"]
    dataset_name = "iris"

    # PCA
    try:
        model = PCA(n_components=2)
        model, fit_time = time_fit(model, X, y)
        t0 = time.perf_counter()
        model.transform(X)
        pred_time = time.perf_counter() - t0
        score = model.explained_variance_ratio_[0]
        emit("PCA", dataset_name, "explained_variance_ratio_0", score, fit_time, pred_time)
    except Exception as e:
        print(f"# ERROR PCA: {e}")

    # TruncatedSVD
    try:
        model = TruncatedSVD(n_components=2, random_state=42)
        model, fit_time = time_fit(model, X, y)
        t0 = time.perf_counter()
        model.transform(X)
        pred_time = time.perf_counter() - t0
        score = model.explained_variance_ratio_[0]
        emit("TruncatedSVD", dataset_name, "explained_variance_ratio_0", score, fit_time, pred_time)
    except Exception as e:
        print(f"# ERROR TruncatedSVD: {e}")

    # NMF (requires non-negative data; iris features are non-negative)
    try:
        model = NMF(n_components=2, random_state=42)
        model, fit_time = time_fit(model, X, y)
        t0 = time.perf_counter()
        model.transform(X)
        pred_time = time.perf_counter() - t0
        score = model.reconstruction_err_
        emit("NMF", dataset_name, "reconstruction_error", score, fit_time, pred_time)
    except Exception as e:
        print(f"# ERROR NMF: {e}")

    # FastICA
    try:
        model = FastICA(n_components=2, random_state=42)
        model, fit_time = time_fit(model, X, y)
        t0 = time.perf_counter()
        components = model.transform(X)
        pred_time = time.perf_counter() - t0
        score = float(kurtosis(components[:, 0]))
        emit("FastICA", dataset_name, "kurtosis_first_component", score, fit_time, pred_time)
    except Exception as e:
        print(f"# ERROR FastICA: {e}")


# ---------------------------------------------------------------------------
# Clustering benchmarks
# ---------------------------------------------------------------------------

def run_clustering(data):
    X = data["X_full"]
    y = data["y_full"]
    dataset_name = "iris"

    clusterers = []

    clusterers.append(
        ("KMeans", KMeans(n_clusters=3, n_init=10, random_state=42))
    )
    clusterers.append(("AgglomerativeClustering", AgglomerativeClustering(n_clusters=3)))
    clusterers.append(("DBSCAN", DBSCAN(eps=0.5, min_samples=5)))
    clusterers.append(
        ("SpectralClustering", SpectralClustering(n_clusters=3, random_state=42))
    )
    clusterers.append(("MeanShift", MeanShift()))
    clusterers.append(("Birch", Birch(n_clusters=3)))
    clusterers.append(("AffinityPropagation", AffinityPropagation(random_state=42)))
    clusterers.append(("OPTICS", OPTICS(min_samples=5)))

    for name, model in clusterers:
        try:
            model, fit_time = time_fit(model, X, y)
            t0 = time.perf_counter()
            labels = model.fit_predict(X) if not hasattr(model, "labels_") else model.labels_
            pred_time = time.perf_counter() - t0
            labels = model.labels_ if hasattr(model, "labels_") else model.predict(X)
            score = adjusted_rand_score(y, labels)
            emit(name, dataset_name, "adjusted_rand_score", score, fit_time, pred_time)
        except Exception as e:
            print(f"# ERROR {name} clustering: {e}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("# Comprehensive scikit-learn benchmark")
    print("# Format: RESULT|algorithm|dataset|metric|score|fit_time|pred_time")

    # --- Classification ---
    print("\n# === CLASSIFICATION (iris) ===")
    iris_data = load_classification_data("iris")
    run_classification("iris", iris_data)

    print("\n# === CLASSIFICATION (digits) ===")
    digits_data = load_classification_data("digits")
    run_classification("digits", digits_data)

    # --- Regression ---
    print("\n# === REGRESSION (diabetes) ===")
    diabetes_data = load_regression_data()
    run_regression(diabetes_data)

    # --- Dimensionality reduction ---
    print("\n# === DIMENSIONALITY REDUCTION (iris) ===")
    run_dim_reduction(iris_data)

    # --- Clustering ---
    print("\n# === CLUSTERING (iris) ===")
    run_clustering(iris_data)

    print("\n# Benchmark complete.")


if __name__ == "__main__":
    main()
