# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 14.31× | 77.5% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 0.69× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 1.08× | 86.5% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 7.27× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 11.46× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 55.89× | 78.2% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 8.41× | 83.9% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 12.29× | 77.9% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 2.62× | 77.5% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 0.22× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 0.59× | 86.5% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 0.49× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 0.32× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 1.03× | 78.2% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 0.19× | 83.9% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 7.68× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 1.10× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 8.73× | 75.7% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 0.11× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 0.65× | 25% |
| mixed | 11 | 5.00× | 64% |
| python-bound | 4 | 19.22× | 100% |
