# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 15.00× | 77.0% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 0.68× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 0.99× | 87.5% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 6.88× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 10.64× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 52.07× | 78.6% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 8.06× | 83.5% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 11.78× | 77.5% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 2.68× | 77.0% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 0.22× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 0.61× | 87.5% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 0.48× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 0.31× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 1.00× | 78.6% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 0.19× | 83.5% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 6.92× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 1.11× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 8.40× | 75.7% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 0.10× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 0.63× | 0% |
| mixed | 11 | 4.90× | 64% |
| python-bound | 4 | 17.94× | 75% |
