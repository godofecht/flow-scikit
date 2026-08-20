# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 11.60× | 76.5% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 0.60× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 0.88× | 87.8% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 5.85× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 9.84× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 40.97× | 77.3% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 6.79× | 83.9% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 9.03× | 77.2% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 2.93× | 76.5% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 0.22× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 0.62× | 87.8% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 0.56× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 0.32× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 0.79× | 77.3% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 0.17× | 83.9% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 5.46× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 0.97× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 6.26× | 74.9% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 0.11× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 0.58× | 0% |
| mixed | 11 | 4.13× | 55% |
| python-bound | 4 | 14.06× | 75% |
