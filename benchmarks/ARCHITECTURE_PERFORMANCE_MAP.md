# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 10.42× | 76.4% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 5.70× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 2.14× | 88.4% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 8.98× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 17.45× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 48.15× | 77.4% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 11.31× | 83.1% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 16.68× | 76.0% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 3.18× | 76.4% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 4.31× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 3.20× | 88.4% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 1.88× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 5.24× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 4.52× | 77.4% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 1.41× | 83.1% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 12.55× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 2.69× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 10.32× | 76.1% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 2.11× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 3.84× | 100% |
| mixed | 11 | 6.82× | 100% |
| python-bound | 4 | 20.47× | 100% |
