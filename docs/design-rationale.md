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

alpha and C are not reciprocals of each other. scikit-learn's `LogisticRegression` minimises the sum of the per-sample losses plus `0.5 * ||w||^2 / C`. `logistic_regression_fit` minimises the mean loss plus `0.5 * alpha * ||w||^2`. Putting the two in the same units leaves

```
alpha = 1 / (C * n_samples)
```

so the sample count is part of the conversion. `penalty_l2_from_c(C, n_samples)` in `lib/scikit/linear.flow` performs it.

Issue #408 recorded what happens when the conversion is skipped. The canonical benchmark passed a flat `penalty_l2(0.001)` on both iris and digits against scikit-learn's `C=1.0`. On iris that is 8.3x weaker than the model it was published beside, and the Flow fit carried a coefficient Frobenius norm of 9.16 against scikit-learn's 4.52 at the same accuracy. A library that asks for the penalty explicitly and then ships a benchmark that picks a number with no stated relationship to the comparison is doing the thing this page objects to.

The intercept is not penalized on either side. `logistic_regression_fit` augments theta with the bias at index `n` and applies the L2 term over `0 to n`, which leaves the bias out.

## 3. Fit returns a value

Estimator fitting returns a value. Hacker News commenter zeec123 argues `fit` should return a function from input space to output space and avoid modifying internal state.

Flow structs pass by value. Every estimator fit function returns a fitted struct.

`Pipeline` was the one exception until recently: `pipeline_fit` returned void and mutated in place, which is the single case where the criticism landed against this library rather than against scikit-learn. It now returns a fitted `Pipeline`, so the rule holds without exception.

## 4. No hidden threshold

The `predict` functions return probabilities. The `decide` functions take an explicit threshold.

For a binary target the probability is P(`classes[1]`), which is the column scikit-learn's `predict_proba` puts it in, so raising the threshold makes `classes[1]` rarer.

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

## Known gaps

A hardcoded list here went stale twice, so it no longer lives in prose. The
current gaps are the [open issues](https://github.com/godofecht/flow-scikit/issues),
each carrying verified claims and a named fix direction. This page records
positions and their reasoning; the tracker records what is missing.

## Closed since this page was written

- Issue #353: OLS coefficient inference exists. `OLSInference` exposes the residual standard error, coefficient covariance, standard errors and t statistics, computed from the QR factorization the fit already performs and checked against hand-derived values. It refuses penalized and rank-deficient fits rather than reporting a covariance that does not mean what the name promises. Logistic inference remains open for the same honesty reason: the Newton Hessian carries the penalty term.
- Issue #354: decision trees handle categorical features natively. A per-feature flag routes a column through Breiman's optimal subset split (sort levels by mean response, evaluate the k-1 contiguous partitions) with the left set stored as a 128-bit mask in the node. On a parity-of-level dataset the categorical path reaches accuracy 1.0 where any threshold on a label encoding tops out at 0.75. Forest and Bagging builders remain numeric-only for now.
- Issue #357: logistic regression offers an explicit solver choice. Newton/IRLS is available and reaches the optimum in 2 to 6 iterations where LBFGS takes 5 to 27 on low-dimensional problems; LBFGS stays the default because Newton pays O(d^2) memory and O(d^3) per iteration on wide data. On a singular Hessian the solve zeroes the dependent coordinate and takes the genuine Newton step for the reduced problem.
- Issue #355: a bootstrap cross-validator now exists. `BootstrapOOB` in `lib/scikit/model_selection.flow` implements plain out-of-bag bootstrap and names the variant, since scikit-learn removed its own `Bootstrap` class for inventing non-standard semantics under a misleading name.
- Issue #356: `pipeline_fit` now returns a fitted `Pipeline` instead of mutating.
- Issue #435: `logistic_predict_proba` returned P(`classes[0]`) while `logistic_decide` labelled a probability above the threshold `classes[1]`, so the two composed to an inverted binary label. The probability is now P(`classes[1]`).
- Issue #449: seven call sites in `model_selection.flow` and `pipeline.flow` handed `logistic_predict`'s argmax class labels to a `decide` function, which thresholds them as probabilities. For classes {0, 1} that threshold is the identity and every fixture in the repository used 0/1 labels. For classes {2, 7} both labels exceed 0.5 and every prediction came out as 7. Cross-validation now scores `logistic_predict`'s labels directly, and `pipeline_predict_proba` returns P(`classes[1]`) for a binary classifier pipeline and null where no single column is the probability.
