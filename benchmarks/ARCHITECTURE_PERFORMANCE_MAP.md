# sklearn execution architecture × Flow performance

This report is generated from the committed inventory, mixed-stack profiles, parity-gated headline data, native-hotspot audit and optimization roadmap.

## Headline rows

| Algorithm | sklearn estimator | Dataset | Substrate | Parity | Flow/sklearn speedup | Python self share |
|---|---|---|---|---|---:|---:|
| `LogisticRegression` | `LogisticRegression` | iris | mixed | approximately equivalent | 10.71× | 76.1% |
| `LinearSVC` | `LinearSVC` | iris | external-native-bound | approximately equivalent | 5.91× |  |
| `KernelSVC_RBF` | `SVC` | iris | external-native-bound | approximately equivalent | 1.88× | 89.4% |
| `DecisionTree` | `DecisionTreeClassifier` | iris | mixed | approximately equivalent | 8.76× |  |
| `RandomForest` | `RandomForestClassifier` | iris | mixed | approximately equivalent | 15.70× |  |
| `GaussianNB` | `GaussianNB` | iris | python-bound | parity verified | 57.65× | 78.2% |
| `KMeans` | `KMeans` | iris | mixed | approximately equivalent | 11.72× | 83.6% |
| `PCA` | `PCA` | iris | python-bound | parity verified | 16.66× | 75.5% |
| `LogisticRegression` | `LogisticRegression` | digits | mixed | approximately equivalent | 1.12× | 76.1% |
| `LinearSVC` | `LinearSVC` | digits | external-native-bound | approximately equivalent | 4.35× |  |
| `KernelSVC_RBF` | `SVC` | digits | external-native-bound | approximately equivalent | 2.98× | 89.4% |
| `DecisionTree` | `DecisionTreeClassifier` | digits | mixed | approximately equivalent | 1.90× |  |
| `RandomForest` | `RandomForestClassifier` | digits | mixed | approximately equivalent | 0.85× |  |
| `GaussianNB` | `GaussianNB` | digits | python-bound | parity verified | 4.39× | 78.2% |
| `KMeans` | `KMeans` | digits | mixed | approximately equivalent | 1.59× | 83.6% |
| `Ridge` | `Ridge` | diabetes | python-bound | approximately equivalent | 13.43× |  |
| `Lasso` | `Lasso` | diabetes | mixed | approximately equivalent | 2.69× |  |
| `LinearRegression` | `LinearRegression` | diabetes | mixed | parity verified | 8.82× | 75.9% |
| `KernelRidge_RBF` | `KernelRidge` | diabetes | mixed | parity verified | 2.12× |  |

## Speedup grouped by execution substrate

| Substrate | Rows | Mean speedup | Flow win fraction |
|---|---:|---:|---:|
| external-native-bound | 4 | 3.78× | 100% |
| mixed | 11 | 6.00× | 91% |
| python-bound | 4 | 23.04× | 100% |
