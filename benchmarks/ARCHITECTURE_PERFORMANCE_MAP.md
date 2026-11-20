# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 17.33× | 76.5% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 4.72× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 3.09× | 88.1% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 11.11× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 4.40× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 54.27× | 77.6% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 20.61× | 84.1% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 26.15× | 76.8% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 3.19× | 76.5% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 2.11× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 1.56× | 88.1% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 1.72× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 1.66× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 4.98× | 77.6% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 1.78× | 84.1% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 7.03× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 8.24× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 7.83× | 75.8% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 6.10× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 2.87× | 100% |
| mixed | 11 | 7.63× | 100% |
| python-bound | 4 | 23.10× | 100% |
