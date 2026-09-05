# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 10.51× | 76.1% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 5.94× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 1.97× | 89.4% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 9.07× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 25.40× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 73.85× | 78.2% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 13.96× | 83.6% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 15.08× | 75.5% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 1.14× | 76.1% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 4.29× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 2.96× | 89.4% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 1.90× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 1.82× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 4.41× | 78.2% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 1.56× | 83.6% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 12.84× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 2.60× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 8.55× | 75.9% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 1.98× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 3.79× | 100% |
| mixed | 11 | 7.13× | 100% |
| python-bound | 4 | 26.55× | 100% |
