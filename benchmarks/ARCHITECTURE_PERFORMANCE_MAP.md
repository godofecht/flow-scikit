# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 18.27× | 77.1% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 0.61× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 0.15× | 88.1% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 3.95× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 10.05× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 41.14× | 77.9% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 7.62× | 84.1% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 9.27× | 77.3% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 4.81× | 77.1% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 0.21× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 0.07× | 88.1% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 0.24× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 0.34× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 0.80× | 77.9% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 0.21× | 84.1% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 5.60× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 0.01× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 5.98× | 75.9% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 0.11× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 0.26× | 0% |
| mixed | 11 | 4.69× | 55% |
| python-bound | 4 | 14.20× | 75% |
