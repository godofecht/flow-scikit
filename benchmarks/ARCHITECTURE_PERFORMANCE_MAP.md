# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 10.24× | 76.4% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 4.38× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 3.10× | 89.2% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 17.15× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 11.37× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 95.12× | 78.7% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 16.26× | 83.0% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 21.89× | 77.3% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 2.73× | 76.4% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 2.16× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 1.22× | 89.2% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 1.21× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 2.70× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 2.63× | 78.7% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 1.68× | 83.0% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 5.93× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 5.40× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 5.97× | 75.0% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 2.42× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 2.71× | 100% |
| mixed | 11 | 7.01× | 100% |
| python-bound | 4 | 31.39× | 100% |
