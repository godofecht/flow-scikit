Alright, I'll allocate 32 bytes for each `CVSplit`.
Let me document the plan.

1. **Modify `GroupCVResult`**:
```flow
export struct GroupCVResult {
    splits: ptr<CVSplit>,
    n_splits: i32
}
```

2. **Modify `group_cv_result_free`**:
```flow
export function group_cv_result_free(result: GroupCVResult) -> void {
    let mut i: i32 = 0
    while i < result.n_splits {
        free(result.splits[i].train_indices as ptr<void>)
        free(result.splits[i].test_indices as ptr<void>)
        i = i + 1
    }
    free(result.splits as ptr<void>)
}
```

3. **Modify `group_kfold_split`**:
Change allocation to `let splits: ptr<CVSplit> = malloc((n_splits as i64) * 32) as ptr<CVSplit>`.
Inside the loop:
```flow
splits[split_idx] = CVSplit {
    train_indices: train_idx,
    n_train: n_train,
    test_indices: test_idx,
    n_test: n_test
}
```
Change return statement to: `return GroupCVResult { splits: splits, n_splits: n_splits }`.

4. **Modify `repeated_stratified_k_fold_split`**:
Similar changes.

5. **Modify `leave_one_group_out_split`**:
Similar changes.

6. **Modify `leave_p_group_out_split`**:
Similar changes.

7. **Update tests**:
Update `tests/test_model_selection.flow` and `tests/test_new_features.flow` to use `result.splits[i].n_train` instead of `result.n_train_arr[i]`.

8. Complete pre commit steps to make sure proper testing, verifications, reviews and reflections are done.
9. Run `python tools/run_all.py` (Wait, it currently fails because `flow` is not installed, so I will only make the code changes, no run all but try to get it right. I will run the precommit).
