# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 11.17× | 76.3% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 5.89× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 4.06× | 89.1% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 9.87× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 17.33× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 41.32× | 77.7% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 12.13× | 84.2% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 16.60× | 77.0% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 3.28× | 76.3% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 4.46× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 2.74× | 89.1% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 1.91× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 4.34× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 4.34× | 77.7% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 1.55× | 84.2% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 13.90× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 7.36× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 10.21× | 75.0% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 2.14× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 4.29× | 100% |
| mixed | 11 | 7.39× | 100% |
| python-bound | 4 | 19.04× | 100% |
