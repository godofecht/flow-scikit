# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 12.59× | 76.5% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 0.70× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 0.14× | 88.0% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 3.73× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 8.94× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 38.79× | 78.0% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 5.69× | 83.1% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 9.16× | 77.3% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 0.38× | 76.5% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 0.28× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 0.07× | 88.0% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 0.22× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 0.31× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 0.99× | 78.0% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 0.16× | 83.1% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 5.54× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 0.97× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 5.44× | 76.1% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 0.17× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 0.30× | 0% |
| mixed | 11 | 3.51× | 45% |
| python-bound | 4 | 13.62× | 75% |
