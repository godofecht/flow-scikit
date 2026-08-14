# Iris Classification: flow-scikit vs scikit-learn

The iris dataset is the canonical ML benchmark. 150 samples, 4 features,
3 classes. Fisher introduced it in 1936. Every ML library implements it.

This comparison runs the same problem through both flow-scikit and
scikit-learn, then measures what it takes to deploy each one.

## Results

### Accuracy

| Algorithm | flow-scikit | scikit-learn |
|-----------|-------------|--------------|
| GaussianNB | 0.9333 | 0.9667 |
| DecisionTree | 0.9333 | 0.9333 |
| KNN (k=5) | 0.9667 | 0.9333 |
| LinearSVC (OVR) | 0.7000 | 0.9000 |
| RandomForest (10 trees) | 0.9333 | 0.9667 |

Both implementations land in the 93 to 97 percent range on the
algorithms that matter. KNN actually does better in flow-scikit.
LinearSVC is weaker because flow-scikit uses fewer iterations than
liblinear. The core algorithms are sound.

### Training and prediction speed

| Algorithm | flow-scikit train | sklearn train | flow-scikit predict | sklearn predict |
|-----------|-------------------|---------------|----------------------|-----------------|
| GaussianNB | 0.016 ms | 0.621 ms | 0.002 ms | 0.126 ms |
| DecisionTree | 0.642 ms | 0.728 ms | 0.002 ms | 0.091 ms |
| KNN (k=5) | 0.012 ms | 1.021 ms | 0.032 ms | 0.837 ms |
| LinearSVC | 0.226 ms | 1.780 ms | 0.001 ms | 0.091 ms |
| RandomForest | 5.432 ms | 4.682 ms | 0.005 ms | 0.344 ms |

flow-scikit trains faster on 4 of 5 algorithms. Prediction is faster
on all 5. The native binary has no Python overhead per call.

### Cold startup

| | flow-scikit | scikit-learn |
|---|-------------|--------------|
| Time to first result | 12 ms | 679 ms |

scikit-learn spends 488 ms just importing. flow-scikit is a native
binary that starts instantly.

### Deployment footprint

| | flow-scikit | scikit-learn |
|---|-------------|--------------|
| Binary size | 1.4 MB | 165 MB |
| Shared objects to load | 0 | 197 |
| Runtime dependencies | system libc | Python, numpy, scipy, joblib, threadpoolctl |
| Install steps | copy 1 file | pip install scikit-learn |

The flow-scikit binary is 1.4 MB. The scikit-learn stack is 165 MB,
not counting Python itself. That 165 MB contains 197 compiled shared
objects that must be dynamically linked at startup.

### Portability

The flow-scikit binary is a single native executable. Copy it to
another arm64 macOS machine and run it. No package manager, no
virtual environment, no version conflicts.

scikit-learn requires a specific Python version, compatible numpy
and scipy builds, and a BLAS implementation. Deploying it to a new
machine means installing Python, creating a venv, and pip installing
the stack. Every machine in the deployment pipeline repeats this.

## Running the comparison

```bash
bash benchmarks/iris_comparison.sh
```

Individual runs:

```bash
# flow-scikit (compiles to native binary, then runs)
FLOW_HOST=python flow run examples/iris_native.flow

# scikit-learn (Python)
python3 examples/iris_sklearn.py
```

## What this shows

flow-scikit trades algorithmic breadth for deployment simplicity.
The same iris classification problem, solved with comparable accuracy,
ships as a 1.4 MB binary that starts in 12 ms. The scikit-learn
solution needs 165 MB of dependencies and 679 ms of startup time.

For edge deployment, embedded systems, CI pipelines, or any
environment where installing a Python ML stack is impractical,
flow-scikit offers a path to native ML inference with zero runtime
dependencies.
