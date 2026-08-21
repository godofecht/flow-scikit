# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 10.75× | 76.4% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 0.68× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 0.74× | 87.0% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 5.49× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 8.71× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 37.18× | 78.2% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 6.06× | 84.2% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 9.21× | 77.1% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 0.28× | 76.4% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 0.22× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 0.57× | 87.0% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 0.49× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 0.29× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 0.64× | 78.2% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 0.15× | 84.2% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 5.63× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 0.92× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 5.97× | 75.6% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 0.12× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 0.55× | 0% |
| mixed | 11 | 3.57× | 45% |
| python-bound | 4 | 13.16× | 75% |
