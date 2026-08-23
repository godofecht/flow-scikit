# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 11.65× | 76.5% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 0.61× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 0.88× | 88.9% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 6.01× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 9.90× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 43.08× | 78.8% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 6.71× | 84.0% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 9.64× | 77.3% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 2.77× | 76.5% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 0.22× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 0.59× | 88.9% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 0.55× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 0.32× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 0.80× | 78.8% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 0.17× | 84.0% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 5.69× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 0.98× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 6.44× | 75.5% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 0.11× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 0.58× | 0% |
| mixed | 11 | 4.15× | 55% |
| python-bound | 4 | 14.80× | 75% |
