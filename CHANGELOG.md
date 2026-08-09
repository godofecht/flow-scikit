# Changelog

## 0.2.0

- Added IsotonicRegression (pool-adjacent-violators algorithm)
- Added TSNE (t-SNE with binary search for perplexity calibration)
- Added KernelRidge (linear, polynomial, RBF, sigmoid kernels)
- Added PLSRegression (NIPALS algorithm for cross decomposition)
- Added permutation_importance (inspection module)
- Added version module
- Added Apache-2.0 license
- Private repository setup

## 0.1.0

- Initial release
- Preprocessing: StandardScaler, MinMaxScaler, RobustScaler, MaxAbsScaler,
  Normalizer, Binarizer, OneHotEncoder, OrdinalEncoder, LabelEncoder,
  SimpleImputer, KBinsDiscretizer, PolynomialFeatures, FunctionTransformer
- Linear models: LinearRegression, LogisticRegression, Ridge, Lasso,
  ElasticNet, SGDClassifier, SGDRegressor, MultiClassLogisticRegression
- Neighbors: KNNClassifier, KNNRegressor
- SVM: LinearSVC, LinearSVR, KernelSVC
- Tree: DecisionTreeClassifier, DecisionTreeRegressor
- Naive Bayes: GaussianNB
- Ensemble: RandomForest, Bagging, Voting, GradientBoosting, AdaBoost
- Clustering: KMeans, DBSCAN, AgglomerativeClustering
- Decomposition: PCA
- Metrics: accuracy, precision/recall/f1, classification_report,
  confusion_matrix, roc_curve, roc_auc, precision_recall_curve,
  log_loss, cohen_kappa, matthews_corrcoef, hinge_loss,
  balanced_accuracy, fbeta_score, MSE, RMSE, MAE, R2,
  explained_variance
- Model selection: train_test_split, cross_validate, GridSearchCV,
  RandomizedSearchCV, KFold, StratifiedKFold, ShuffleSplit,
  learning_curve, validation_curve
- Feature selection: SelectKBest, VarianceThreshold, SelectFromModel
- Calibration: calibration_curve with Clopper-Pearson CI
- Pipeline with clone-in-init
- Progress effect system for GridSearchCV
