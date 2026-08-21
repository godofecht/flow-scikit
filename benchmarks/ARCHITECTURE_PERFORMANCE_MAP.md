# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 11.85× | 76.4% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 0.63× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 0.79× | 89.1% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 6.03× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 9.82× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 40.89× | 78.0% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 6.61× | 83.7% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 8.53× | 76.7% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 0.34× | 76.4% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 0.24× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 0.55× | 89.1% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 0.41× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 0.33× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 0.95× | 78.0% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 0.15× | 83.7% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 4.43× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 0.83× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 5.32× | 76.1% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 0.09× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 0.55× | 0% |
| mixed | 11 | 3.80× | 45% |
| python-bound | 4 | 13.70× | 75% |
