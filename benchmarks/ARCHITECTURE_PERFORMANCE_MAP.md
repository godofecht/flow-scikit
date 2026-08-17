# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 11.21× | 76.1% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 0.69× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 0.14× | 89.1% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 3.53× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 9.25× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 15.37× | 77.4% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 4.17× | 84.4% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 4.87× | 77.1% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 0.24× | 76.1% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 0.22× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 0.06× | 89.1% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 0.26× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 0.28× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 0.16× | 77.4% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 0.03× | 84.4% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 2.13× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 0.02× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 2.47× | 75.8% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 0.19× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 0.28× | 0% |
| mixed | 11 | 2.88× | 45% |
| python-bound | 4 | 5.63× | 75% |
