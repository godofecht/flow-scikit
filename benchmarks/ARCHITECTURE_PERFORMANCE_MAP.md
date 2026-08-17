# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 10.61× | 77.1% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 0.61× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 0.14× | 88.2% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 3.65× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 8.88× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 17.22× | 78.3% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 4.21× | 83.8% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 4.72× | 76.9% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 2.36× | 77.1% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 0.22× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 0.06× | 88.2% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 0.21× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 0.26× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 0.20× | 78.3% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 0.03× | 83.8% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 2.10× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 0.02× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 2.51× | 75.6% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 0.13× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 0.26× | 0% |
| mixed | 11 | 2.99× | 55% |
| python-bound | 4 | 6.06× | 75% |
