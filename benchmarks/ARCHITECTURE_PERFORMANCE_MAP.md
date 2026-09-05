# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 11.43× | 76.1% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 5.96× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 2.20× | 89.4% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 9.86× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 14.90× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 48.41× | 78.2% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 13.60× | 83.6% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 16.90× | 75.5% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 1.18× | 76.1% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 4.43× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 3.27× | 89.4% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 1.95× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 5.01× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 4.43× | 78.2% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 1.79× | 83.6% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 14.24× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 2.73× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 10.57× | 75.9% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 2.20× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 3.96× | 100% |
| mixed | 11 | 6.84× | 100% |
| python-bound | 4 | 20.99× | 100% |
