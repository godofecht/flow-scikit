# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 10.84× | 76.9% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 0.62× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 0.14× | 88.0% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 3.73× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 8.97× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 38.12× | 78.2% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 4.24× | 84.0% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 4.76× | 77.3% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 2.11× | 76.9% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 0.22× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 0.06× | 88.0% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 0.21× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 0.26× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 0.80× | 78.2% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 0.03× | 84.0% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 1.90× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 0.02× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 2.58× | 76.1% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 0.13× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 0.26× | 0% |
| mixed | 11 | 3.01× | 55% |
| python-bound | 4 | 11.39× | 75% |
