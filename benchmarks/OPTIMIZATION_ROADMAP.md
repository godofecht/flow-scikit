# Flow optimization roadmap

Generated from committed inventory/profile/benchmark evidence.

Observed Flow speedup is the mean over the estimator's canonical rows of the stage that times the operation: the fit stage for `fit`, the prediction stage for `predict`, `predict_proba`, `decision_function` and `transform`. The Basis column names the stage. End-to-end totals are kept in the JSON as `end_to_end_flow_speedup` and are not used for ranking.

| Rank | Estimator | Operation | Substrate | Score | Disposition | Observed Flow speedup | Basis | Hypothesis |
|---:|---|---|---|---:|---|---:|---|---|
| 1 | `GaussianNB` | `fit` | python-bound | 75.3 | rewrite first | 65.85× | fit stage | remove Python control/validation and specialize the complete operation |
| 2 | `PCA` | `fit` | python-bound | 73.9 | rewrite first | 23.03× | fit stage | remove Python control/validation and specialize the complete operation |
| 3 | `LogisticRegression` | `predict` | python-bound | 73.8 | rewrite first | 10.09× | prediction stage | remove Python control/validation and specialize the complete operation |
| 4 | `GaussianNB` | `predict` | python-bound | 73.7 | rewrite first | 7.92× | prediction stage | remove Python control/validation and specialize the complete operation |
| 5 | `PCA` | `transform` | python-bound | 73.5 | rewrite first | 42.22× | prediction stage | remove Python control/validation and specialize the complete operation |
| 6 | `LinearRegression` | `predict` | python-bound | 73.4 | rewrite first | 76.69× | prediction stage | remove Python control/validation and specialize the complete operation |
| 7 | `KMeans` | `fit` | mixed | 72.2 | rewrite first | 10.55× | fit stage | remove Python control/validation and specialize the complete operation |
| 8 | `LogisticRegression` | `fit` | mixed | 71.7 | rewrite first | 10.37× | fit stage | remove Python control/validation and specialize the complete operation |
| 9 | `LinearRegression` | `fit` | mixed | 68.3 | rewrite first | 7.27× | fit stage | remove Python control/validation and specialize the complete operation |
| 10 | `SVC` | `predict` | numpy-bound | 63.6 | rewrite first | 3.99× | prediction stage | remove Python control/validation and specialize the complete operation |
| 11 | `KMeans` | `predict` | numpy-bound | 60.4 | rewrite first | 34.50× | prediction stage | remove Python control/validation and specialize the complete operation |
| 12 | `GaussianNB` | `predict_proba` | python-bound | 54.0 | rewrite first | 7.92× | prediction stage | remove Python control/validation and specialize the complete operation |
| 13 | `KMeans` | `transform` | python-bound | 54.0 | rewrite first | 34.50× | prediction stage | remove Python control/validation and specialize the complete operation |
| 14 | `Lasso` | `predict` | python-bound | 54.0 | rewrite first | 40.56× | prediction stage | remove Python control/validation and specialize the complete operation |
| 15 | `LinearSVC` | `predict` | python-bound | 54.0 | rewrite first | 43.98× | prediction stage | remove Python control/validation and specialize the complete operation |
| 16 | `LinearSVC` | `decision_function` | python-bound | 54.0 | rewrite first | 43.98× | prediction stage | remove Python control/validation and specialize the complete operation |
| 17 | `LogisticRegression` | `predict_proba` | python-bound | 54.0 | rewrite first | 10.09× | prediction stage | remove Python control/validation and specialize the complete operation |
| 18 | `LogisticRegression` | `decision_function` | python-bound | 54.0 | rewrite first | 10.09× | prediction stage | remove Python control/validation and specialize the complete operation |
| 19 | `Ridge` | `fit` | python-bound | 54.0 | rewrite first | 7.17× | fit stage | remove Python control/validation and specialize the complete operation |
| 20 | `Ridge` | `predict` | python-bound | 54.0 | rewrite first | 29.75× | prediction stage | remove Python control/validation and specialize the complete operation |
| 21 | `SVC` | `predict_proba` | python-bound | 54.0 | rewrite first | 3.99× | prediction stage | remove Python control/validation and specialize the complete operation |
| 22 | `SVC` | `decision_function` | python-bound | 54.0 | rewrite first | 3.99× | prediction stage | remove Python control/validation and specialize the complete operation |
| 23 | `DecisionTreeClassifier` | `fit` | mixed | 48.0 | compile whole estimator | 6.20× | fit stage | retain useful numerical kernels while fusing validation, allocation and orchestration |
| 24 | `DecisionTreeClassifier` | `predict` | mixed | 48.0 | compile whole estimator | 24.86× | prediction stage | retain useful numerical kernels while fusing validation, allocation and orchestration |
| 25 | `KernelRidge` | `fit` | mixed | 48.0 | compile whole estimator | 7.02× | fit stage | retain useful numerical kernels while fusing validation, allocation and orchestration |
| 26 | `Lasso` | `fit` | mixed | 48.0 | compile whole estimator | 7.37× | fit stage | retain useful numerical kernels while fusing validation, allocation and orchestration |
| 27 | `RandomForestClassifier` | `predict` | mixed | 48.0 | compile whole estimator | 29.81× | prediction stage | retain useful numerical kernels while fusing validation, allocation and orchestration |
| 28 | `RandomForestClassifier` | `predict_proba` | mixed | 48.0 | compile whole estimator | 29.81× | prediction stage | retain useful numerical kernels while fusing validation, allocation and orchestration |
| 29 | `AdaBoostRegressor` | `predict` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 30 | `AdditiveChi2Sampler` | `fit` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 31 | `AdditiveChi2Sampler` | `transform` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 32 | `AgglomerativeClustering` | `fit` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 33 | `BaggingClassifier` | `fit` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 34 | `BaggingClassifier` | `predict_proba` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 35 | `BaggingClassifier` | `decision_function` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 36 | `BaggingRegressor` | `fit` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 37 | `BaggingRegressor` | `predict` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 38 | `BayesianGaussianMixture` | `fit` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 39 | `BayesianGaussianMixture` | `predict` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 40 | `BayesianGaussianMixture` | `predict_proba` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 41 | `BernoulliNB` | `predict` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 42 | `BernoulliNB` | `predict_proba` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 43 | `Binarizer` | `fit` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 44 | `Birch` | `fit` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 45 | `Birch` | `predict` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 46 | `Birch` | `transform` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 47 | `BisectingKMeans` | `transform` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 48 | `CCA` | `predict` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 49 | `CategoricalNB` | `fit` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 50 | `CategoricalNB` | `predict` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 51 | `CategoricalNB` | `predict_proba` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 52 | `ClassifierChain` | `fit` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 53 | `ClassifierChain` | `predict` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 54 | `ClassifierChain` | `predict_proba` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 55 | `ClassifierChain` | `decision_function` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 56 | `ColumnTransformer` | `fit` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 57 | `ComplementNB` | `predict` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 58 | `ComplementNB` | `predict_proba` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 59 | `CountVectorizer` | `fit` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 60 | `CountVectorizer` | `transform` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 61 | `DictVectorizer` | `fit` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 62 | `DictVectorizer` | `transform` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 63 | `DictionaryLearning` | `fit` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 64 | `DictionaryLearning` | `transform` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 65 | `ElasticNet` | `predict` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 66 | `ElasticNetCV` | `fit` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 67 | `ElasticNetCV` | `predict` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 68 | `EllipticEnvelope` | `decision_function` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 69 | `FastICA` | `fit` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 70 | `FeatureAgglomeration` | `fit` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 71 | `FeatureHasher` | `fit` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 72 | `FeatureUnion` | `fit` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 73 | `FeatureUnion` | `transform` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 74 | `FunctionTransformer` | `fit` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 75 | `FunctionTransformer` | `transform` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 76 | `GaussianMixture` | `fit` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 77 | `GaussianMixture` | `predict` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 78 | `GaussianMixture` | `predict_proba` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 79 | `GaussianProcessClassifier` | `predict` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 80 | `GaussianProcessClassifier` | `predict_proba` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 81 | `GenericUnivariateSelect` | `transform` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 82 | `GridSearchCV` | `fit` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 83 | `GridSearchCV` | `predict` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 84 | `GridSearchCV` | `predict_proba` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 85 | `GridSearchCV` | `decision_function` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 86 | `GridSearchCV` | `transform` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 87 | `HashingVectorizer` | `fit` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 88 | `HashingVectorizer` | `transform` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 89 | `HuberRegressor` | `predict` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 90 | `Isomap` | `fit` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 91 | `IsotonicRegression` | `predict` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 92 | `IsotonicRegression` | `transform` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 93 | `KNeighborsClassifier` | `fit` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 94 | `KNeighborsRegressor` | `fit` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 95 | `KNeighborsTransformer` | `fit` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 96 | `KNeighborsTransformer` | `transform` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 97 | `LabelBinarizer` | `fit` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 98 | `LabelBinarizer` | `transform` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 99 | `LabelEncoder` | `fit` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
| 100 | `LabelEncoder` | `transform` | python-bound | 46.5 | rewrite first |  |  | remove Python control/validation and specialize the complete operation |
