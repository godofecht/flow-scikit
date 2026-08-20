# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 11.79× | 76.3% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 0.70× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 0.15× | 89.1% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 6.07× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 9.43× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 36.35× | 78.0% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 6.33× | 83.7% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 9.47× | 77.1% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 0.29× | 76.3% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 0.23× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 0.06× | 89.1% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 0.51× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 0.32× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 0.70× | 78.0% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 0.16× | 83.7% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 5.77× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 0.96× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 6.41× | 75.7% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 0.12× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 0.29× | 0% |
| mixed | 11 | 3.85× | 45% |
| python-bound | 4 | 13.07× | 75% |
