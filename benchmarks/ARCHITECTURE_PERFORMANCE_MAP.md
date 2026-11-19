# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 17.45× | 77.0% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 5.32× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 3.03× | 87.8% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 11.63× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 3.80× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 56.19× | 78.0% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 19.56× | 83.6% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 25.57× | 77.5% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 3.28× | 77.0% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 2.16× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 1.57× | 87.8% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 1.75× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 1.76× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 3.14× | 78.0% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 1.77× | 83.6% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 7.84× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 8.11× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 8.13× | 76.7% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 6.15× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 3.02× | 100% |
| mixed | 11 | 7.58× | 100% |
| python-bound | 4 | 23.18× | 100% |
