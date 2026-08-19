# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 23.58× | 77.2% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 0.69× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 0.16× | 88.3% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 4.57× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 10.66× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 53.35× | 77.3% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 8.28× | 83.8% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 11.74× | 77.5% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 4.81× | 77.2% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 0.22× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 0.08× | 88.3% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 0.20× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 0.33× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 1.00× | 77.3% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 0.19× | 83.8% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 7.28× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 1.08× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 8.27× | 75.5% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 0.11× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 0.29× | 0% |
| mixed | 11 | 5.64× | 64% |
| python-bound | 4 | 18.34× | 100% |
