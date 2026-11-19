# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 18.33× | 76.0% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 5.96× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 3.58× | 89.0% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 15.21× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 7.15× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 95.68× | 77.7% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 19.26× | 84.0% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 28.04× | 76.8% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 3.02× | 76.0% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 2.01× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 1.50× | 89.0% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 1.62× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 1.55× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 5.40× | 77.7% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 1.59× | 84.0% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 9.57× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 9.39× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 9.39× | 75.8% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 5.06× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 3.26× | 100% |
| mixed | 11 | 8.32× | 100% |
| python-bound | 4 | 34.67× | 100% |
