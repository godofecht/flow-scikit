# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 17.17× | 76.0% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 6.34× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 4.17× | 89.0% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 20.02× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 10.98× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 141.27× | 77.9% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 26.18× | 84.0% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 30.72× | 77.1% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 24.43× | 76.0% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 2.24× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 1.54× | 89.0% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 1.41× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 2.79× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 3.25× | 77.9% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 2.23× | 84.0% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 10.31× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 9.09× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 11.17× | 76.0% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 3.61× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 3.57× | 100% |
| mixed | 11 | 11.73× | 100% |
| python-bound | 4 | 46.39× | 100% |
