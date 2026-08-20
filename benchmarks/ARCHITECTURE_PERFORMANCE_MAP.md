# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 14.53× | 76.1% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 0.70× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 0.17× | 88.8% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 7.33× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 11.65× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 55.53× | 77.7% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 8.69× | 83.7% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 12.59× | 77.2% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 2.83× | 76.1% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 0.22× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 0.08× | 88.8% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 0.47× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 0.32× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 1.00× | 77.7% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 0.19× | 83.7% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 7.33× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 1.07× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 8.66× | 75.4% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 0.11× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 0.29× | 0% |
| mixed | 11 | 5.08× | 64% |
| python-bound | 4 | 19.11× | 100% |
