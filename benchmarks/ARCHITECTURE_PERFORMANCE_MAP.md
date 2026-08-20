# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 14.87× | 76.6% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 0.68× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 0.16× | 89.1% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 6.73× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 10.66× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 53.17× | 78.1% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 8.21× | 83.5% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 11.82× | 77.5% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 3.46× | 76.6% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 0.22× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 0.07× | 89.1% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 0.48× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 0.31× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 1.00× | 78.1% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 0.19× | 83.5% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 6.99× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 1.07× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 8.43× | 74.8% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 0.11× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 0.28× | 0% |
| mixed | 11 | 4.96× | 64% |
| python-bound | 4 | 18.25× | 75% |
