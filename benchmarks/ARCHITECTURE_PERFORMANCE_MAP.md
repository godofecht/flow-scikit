# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 11.52× | 76.4% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 0.61× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 0.14× | 85.6% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 3.69× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 8.85× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 29.14× | 77.9% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 4.12× | 84.2% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 4.74× | 77.1% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 0.24× | 76.4% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 0.22× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 0.06× | 85.6% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 0.21× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 0.26× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 0.33× | 77.9% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 0.03× | 84.2% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 2.07× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 0.02× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 2.58× | 75.1% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 0.16× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 0.26× | 0% |
| mixed | 11 | 2.88× | 45% |
| python-bound | 4 | 9.07× | 75% |
