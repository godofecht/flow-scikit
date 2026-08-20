# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 12.32× | 75.9% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 0.61× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 0.83× | 89.1% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 6.00× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 9.77× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 41.67× | 77.6% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 6.82× | 83.9% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 9.37× | 76.7% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 0.30× | 75.9% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 0.22× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 0.61× | 89.1% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 0.55× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 0.31× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 0.65× | 77.6% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 0.17× | 83.9% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 5.46× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 0.92× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 6.26× | 76.2% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 0.13× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 0.57× | 0% |
| mixed | 11 | 3.96× | 45% |
| python-bound | 4 | 14.29× | 75% |
