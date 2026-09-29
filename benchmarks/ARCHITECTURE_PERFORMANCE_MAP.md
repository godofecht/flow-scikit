# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 10.68× | 76.3% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 4.34× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 3.07× | 89.3% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 17.79× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 10.64× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 94.46× | 77.8% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 15.83× | 84.1% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 21.72× | 76.8% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 2.75× | 76.3% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 2.21× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 1.23× | 89.3% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 1.21× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 2.68× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 2.49× | 77.8% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 1.64× | 84.1% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 6.24× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 6.20× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 7.03× | 75.0% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 2.62× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 2.71× | 100% |
| mixed | 11 | 7.19× | 100% |
| python-bound | 4 | 31.23× | 100% |
