# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 10.38× | 76.2% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 0.62× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 0.14× | 88.7% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 3.65× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 8.89× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 16.67× | 77.9% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 4.32× | 84.1% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 4.64× | 76.5% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 2.93× | 76.2% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 0.21× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 0.06× | 88.7% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 0.21× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 0.27× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 0.20× | 77.9% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 0.03× | 84.1% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 2.09× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 0.02× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 2.56× | 74.7% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 0.13× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 0.26× | 0% |
| mixed | 11 | 3.04× | 55% |
| python-bound | 4 | 5.90× | 75% |
