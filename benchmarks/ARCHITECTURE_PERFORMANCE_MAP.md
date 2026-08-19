# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 7.50× | 76.2% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 0.71× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 0.14× | 87.1% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 3.61× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 8.56× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 37.73× | 78.3% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 4.98× | 83.5% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 5.32× | 75.9% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 0.20× | 76.2% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 0.28× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 0.06× | 87.1% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 0.21× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 0.26× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 1.01× | 78.3% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 0.06× | 83.5% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 2.41× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 0.02× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 2.85× | 75.3% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 0.25× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 0.30× | 0% |
| mixed | 11 | 2.59× | 45% |
| python-bound | 4 | 11.62× | 100% |
