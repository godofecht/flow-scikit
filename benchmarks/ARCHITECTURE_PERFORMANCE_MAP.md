# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 19.26× | 76.3% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 0.61× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 0.14× | 86.0% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 3.85× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 9.77× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 41.89× | 77.4% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 7.74× | 83.7% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 9.45× | 75.7% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 0.49× | 76.3% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 0.22× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 0.06× | 86.0% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 0.23× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 0.33× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 0.81× | 77.4% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 0.22× | 83.7% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 5.40× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 0.93× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 6.33× | 75.2% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 0.13× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 0.26× | 0% |
| mixed | 11 | 4.48× | 45% |
| python-bound | 4 | 14.39× | 75% |
