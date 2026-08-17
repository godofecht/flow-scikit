# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 13.57× | 76.4% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 0.68× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 0.15× | 88.7% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 4.19× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 9.38× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 52.23× | 78.1% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 4.79× | 84.4% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 5.50× | 76.3% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 2.31× | 76.4% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 0.22× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 0.06× | 88.7% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 0.18× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 0.26× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 1.00× | 78.1% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 0.04× | 84.4% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 2.92× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 0.02× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 3.35× | 75.5% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 0.14× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 0.28× | 0% |
| mixed | 11 | 3.48× | 55% |
| python-bound | 4 | 15.41× | 100% |
