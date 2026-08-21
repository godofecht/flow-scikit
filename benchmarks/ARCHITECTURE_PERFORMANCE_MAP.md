# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 11.71× | 77.2% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 0.72× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 0.79× | 88.4% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 6.07× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 9.27× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 40.96× | 78.7% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 6.21× | 83.3% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 9.54× | 78.3% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 0.29× | 77.2% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 0.23× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 0.56× | 88.4% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 0.51× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 0.32× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 0.66× | 78.7% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 0.16× | 83.3% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 5.88× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 0.95× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 6.44× | 75.9% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 0.12× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 0.57× | 0% |
| mixed | 11 | 3.82× | 45% |
| python-bound | 4 | 14.26× | 75% |
