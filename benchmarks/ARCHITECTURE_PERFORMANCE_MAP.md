# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 10.52× | 76.6% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 0.60× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 0.14× | 88.9% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 3.34× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 8.86× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 17.03× | 77.8% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 4.20× | 83.5% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 4.69× | 76.4% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 2.22× | 76.6% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 0.21× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 0.07× | 88.9% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 0.21× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 0.26× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | not parity verified | 0.20× | 77.8% |
| `KMeans` | `KMeans` | digits | mixed | not parity verified | 0.03× | 83.5% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 1.91× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 0.02× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 2.62× | 75.3% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 0.13× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 0.26× | 0% |
| mixed | 10 | 3.24× | 60% |
| python-bound | 3 | 7.88× | 100% |
