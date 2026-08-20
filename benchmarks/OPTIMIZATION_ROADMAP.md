# Flow optimization roadmap

Generated from committed inventory/profile/benchmark evidence.

| Rank | Estimator | Operation | Substrate | Score | Disposition | Observed Flow speedup | Hypothesis |
|---:|---|---|---|---:|---|---:|---|
| 1 | `GaussianNB` | `fit` | python-bound | 75.4 | rewrite first | 18.52× | remove Python control/validation and specialize the complete operation |
| 2 | `PCA` | `fit` | python-bound | 74.3 | rewrite first | 9.47× | remove Python control/validation and specialize the complete operation |
| 3 | `LogisticRegression` | `predict` | python-bound | 73.6 | rewrite first | 6.04× | remove Python control/validation and specialize the complete operation |
| 4 | `GaussianNB` | `predict` | python-bound | 73.6 | rewrite first | 18.52× | remove Python control/validation and specialize the complete operation |
| 5 | `PCA` | `transform` | python-bound | 73.3 | rewrite first | 9.47× | remove Python control/validation and specialize the complete operation |
| 6 | `LinearRegression` | `predict` | python-bound | 73.3 | rewrite first | 6.41× | remove Python control/validation and specialize the complete operation |
| 7 | `KMeans` | `fit` | mixed | 72.1 | rewrite first | 3.24× | remove Python control/validation and specialize the complete operation |
| 8 | `LogisticRegression` | `fit` | mixed | 71.8 | rewrite first | 6.04× | remove Python control/validation and specialize the complete operation |
| 9 | `LinearRegression` | `fit` | mixed | 68.5 | rewrite first | 6.41× | remove Python control/validation and specialize the complete operation |
| 10 | `KMeans` | `predict` | numpy-bound | 60.4 | rewrite first | 3.24× | remove Python control/validation and specialize the complete operation |
| 11 | `GaussianNB` | `predict_proba` | python-bound | 54.0 | rewrite first | 18.52× | remove Python control/validation and specialize the complete operation |
| 12 | `KMeans` | `transform` | python-bound | 54.0 | rewrite first | 3.24× | remove Python control/validation and specialize the complete operation |
| 13 | `LogisticRegression` | `predict_proba` | python-bound | 54.0 | rewrite first | 6.04× | remove Python control/validation and specialize the complete operation |
| 14 | `LogisticRegression` | `decision_function` | python-bound | 54.0 | rewrite first | 6.04× | remove Python control/validation and specialize the complete operation |
| 15 | `Ridge` | `fit` | python-bound | 54.0 | rewrite first | 5.77× | remove Python control/validation and specialize the complete operation |
| 16 | `Ridge` | `predict` | python-bound | 54.0 | rewrite first | 5.77× | remove Python control/validation and specialize the complete operation |
| 17 | `SVC` | `predict` | numpy-bound | 49.3 | rewrite first | 0.11× | remove Python control/validation and specialize the complete operation |
| 18 | `DecisionTreeClassifier` | `fit` | mixed | 48.0 | compile whole estimator | 3.29× | retain useful numerical kernels while fusing validation, allocation and orchestration |
| 19 | `DecisionTreeClassifier` | `predict` | mixed | 48.0 | compile whole estimator | 3.29× | retain useful numerical kernels while fusing validation, allocation and orchestration |
| 20 | `RandomForestClassifier` | `fit` | mixed | 48.0 | compile whole estimator | 4.87× | retain useful numerical kernels while fusing validation, allocation and orchestration |
| 21 | `RandomForestClassifier` | `predict` | mixed | 48.0 | compile whole estimator | 4.87× | retain useful numerical kernels while fusing validation, allocation and orchestration |
| 22 | `RandomForestClassifier` | `predict_proba` | mixed | 48.0 | compile whole estimator | 4.87× | retain useful numerical kernels while fusing validation, allocation and orchestration |
| 23 | `AdaBoostRegressor` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 24 | `AdditiveChi2Sampler` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 25 | `AdditiveChi2Sampler` | `transform` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 26 | `AgglomerativeClustering` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 27 | `BaggingClassifier` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 28 | `BaggingClassifier` | `predict_proba` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 29 | `BaggingClassifier` | `decision_function` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 30 | `BaggingRegressor` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 31 | `BaggingRegressor` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 32 | `BayesianGaussianMixture` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 33 | `BayesianGaussianMixture` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 34 | `BayesianGaussianMixture` | `predict_proba` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 35 | `BernoulliNB` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 36 | `BernoulliNB` | `predict_proba` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 37 | `Binarizer` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 38 | `Birch` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 39 | `Birch` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 40 | `Birch` | `transform` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 41 | `BisectingKMeans` | `transform` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 42 | `CCA` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 43 | `CategoricalNB` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 44 | `CategoricalNB` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 45 | `CategoricalNB` | `predict_proba` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 46 | `ClassifierChain` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 47 | `ClassifierChain` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 48 | `ClassifierChain` | `predict_proba` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 49 | `ClassifierChain` | `decision_function` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 50 | `ColumnTransformer` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 51 | `ComplementNB` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 52 | `ComplementNB` | `predict_proba` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 53 | `CountVectorizer` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 54 | `CountVectorizer` | `transform` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 55 | `DictVectorizer` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 56 | `DictVectorizer` | `transform` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 57 | `DictionaryLearning` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 58 | `DictionaryLearning` | `transform` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 59 | `ElasticNet` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 60 | `ElasticNetCV` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 61 | `ElasticNetCV` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 62 | `EllipticEnvelope` | `decision_function` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 63 | `FastICA` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 64 | `FeatureAgglomeration` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 65 | `FeatureHasher` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 66 | `FeatureUnion` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 67 | `FeatureUnion` | `transform` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 68 | `FunctionTransformer` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 69 | `FunctionTransformer` | `transform` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 70 | `GaussianMixture` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 71 | `GaussianMixture` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 72 | `GaussianMixture` | `predict_proba` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 73 | `GaussianProcessClassifier` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 74 | `GaussianProcessClassifier` | `predict_proba` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 75 | `GenericUnivariateSelect` | `transform` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 76 | `GridSearchCV` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 77 | `GridSearchCV` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 78 | `GridSearchCV` | `predict_proba` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 79 | `GridSearchCV` | `decision_function` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 80 | `GridSearchCV` | `transform` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 81 | `HashingVectorizer` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 82 | `HashingVectorizer` | `transform` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 83 | `HuberRegressor` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 84 | `Isomap` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 85 | `IsotonicRegression` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 86 | `IsotonicRegression` | `transform` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 87 | `KNeighborsClassifier` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 88 | `KNeighborsRegressor` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 89 | `KNeighborsTransformer` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 90 | `KNeighborsTransformer` | `transform` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 91 | `LabelBinarizer` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 92 | `LabelBinarizer` | `transform` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 93 | `LabelEncoder` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 94 | `LabelEncoder` | `transform` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 95 | `LabelPropagation` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 96 | `Lars` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 97 | `LarsCV` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 98 | `LassoCV` | `fit` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 99 | `LassoCV` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
| 100 | `LassoLars` | `predict` | python-bound | 46.5 | rewrite first |  | remove Python control/validation and specialize the complete operation |
