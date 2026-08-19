# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 14.73× | 76.5% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 0.68× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 0.16× | 88.6% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 6.96× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 10.82× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 52.52× | 77.7% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 8.33× | 84.3% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 11.95× | 76.4% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 2.60× | 76.5% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 0.22× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 0.08× | 88.6% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 0.48× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 0.31× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 1.00× | 77.7% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 0.19× | 84.3% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 7.29× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 1.08× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 8.70× | 75.7% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 0.11× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 0.28× | 0% |
| mixed | 11 | 4.94× | 64% |
| python-bound | 4 | 18.19× | 100% |
