# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 11.55× | 76.5% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 0.60× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 0.87× | 89.1% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 5.91× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 9.65× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 39.89× | 78.2% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 6.79× | 83.5% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 9.13× | 77.3% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 2.96× | 76.5% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 0.21× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 0.61× | 89.1% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 0.55× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 0.31× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 0.79× | 78.2% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 0.17× | 83.5% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 5.40× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 0.96× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 6.31× | 74.6% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 0.11× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 0.57× | 0% |
| mixed | 11 | 4.11× | 55% |
| python-bound | 4 | 13.80× | 75% |
