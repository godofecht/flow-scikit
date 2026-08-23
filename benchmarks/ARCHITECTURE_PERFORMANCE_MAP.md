# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 14.60× | 76.4% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 0.67× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 1.02× | 88.4% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 6.81× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 10.51× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 53.92× | 77.4% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 8.47× | 83.1% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 11.83× | 76.0% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 2.64× | 76.4% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 0.23× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 0.63× | 88.4% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 0.47× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 0.31× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 1.00× | 77.4% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 0.19× | 83.1% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 7.31× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 1.09× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 8.52× | 76.1% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 0.11× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 0.64× | 25% |
| mixed | 11 | 4.88× | 64% |
| python-bound | 4 | 18.51× | 75% |
