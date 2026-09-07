# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 11.32× | 76.3% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 2.21× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 1.47× | 89.1% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 8.33× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 7.79× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 65.62× | 77.7% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 8.69× | 84.2% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 11.95× | 77.0% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 9.80× | 76.3% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 0.68× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 0.78× | 89.1% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 0.54× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 1.17× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 1.12× | 77.7% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 1.04× | 84.2% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 7.10× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 1.05× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 8.50× | 75.0% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 2.44× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 1.29× | 50% |
| mixed | 11 | 5.52× | 91% |
| python-bound | 4 | 21.45× | 100% |
