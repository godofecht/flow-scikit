# Design Rationale

This document records the API positions flow-scikit takes. Most of the behavior documented here falls out of the Flow language having no default arguments. It is an accident of the toolchain. The language makes hidden defaults impossible, and the project keeps it that way on purpose.

## 1. No hidden regularization

The scikit-learn `LogisticRegression` class applies L2 regularization with C=1.0 by default. The class named after logistic regression does not perform plain logistic regression. The blog post "Scikit-learn's Defaults are Wrong" by ryxcommar (2019-08-30) documents this behavior. Independent threads on Hacker News and r/datascience raise the same issue.

In flow-scikit, estimators require an explicit penalty argument. The caller writes `penalty_none()` or `penalty_l2(alpha)` explicitly.

- `linear_regression_fit` (lib/scikit/linear.flow, line 323):
  `export function linear_regression_fit(X: Matrix, y: ptr<f32>, penalty: Penalty) -> LinearRegression`

- `logistic_regression_fit` (lib/scikit/linear.flow, line 443):
  `export function logistic_regression_fit(X: Matrix, y: ptr<f32>, n_classes: i32, epochs: i32, lr: f32, penalty: Penalty) -> LogisticRegression`

## 2. Regularization strength

The parameter for regularization strength is alpha. The scikit-learn API uses C, the inverse of the penalty. The ryxcommar post complains that C is two steps removed from the textbook lambda.

The flow-scikit library uses `penalty_l2(alpha)`. This is a partial answer. As ryxcommar notes, alpha itself is one step removed from lambda.

## 3. Fit returns a value

Estimator fitting returns a value. Hacker News commenter zeec123 argues `fit` should return a function from input space to output space and avoid modifying internal state.

Flow structs pass by value. Every estimator fit function returns a fitted struct.

There is one exception. The `pipeline_fit` function in `lib/scikit/pipeline.flow` mutates state and returns void. Issue #356 tracks this divergence.

## 4. No hidden threshold

The `predict` functions return probabilities. The `decide` functions take an explicit threshold.

The codebase contains nine `*_decide` functions:
- `random_forest_classifier_decide`
- `logistic_decide`
- `sgd_classifier_decide`
- `multiclass_logistic_decide`
- `knn_classifier_decide`
- `mlp_classifier_decide`
- `pipeline_decide`
- `kernel_svc_decide`
- `linear_svc_decide`

## 5. Structured validation errors

The `ValidationResult` struct in `lib/scikit/validation.flow` carries a numeric code and a string message. The `ensure_*` validation functions share a consistent naming convention. G2 reviewers raised unhelpful error messages in both 2019 and 2024. The structured approach provides clear diagnostics.

## Known Gaps

The implementation has several known gaps:
- Issue #353: The library lacks coefficient inference. There are no p-values and no standard errors.
- Issue #354: Decision trees cannot handle categorical features natively.
- Issue #355: The project lacks a bootstrap cross-validator.
- Issue #356: The `pipeline_fit` function mutates state.
- Issue #357: The optimizer supports LBFGS only. There is no Newton solver.
