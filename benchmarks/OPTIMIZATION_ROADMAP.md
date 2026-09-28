# Flow optimization roadmap

Generated from committed inventory/profile/benchmark evidence.

| Rank | Estimator | Operation | Substrate | Score | Disposition | Observed Flow speedup | Hypothesis |
|---:|---|---|---|---:|---|---:|---|
| 1 | `GaussianNB` | `fit` | python-bound | 75.5 | rewrite first | 68.49× | remove Python control/validation and specialize the complete operation |
| 2 | `PCA` | `fit` | python-bound | 74.4 | rewrite first | 30.31× | remove Python control/validation and specialize the complete operation |
| 3 | `LogisticRegression` | `predict` | python-bound | 73.9 | rewrite first | 23.72× | remove Python control/validation and specialize the complete operation |
| 4 | `GaussianNB` | `predict` | python-bound | 73.7 | rewrite first | 68.49× | remove Python control/validation and specialize the complete operation |
| 5 | `LinearRegression` | `predict` | python-bound | 73.5 | rewrite first | 10.93× | remove Python control/validation and specialize the complete operation |
| 6 | `PCA` | `transform` | python-bound | 73.4 | rewrite first | 30.31× | remove Python control/validation and specialize the complete operation |
| 7 | `KMeans` | `fit` | mixed | 72.1 | rewrite first | 13.57× | remove Python control/validation and specialize the complete operation |
| 8 | `LogisticRegression` | `fit` | mixed | 71.9 | rewrite first | 23.72× | remove Python control/validation and specialize the complete operation |
| 9 | `LinearRegression` | `fit` | mixed | 68.6 | rewrite first | 10.93× | remove Python control/validation and specialize the complete operation |
| 10 | `SVC` | `predict` | numpy-bound | 62.7 | rewrite first | 2.78× | remove Python control/validation and specialize the complete operation |
| 11 | `KMeans` | `predict` | numpy-bound | 60.2 | rewrite first | 13.57× | remove Python control/validation and specialize the complete operation |
| 12 | `GaussianNB` | `predict_proba` | python-bound | 54.0 | rewrite first | 68.49× | remove Python control/validation and specialize the complete operation |
| 13 | `KMeans` | `transform` | python-bound | 54.0 | rewrite first | 13.57× | remove Python control/validation and specialize the complete operation |
| 14 | `Lasso` | `predict` | python-bound | 54.0 | rewrite first | 9.10× | remove Python control/validation and specialize the complete operation |
| 15 | `LinearSVC` | `predict` | python-bound | 54.0 | rewrite first | 4.52× | remove Python control/validation and specialize the complete operation |
| 16 | `LinearSVC` | `decision_function` | python-bound | 54.0 | rewrite first | 4.52× | remove Python control/validation and specialize the complete operation |
| 17 | `LogisticRegression` | `predict_proba` | python-bound | 54.0 | rewrite first | 23.72× | remove Python control/validation and specialize the complete operation |
| 18 | `LogisticRegression` | `decision_function` | python-bound | 54.0 | rewrite first | 23.72× | remove Python control/validation and specialize the complete operation |
| 19 | `Ridge` | `fit` | python-bound | 54.0 | rewrite first | 10.03× | remove Python control/validation and specialize the complete operation |
| 20 | `Ridge` | `predict` | python-bound | 54.0 | rewrite first | 10.03× | remove Python control/validation and specialize the complete operation |
| 21 | `SVC` | `predict_proba` | python-bound | 52.9 | rewrite first | 2.78× | remove Python control/validation and specialize the complete operation |
| 22 | `SVC` | `decision_function` | python-bound | 52.9 | rewrite first | 2.78× | remove Python control/validation and specialize the complete operation |
| 23 | `DecisionTreeClassifier` | `fit` | mixed | 48.0 | compile whole estimator | 10.75× | retain useful numerical kernels while fusing validation, allocation and orchestration |
| 24 | `DecisionTreeClassifier` | `predict` | mixed | 48.0 | compile whole estimator | 10.75× | retain useful numerical kernels while fusing validation, allocation and orchestration |
| 25 | `KernelRidge` | `fit` | mixed | 48.0 | compile whole estimator | 3.42× | retain useful numerical kernels while fusing validation, allocation and orchestration |
| 26 | `Lasso` | `fit` | mixed | 48.0 | compile whole estimator | 9.10× | retain useful numerical kernels while fusing validation, allocation and orchestration |
| 27 | `RandomForestClassifier` | `fit` | mixed | 48.0 | compile whole estimator | 6.78× | retain useful numerical kernels while fusing validation, allocation and orchestration |
| 28 | `RandomForestClassifier` | `predict` | mixed | 48.0 | compile whole estimator | 6.78× | retain useful numerical kernels while fusing validation, allocation and orchestration |
| 29 | `RandomForestClassifier` | `predict_proba` | mixed | 48.0 | compile whole estimator | 6.78× | retain useful numerical kernels while fusing validation, allocation and orchestration |
| 30 | `AdaBoostRegressor` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 31 | `AdditiveChi2Sampler` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 32 | `AdditiveChi2Sampler` | `transform` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 33 | `AgglomerativeClustering` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 34 | `BaggingClassifier` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 35 | `BaggingClassifier` | `predict_proba` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 36 | `BaggingClassifier` | `decision_function` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 37 | `BaggingRegressor` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 38 | `BaggingRegressor` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 39 | `BayesianGaussianMixture` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 40 | `BayesianGaussianMixture` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 41 | `BayesianGaussianMixture` | `predict_proba` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 42 | `BernoulliNB` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 43 | `BernoulliNB` | `predict_proba` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 44 | `Binarizer` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 45 | `Birch` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 46 | `Birch` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 47 | `Birch` | `transform` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 48 | `BisectingKMeans` | `transform` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 49 | `CCA` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 50 | `CategoricalNB` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 51 | `CategoricalNB` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 52 | `CategoricalNB` | `predict_proba` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 53 | `ClassifierChain` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 54 | `ClassifierChain` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 55 | `ClassifierChain` | `predict_proba` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 56 | `ClassifierChain` | `decision_function` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 57 | `ColumnTransformer` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 58 | `ComplementNB` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 59 | `ComplementNB` | `predict_proba` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 60 | `CountVectorizer` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 61 | `CountVectorizer` | `transform` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 62 | `DictVectorizer` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 63 | `DictVectorizer` | `transform` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 64 | `DictionaryLearning` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 65 | `DictionaryLearning` | `transform` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 66 | `ElasticNet` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 67 | `ElasticNetCV` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 68 | `ElasticNetCV` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 69 | `EllipticEnvelope` | `decision_function` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 70 | `FastICA` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 71 | `FeatureAgglomeration` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 72 | `FeatureHasher` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 73 | `FeatureUnion` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 74 | `FeatureUnion` | `transform` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 75 | `FunctionTransformer` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 76 | `FunctionTransformer` | `transform` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 77 | `GaussianMixture` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 78 | `GaussianMixture` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 79 | `GaussianMixture` | `predict_proba` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 80 | `GaussianProcessClassifier` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 81 | `GaussianProcessClassifier` | `predict_proba` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 82 | `GenericUnivariateSelect` | `transform` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 83 | `GridSearchCV` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 84 | `GridSearchCV` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 85 | `GridSearchCV` | `predict_proba` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 86 | `GridSearchCV` | `decision_function` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 87 | `GridSearchCV` | `transform` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 88 | `HashingVectorizer` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 89 | `HashingVectorizer` | `transform` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 90 | `HuberRegressor` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 91 | `Isomap` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 92 | `IsotonicRegression` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 93 | `IsotonicRegression` | `transform` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 94 | `KNeighborsClassifier` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 95 | `KNeighborsRegressor` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 96 | `KNeighborsTransformer` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 97 | `KNeighborsTransformer` | `transform` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 98 | `LabelBinarizer` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 99 | `LabelBinarizer` | `transform` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 100 | `LabelEncoder` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
