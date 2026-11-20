# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 19.67× | 77.3% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 5.65× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 3.51× | 88.0% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 15.42× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 5.44× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 75.58× | 78.7% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 21.75× | 83.7% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 30.81× | 77.8% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 3.01× | 77.3% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 2.48× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 1.72× | 88.0% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 1.74× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 2.19× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 4.74× | 78.7% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 1.94× | 83.7% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 8.27× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 9.27× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 8.82× | 76.1% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 4.59× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 3.34× | 100% |
| mixed | 11 | 8.53× | 100% |
| python-bound | 4 | 29.85× | 100% |
