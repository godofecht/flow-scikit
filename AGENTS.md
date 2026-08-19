# flow-scikit agent notes

## Flow compiler bugs and feature requests

When you encounter a Flow compiler bug or missing feature while working on this
repo, file it as an issue to the Flow compiler repo:

```
cd /Users/abhishekshivakumar/flow
gh issue create --title "..." --label "bug" --body "..."
```

Do this immediately, before continuing with workarounds. Include:

- A minimal reproduction
- Expected vs actual behavior
- The workaround you are using
- Where in flow-scikit it was discovered

Filed issues so far:
- #408: Escaped quotes in string literals cause memory corruption
- #409: Direct return of struct literal with function calls fails to compile
- #410: Reverse for loops generate incorrect step direction
- #411: export const not visible through import chain
- #412: String concatenation with + not supported
- #413: FLOW compilation failed suppresses all error diagnostics
- #414: Vectorization pragmas generate incorrect code in sensitive loops
- #421: Inline exp() in nested while loop causes bus error
- #431: Arrays of structs containing pointer fields produce invalid
  pointers after function return. Workaround: use separate arrays of
  pointers (ptr<ptr<T>>) instead of arrays of structs with pointer fields.
- #465: Non-exported functions with same name in different modules collide
  in generated C. Only one definition is emitted. Workaround: rename one.
- #469: Large programs produce incorrect code for certain functions.
  LinearSVC accuracy drops from 0.833 to 0.033 when surrounding code grows.
  Adding a comment to svm.flow changes the result. Workaround: split
  benchmarks into smaller files.
- #472: Adding prng.flow import to scikit.flow umbrella triggers incorrect
  code generation for regression and clustering. Ridge R2 jumps from 0.33
  to 0.61, KMeans iris drops from 0.80 to 0.47. Workaround: import prng.flow
  directly from cluster.flow and ensemble.flow instead of through scikit.flow.
- #547: Follow-up to #469, which is closed. Dead code in a module the program
  never calls decides whether that program corrupts its heap. Growing
  mixture.flow makes examples/regression_demo.flow SIGBUS inside malloc
  (mfm_alloc, reached from linear_regression_predict) after printing all of
  its output, 10 runs out of 10 on macOS arm64. Appending one never-called
  6-line function to mixture.flow makes it exit 0, 12 runs out of 12.
  regression_demo never calls anything in mixture.flow. Linux is unaffected;
  CI run-all is green. No workaround applied, since a dead function added to
  nudge codegen breaks again on the next edit. When an unrelated example
  starts crashing after you grow a library file, check this before assuming
  your change is wrong.

## Flow transpiler constraints (workarounds)

- No reverse `for` loops. Use `while` with explicit decrement.
- No direct `return StructLiteral { field: func() }`. Assign to locals first.
- No escaped quotes in strings. Avoid `\"` entirely.
- No string concatenation with `+`. Use sequential `print()` calls.
- No inline `exp()` in nested while loops. Extract to a helper function.
- `export const` is not transitively visible. Use numeric literals downstream.
- No scientific notation (`1e-10`). Use `0.0000000001`.
- Use `fabs((x) as f64) as f32` for absolute value.
- Use `sqrt((x) as f64) as f32` for square root.
- Use `log((x) as f64) as f32` for natural log.
- Flow structs are passed by value. Mutating functions must return the struct.
- Use generous allocation sizes (128+ bytes per struct) on arm64.

## Build and test

BLAS linkage is required. Without `FLOW_LDFLAGS` the build fails at the
link step with undefined `cblas_*` symbols.

macOS:
```
export FLOW_HOST=python
export FLOW_OPT_LEVEL=0
export FLOW_LDFLAGS="-framework Accelerate"
flow run tests/test_new_features.flow
```

Linux, matching CI:
```
export FLOW_HOST=python
export FLOW_OPT_LEVEL=0
export FLOW_LDFLAGS="-lm -lopenblas"
flow run tests/test_new_features.flow
```

Run everything the way CI does:
```
python tools/run_all.py
```

`tools/run_all.py` passes a file purely on its process exit code. A test
that prints `FAIL` and returns 0 is invisible. New tests must count
failures and `return 1` from `main`; see `tests/test_preprocessing.flow`.
Verify a new test is a real gate by deliberately breaking its assertion
and confirming a non-zero exit.

## Measuring

`flow run` writes compiled C and binaries into a single shared build
directory next to the `flow` binary, regardless of which worktree you
are in. Two processes compiling a file with the same basename overwrite
each other's executable mid-run, which surfaces as a bus error or a
wrong number in a file you did not touch. Give scratch harnesses a
unique prefix, and re-run a single file on its own before believing an
unexplained failure.

Timing on a developer machine is unreliable unless you check the load
first. Measurements taken at load average 126 on a 14-core machine
varied by 3x on the same row and reversed the sign of a comparison.
Interleave the two variants in one process, take a median of several
runs, and time an untouched estimator alongside as a control. CI's
`Scaled benchmark report` is the authority for anything published.

Substituting cblas for a scalar loop needs a work threshold. OpenBLAS
spends roughly 0.1 ms dispatching threads, so a change that is 40x
faster on digits can be 25x slower at 100 rows and 8 features. Gate on
a size product and run the original scalar path below it.

BLAS results are not bit-identical across implementations. Code verified
bit-identical on macOS Accelerate has been found to differ under OpenBLAS
on Linux, which matters wherever a threshold turns a last-ulp difference
into a different answer. Verify on the platform CI runs on before
claiming bit-identity.

## Working alongside other agents

Worktrees share one `.git`. Never run `git stash`: the stash stack is
global, and one agent's `stash pop` has already consumed another's work.
Commit to your own branch instead. Do not `git gc`, reset outside your
worktree, or touch a branch you did not create.
