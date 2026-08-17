# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 10.16× | 76.6% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 0.63× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 0.14× | 88.9% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 3.73× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 8.85× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 17.03× | 77.8% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 4.28× | 83.6% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 4.84× | 73.8% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 2.30× | 76.6% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 0.22× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 0.06× | 88.9% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 0.21× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 0.27× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 0.20× | 77.8% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 0.03× | 83.6% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 1.88× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 0.02× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 2.59× | 75.7% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 0.13× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 0.26× | 0% |
| mixed | 11 | 2.96× | 55% |
| python-bound | 4 | 5.99× | 75% |
