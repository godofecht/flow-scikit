# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 9.15× | 76.3% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 0.68× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 0.69× | 88.7% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 5.25× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 8.53× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 37.26× | 77.7% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 5.70× | 84.0% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 9.15× | 75.9% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 0.25× | 76.3% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 0.28× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 0.61× | 88.7% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 0.50× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 0.31× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 0.65× | 77.7% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 0.15× | 84.0% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 5.25× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 0.89× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 5.25× | 75.5% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 0.17× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 0.56× | 0% |
| mixed | 11 | 3.29× | 45% |
| python-bound | 4 | 13.08× | 75% |
