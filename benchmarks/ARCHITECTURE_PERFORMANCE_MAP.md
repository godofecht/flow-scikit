# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 9.81× | 76.1% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 0.75× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 0.76× | 89.4% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 5.51× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 8.79× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 37.50× | 78.2% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 5.71× | 83.6% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 9.13× | 75.5% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 0.25× | 76.1% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 0.28× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 0.61× | 89.4% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 0.51× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 0.31× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 0.66× | 78.2% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 0.16× | 83.6% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 5.33× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 0.97× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 5.17× | 75.9% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 0.17× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 0.60× | 0% |
| mixed | 11 | 3.39× | 45% |
| python-bound | 4 | 13.16× | 75% |
