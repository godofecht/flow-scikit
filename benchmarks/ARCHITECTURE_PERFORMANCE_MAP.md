# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 23.53× | 76.4% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 0.66× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 0.16× | 88.9% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 4.57× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 10.59× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 52.78× | 77.9% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 8.22× | 84.4% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 12.06× | 77.3% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 5.71× | 76.4% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 0.21× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 0.08× | 88.9% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 0.20× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 0.33× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 0.98× | 77.9% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 0.19× | 84.4% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 7.26× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 1.06× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 8.24× | 75.6% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 0.11× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 0.28× | 0% |
| mixed | 11 | 5.71× | 64% |
| python-bound | 4 | 18.27× | 75% |
