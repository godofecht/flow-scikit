# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 16.50× | 76.0% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 6.61× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 4.10× | 89.0% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 20.27× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 10.86× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 141.30× | 78.0% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 23.37× | 83.1% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 28.89× | 76.0% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 23.01× | 76.0% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 2.23× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 1.45× | 89.0% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 1.41× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 2.76× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 3.19× | 78.0% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 2.20× | 83.1% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 9.61× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 9.72× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 10.71× | 75.5% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 3.65× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 3.60× | 100% |
| mixed | 11 | 11.31× | 100% |
| python-bound | 4 | 45.75× | 100% |
