# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 13.72× | 76.2% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 0.70× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 0.16× | 88.8% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 4.24× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 9.59× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 21.83× | 77.8% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 4.97× | 83.5% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 5.55× | 76.3% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 2.18× | 76.2% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 0.22× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 0.07× | 88.8% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 0.18× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 0.26× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 0.23× | 77.8% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 0.04× | 83.5% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 2.94× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 0.02× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 3.47× | 75.4% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 0.14× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 0.28× | 0% |
| mixed | 11 | 3.53× | 55% |
| python-bound | 4 | 7.64× | 75% |
