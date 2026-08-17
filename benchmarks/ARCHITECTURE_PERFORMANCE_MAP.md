# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 14.02× | 76.3% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 0.70× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 0.16× | 88.7% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 4.20× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 9.63× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 22.55× | 77.5% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 4.97× | 83.4% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 5.34× | 76.7% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 2.57× | 76.3% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 0.22× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 0.07× | 88.7% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 0.18× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 0.26× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 0.23× | 77.5% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 0.04× | 83.4% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 2.85× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 0.02× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 3.44× | 75.0% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 0.14× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 0.28× | 0% |
| mixed | 11 | 3.59× | 55% |
| python-bound | 4 | 7.74× | 75% |
