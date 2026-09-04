# Flow optimization roadmap

Generated from committed inventory/profile/benchmark evidence.

| Rank | Estimator | Operation | Substrate | Score | Disposition | Observed Flow speedup | Hypothesis |
|---:|---|---|---|---:|---|---:|---|
| 1 | `GaussianNB` | `fit` | python-bound | 75.4 | rewrite first | 31.02× | remove Python control/validation and specialize the complete operation |
| 2 | `PCA` | `fit` | python-bound | 73.9 | rewrite first | 16.66× | remove Python control/validation and specialize the complete operation |
| 3 | `LogisticRegression` | `predict` | python-bound | 73.7 | rewrite first | 5.92× | remove Python control/validation and specialize the complete operation |
| 4 | `PCA` | `transform` | python-bound | 73.4 | rewrite first | 16.66× | remove Python control/validation and specialize the complete operation |
| 5 | `GaussianNB` | `predict` | python-bound | 73.3 | rewrite first | 31.02× | remove Python control/validation and specialize the complete operation |
| 6 | `LinearRegression` | `predict` | python-bound | 72.8 | rewrite first | 8.82× | remove Python control/validation and specialize the complete operation |
| 7 | `KMeans` | `fit` | mixed | 72.0 | rewrite first | 6.66× | remove Python control/validation and specialize the complete operation |
| 8 | `LogisticRegression` | `fit` | mixed | 71.8 | rewrite first | 5.92× | remove Python control/validation and specialize the complete operation |
| 9 | `LinearRegression` | `fit` | mixed | 68.6 | rewrite first | 8.82× | remove Python control/validation and specialize the complete operation |
| 10 | `SVC` | `predict` | numpy-bound | 60.8 | rewrite first | 2.43× | remove Python control/validation and specialize the complete operation |
| 11 | `KMeans` | `predict` | numpy-bound | 59.9 | rewrite first | 6.66× | remove Python control/validation and specialize the complete operation |
| 12 | `GaussianNB` | `predict_proba` | python-bound | 54.0 | rewrite first | 31.02× | remove Python control/validation and specialize the complete operation |
| 13 | `KMeans` | `transform` | python-bound | 54.0 | rewrite first | 6.66× | remove Python control/validation and specialize the complete operation |
| 14 | `LinearSVC` | `predict` | python-bound | 54.0 | rewrite first | 5.13× | remove Python control/validation and specialize the complete operation |
| 15 | `LinearSVC` | `decision_function` | python-bound | 54.0 | rewrite first | 5.13× | remove Python control/validation and specialize the complete operation |
| 16 | `LogisticRegression` | `predict_proba` | python-bound | 54.0 | rewrite first | 5.92× | remove Python control/validation and specialize the complete operation |
| 17 | `LogisticRegression` | `decision_function` | python-bound | 54.0 | rewrite first | 5.92× | remove Python control/validation and specialize the complete operation |
| 18 | `Ridge` | `fit` | python-bound | 54.0 | rewrite first | 13.43× | remove Python control/validation and specialize the complete operation |
| 19 | `Ridge` | `predict` | python-bound | 54.0 | rewrite first | 13.43× | remove Python control/validation and specialize the complete operation |
| 20 | `Lasso` | `predict` | python-bound | 52.4 | rewrite first | 2.69× | remove Python control/validation and specialize the complete operation |
| 21 | `SVC` | `predict_proba` | python-bound | 51.2 | rewrite first | 2.43× | remove Python control/validation and specialize the complete operation |
| 22 | `SVC` | `decision_function` | python-bound | 51.2 | rewrite first | 2.43× | remove Python control/validation and specialize the complete operation |
| 23 | `DecisionTreeClassifier` | `fit` | mixed | 48.0 | compile whole estimator | 5.33× | retain useful numerical kernels while fusing validation, allocation and orchestration |
| 24 | `DecisionTreeClassifier` | `predict` | mixed | 48.0 | compile whole estimator | 5.33× | retain useful numerical kernels while fusing validation, allocation and orchestration |
| 25 | `RandomForestClassifier` | `fit` | mixed | 48.0 | compile whole estimator | 8.27× | retain useful numerical kernels while fusing validation, allocation and orchestration |
| 26 | `RandomForestClassifier` | `predict` | mixed | 48.0 | compile whole estimator | 8.27× | retain useful numerical kernels while fusing validation, allocation and orchestration |
| 27 | `RandomForestClassifier` | `predict_proba` | mixed | 48.0 | compile whole estimator | 8.27× | retain useful numerical kernels while fusing validation, allocation and orchestration |
| 28 | `AdaBoostRegressor` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 29 | `AdditiveChi2Sampler` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 30 | `AdditiveChi2Sampler` | `transform` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 31 | `AgglomerativeClustering` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 32 | `BaggingClassifier` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 33 | `BaggingClassifier` | `predict_proba` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 34 | `BaggingClassifier` | `decision_function` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 35 | `BaggingRegressor` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 36 | `BaggingRegressor` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 37 | `BayesianGaussianMixture` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 38 | `BayesianGaussianMixture` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 39 | `BayesianGaussianMixture` | `predict_proba` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 40 | `BernoulliNB` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 41 | `BernoulliNB` | `predict_proba` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 42 | `Binarizer` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 43 | `Birch` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 44 | `Birch` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 45 | `Birch` | `transform` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 46 | `BisectingKMeans` | `transform` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 47 | `CCA` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 48 | `CategoricalNB` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 49 | `CategoricalNB` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 50 | `CategoricalNB` | `predict_proba` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 51 | `ClassifierChain` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 52 | `ClassifierChain` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 53 | `ClassifierChain` | `predict_proba` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 54 | `ClassifierChain` | `decision_function` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 55 | `ColumnTransformer` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 56 | `ComplementNB` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 57 | `ComplementNB` | `predict_proba` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 58 | `CountVectorizer` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 59 | `CountVectorizer` | `transform` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 60 | `DictVectorizer` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 61 | `DictVectorizer` | `transform` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 62 | `DictionaryLearning` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 63 | `DictionaryLearning` | `transform` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 64 | `ElasticNet` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 65 | `ElasticNetCV` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 66 | `ElasticNetCV` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 67 | `EllipticEnvelope` | `decision_function` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 68 | `FastICA` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 69 | `FeatureAgglomeration` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 70 | `FeatureHasher` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 71 | `FeatureUnion` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 72 | `FeatureUnion` | `transform` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 73 | `FunctionTransformer` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 74 | `FunctionTransformer` | `transform` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 75 | `GaussianMixture` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 76 | `GaussianMixture` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 77 | `GaussianMixture` | `predict_proba` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 78 | `GaussianProcessClassifier` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 79 | `GaussianProcessClassifier` | `predict_proba` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 80 | `GenericUnivariateSelect` | `transform` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 81 | `GridSearchCV` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 82 | `GridSearchCV` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 83 | `GridSearchCV` | `predict_proba` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 84 | `GridSearchCV` | `decision_function` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 85 | `GridSearchCV` | `transform` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 86 | `HashingVectorizer` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 87 | `HashingVectorizer` | `transform` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 88 | `HuberRegressor` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 89 | `Isomap` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 90 | `IsotonicRegression` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 91 | `IsotonicRegression` | `transform` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 92 | `KNeighborsClassifier` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 93 | `KNeighborsRegressor` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 94 | `KNeighborsTransformer` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 95 | `KNeighborsTransformer` | `transform` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 96 | `LabelBinarizer` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 97 | `LabelBinarizer` | `transform` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 98 | `LabelEncoder` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 99 | `LabelEncoder` | `transform` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 100 | `LabelPropagation` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
