# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 15.72× | 76.8% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 6.80× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 4.14× | 88.3% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 20.08× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 10.79× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 133.56× | 78.4% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 24.94× | 83.9% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 30.31× | 77.4% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 31.72× | 76.8% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 2.24× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 1.41× | 88.3% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 1.42× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 2.76× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 3.41× | 78.4% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 2.21× | 83.9% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 10.03× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 9.10× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 10.93× | 75.9% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 3.42× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 3.65× | 100% |
| mixed | 11 | 12.10× | 100% |
| python-bound | 4 | 44.33× | 100% |
