# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 28.10× | 75.7% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 6.83× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 4.42× | 88.1% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 20.19× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 6.99× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 99.89× | 77.6% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 28.89× | 84.3% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 35.43× | 75.5% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 27.69× | 75.7% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 2.32× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 1.93× | 88.1% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 1.63× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 2.14× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 3.75× | 77.6% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 2.12× | 84.3% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 10.83× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 10.14× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 11.50× | 74.8% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 3.98× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 3.88× | 100% |
| mixed | 11 | 13.03× | 100% |
| python-bound | 4 | 37.48× | 100% |
