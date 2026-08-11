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

## Flow transpiler constraints (workarounds)

- No reverse `for` loops. Use `while` with explicit decrement.
- No direct `return StructLiteral { field: func() }`. Assign to locals first.
- No escaped quotes in strings. Avoid `\"` entirely.
- No string concatenation with `+`. Use sequential `print()` calls.
- `export const` is not transitively visible. Use numeric literals downstream.
- No scientific notation (`1e-10`). Use `0.0000000001`.
- Use `fabs((x) as f64) as f32` for absolute value.
- Use `sqrt((x) as f64) as f32` for square root.
- Use `log((x) as f64) as f32` for natural log.
- Flow structs are passed by value. Mutating functions must return the struct.
- Use generous allocation sizes (64+ bytes per struct) on arm64.

## Build and test

```
FLOW_HOST=python flow run tests/test_new_features.flow
```

Run all tests:
```
for f in tests/test_*.flow; do
  FLOW_HOST=python flow run "$f"
done
```

Run all examples:
```
for f in examples/*.flow; do
  FLOW_HOST=python flow run "$f"
done
```
