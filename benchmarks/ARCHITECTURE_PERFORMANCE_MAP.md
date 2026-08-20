# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 14.73× | 76.6% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 0.67× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 1.01× | 89.1% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 6.94× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 10.68× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 53.47× | 77.5% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 8.30× | 83.7% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 11.52× | 76.7% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 3.28× | 76.6% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 0.22× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 0.61× | 89.1% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 0.48× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 0.31× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 1.00× | 77.5% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 0.19× | 83.7% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 7.04× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 1.09× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 8.33× | 75.8% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 0.11× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 0.63× | 25% |
| mixed | 11 | 4.95× | 64% |
| python-bound | 4 | 18.26× | 100% |
