# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 16.64× | 77.1% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 6.76× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 4.10× | 88.1% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 20.02× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 11.22× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 140.96× | 77.4% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 23.60× | 83.5% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 29.24× | 78.0% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 29.87× | 77.1% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 2.23× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 1.52× | 88.1% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 1.41× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 2.83× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 3.24× | 77.4% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 2.26× | 83.5% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 10.31× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 9.94× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 10.97× | 76.0% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 3.59× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 3.65× | 100% |
| mixed | 11 | 12.03× | 100% |
| python-bound | 4 | 45.94× | 100% |
