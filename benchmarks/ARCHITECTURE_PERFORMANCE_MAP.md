# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 13.20× | 76.5% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 5.07× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 3.05× | 88.8% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 14.82× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 8.83× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 88.32× | 78.2% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 17.08× | 83.6% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 25.97× | 76.2% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 2.75× | 76.5% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 2.28× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 1.34× | 88.8% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 1.49× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 2.52× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 2.99× | 78.2% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 2.01× | 83.6% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 7.28× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 8.08× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 7.99× | 75.5% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 3.88× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 2.94× | 100% |
| mixed | 11 | 7.51× | 100% |
| python-bound | 4 | 31.14× | 100% |
