# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 14.75× | 76.6% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 0.69× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 0.16× | 88.6% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 6.76× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 10.59× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 51.00× | 77.9% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 8.20× | 83.5% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 12.11× | 77.4% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 3.41× | 76.6% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 0.22× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 0.08× | 88.6% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 0.47× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 0.31× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 1.00× | 77.9% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 0.19× | 83.5% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 7.12× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 1.07× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 8.54× | 74.9% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 0.11× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 0.29× | 0% |
| mixed | 11 | 4.95× | 64% |
| python-bound | 4 | 17.81× | 100% |
