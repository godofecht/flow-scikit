# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 14.49× | 77.2% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 0.69× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 1.04× | 88.3% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 6.79× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 10.32× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 53.25× | 78.3% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 8.34× | 84.0% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 12.11× | 77.9% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 2.51× | 77.2% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 0.22× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 0.62× | 88.3% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 0.47× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 0.31× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 1.00× | 78.3% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 0.20× | 84.0% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 7.08× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 1.07× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 8.23× | 76.5% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 0.11× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 0.64× | 25% |
| mixed | 11 | 4.80× | 64% |
| python-bound | 4 | 18.36× | 100% |
