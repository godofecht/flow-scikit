# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 16.43× | 76.7% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 0.70× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 0.16× | 86.5% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 3.87× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 9.15× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 38.27× | 77.8% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 7.06× | 83.7% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 9.42× | 77.4% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 0.42× | 76.7% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 0.22× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 0.07× | 86.5% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 0.21× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 0.33× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 0.92× | 77.8% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 0.20× | 83.7% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 5.57× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 0.01× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 6.08× | 75.7% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 0.12× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 0.29× | 0% |
| mixed | 11 | 3.99× | 45% |
| python-bound | 4 | 13.55× | 75% |
