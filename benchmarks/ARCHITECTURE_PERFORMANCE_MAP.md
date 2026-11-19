# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 20.14× | 76.0% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 5.70× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 3.41× | 89.0% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 15.24× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 4.33× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 73.75× | 77.7% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 22.30× | 84.0% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 29.01× | 76.8% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 3.09× | 76.0% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 2.48× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 1.77× | 89.0% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 1.75× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 2.23× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 4.91× | 77.7% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 2.02× | 84.0% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 7.89× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 9.38× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 8.81× | 75.8% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 4.09× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 3.34× | 100% |
| mixed | 11 | 8.49× | 100% |
| python-bound | 4 | 28.89× | 100% |
