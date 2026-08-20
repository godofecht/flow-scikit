# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 14.22× | 76.2% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 0.69× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 0.16× | 88.9% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 6.99× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 10.79× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 51.88× | 78.1% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 8.14× | 83.1% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 12.35× | 77.0% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 2.55× | 76.2% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 0.22× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 0.08× | 88.9% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 0.48× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 0.31× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 1.00× | 78.1% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 0.19× | 83.1% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 7.22× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 1.08× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 8.58× | 75.6% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 0.11× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 0.29× | 0% |
| mixed | 11 | 4.86× | 64% |
| python-bound | 4 | 18.11× | 100% |
