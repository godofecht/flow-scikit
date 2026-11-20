# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 27.12× | 76.4% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 6.67× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 4.43× | 89.3% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 19.38× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 7.59× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 99.38× | 78.2% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 28.77× | 83.3% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 34.79× | 76.5% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 30.57× | 76.4% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 2.32× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 2.01× | 89.3% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 1.64× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 2.16× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 5.43× | 78.2% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 2.19× | 83.3% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 10.68× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 9.95× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 11.41× | 75.5% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 4.20× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 3.85× | 100% |
| mixed | 11 | 13.18× | 100% |
| python-bound | 4 | 37.57× | 100% |
