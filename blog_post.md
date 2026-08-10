# I Rewrote scikit-learn in a Language Nobody Uses

## What I learned building a full ML library in Flow

---

Hey. So I did something kind of dumb.

I took scikit-learn, the Python library that basically everyone in machine learning has used at some point, and I rewrote a big chunk of it in a language called Flow. Flow is a statically-typed compiled language with algebraic effects, autodiff, and a C backend. It is not Python. It does not have pandas. It does not have numpy. It does not have pip install sklearn and you are done.

What it does have is a type system, manual memory management, and a compiler that turns your code into C. Which means it is fast. But it also means you have to think about things that Python just... handles for you.

I want to talk about what that was like. Not the math. The language patterns. The stuff that made me go "oh, that is interesting" and the stuff that made me go "I miss Python."

Let us get into it.

---

### Everything is a struct

In Python, you have classes. You have inheritance. You have `self`. You have `__init__` and `__repr__` and all that jazz.

Flow has structs.

```flow
export struct KMeans {
    centroids: ptr<ptr<f32>>,
    n_clusters: i32,
    n_features: i32,
    labels: ptr<i32>,
    inertia: f32,
    fitted: bool
}
```

That is it. No methods on the struct. No constructor. No inheritance. A struct is just a bag of fields with a name.

Want to create one? You use a struct literal:

```flow
return KMeans {
    centroids: centroids,
    n_clusters: n_clusters,
    n_features: n_features,
    labels: labels,
    inertia: best_inertia,
    n_iter: iter,
    fitted: true
}
```

Want to do something with it? You write a free function that takes the struct as its first argument:

```flow
export function kmeans_predict(model: KMeans, X: Matrix) -> ptr<i32> {
    // ...
}
```

This is the pattern. Every estimator in flow-scikit follows it. `kmeans_fit` returns a `KMeans`. `kmeans_predict` takes a `KMeans` and a `Matrix` and returns predictions. `kmeans_free` takes a `KMeans` and cleans up.

It is C-style API design. The struct is a handle. The functions are the interface. And honestly, once you get used to it, it is really clean. There is no hidden state. No magic methods. You can look at any function signature and know exactly what goes in and what comes out.

---

### Memory is your problem

This is the big one.

In Python, you create a list, you use it, and the garbage collector takes care of it. In Flow, you call `malloc`, you use the memory, and then you call `free`. If you forget, you leak. There is no GC coming to save you.

Every estimator in flow-scikit has a `_free` function:

```flow
export function kmeans_free(model: KMeans) -> void {
    for k in 0 to model.n_clusters {
        array_free_f32(model.centroids[k])
    }
    free(model.centroids as ptr<void>)
    free(model.labels as ptr<void>)
}
```

Every allocation has a matching deallocation. Every `array_new_f32` has an `array_free_f32`. Every `malloc` has a `free`.

This sounds tedious, and it is. But it also makes you think about ownership in a way that Python never forces you to. When a function returns a `ptr<f32>`, who owns that memory? Is it the caller's job to free it? Or is it borrowed?

The convention I settled on: if a function allocates and returns a pointer, the caller frees it. If a function takes a pointer as input, it does not free it. Simple. Not enforced by the compiler. Just discipline.

I miss garbage collection. But I also like knowing exactly when memory goes away.

---

### The extern block is your bridge to C

Flow does not have a standard library in the way Python does. No `math.sqrt`. No `random.random`. No `printf`.

What it does have is an `extern` block that lets you declare C functions:

```flow
extern {
    function malloc(size: i64) -> ptr<void>
    function calloc(n: i64, size: i64) -> ptr<void>
    function free(p: ptr<void>) -> void
    function memcpy(dst: ptr<void>, src: ptr<void>, n: i64) -> ptr<void>
    function memset(p: ptr<void>, val: i32, n: i64) -> ptr<void>
    function sqrt(x: f64) -> f64
    function exp(x: f64) -> f64
    function log(x: f64) -> f64
    function fabs(x: f64) -> f64
    function printf(fmt: string, ...) -> i32
}
```

This is how you get math functions. This is how you get random numbers. This is how you print anything at all.

The cool part is that Flow compiles to C, so these are not wrappers. You are calling the actual C functions directly. No FFI overhead. No marshalling. Just a direct call.

The uncool part is that you have to know what C functions exist and what their signatures are. And you have to get the types right. `sqrt` takes `f64`, not `f32`. So you end up writing this a lot:

```flow
sqrt(sum_sq as f64) as f32
```

Cast up to f64, call the function, cast back to f32. Every single time.

---

### Pointers everywhere

In Python, a list of lists is just `[[1, 2], [3, 4]]`. In Flow, that is a `ptr<ptr<f32>>`.

```flow
let centroids: ptr<ptr<f32>> = malloc((n_clusters as i64) * 8) as ptr<ptr<f32>>
for k in 0 to n_clusters {
    centroids[k] = array_new_f32(n_features)
}
```

You allocate an array of pointers. Each pointer points to another array. To free it, you free each inner array, then free the outer array.

```flow
for k in 0 to n.n_clusters {
    array_free_f32(centroids[k])
}
free(centroids as ptr<void>)
```

That `as ptr<void>` cast shows up constantly. `free` takes `ptr<void>`, so you have to cast whatever pointer you have to `ptr<void>` before freeing it. It is a bit noisy but it works.

The thing that surprised me is how often I needed `ptr<ptr<f32>>`. In scikit-learn, a 2D array is just a numpy array. In Flow, a Matrix is a struct with a flat `ptr<f32>` and row/col counts. But for things like centroids in KMeans or weights in a neural network, you want an array of arrays. So you end up with pointer-to-pointer patterns.

---

### Loops are simple and that is fine

Flow has two loop constructs:

```flow
for i in 0 to n {
    // i goes from 0 to n-1
}
```

```flow
for i in n - 1 down to 1 {
    // i goes from n-1 down to 1
}
```

That is it. No `range()`. No `enumerate()`. No `zip()`. No list comprehensions. No `map` or `filter`.

Want to iterate over two arrays at the same time? Use an index:

```flow
for i in 0 to n {
    let d: f32 = a[i] - b[i]
    sum = sum + d * d
}
```

Want to sort something? Write insertion sort by hand:

```flow
for i in 1 to n {
    let key: f32 = errors[i]
    let mut j: i32 = i - 1
    while j >= 0 && errors[j] > key {
        errors[j + 1] = errors[j]
        j = j - 1
    }
    errors[j + 1] = key
}
```

Is this verbose? Yes. Is it clear? Also yes. You can read exactly what the code does. There is no magic, no overloaded operators, no hidden iterations.

I actually kind of love this. In Python, `sorted(errors)` is one line and you move on. In Flow, you write the sort yourself. But you understand the sort. You wrote it. It is yours.

---

### Mutable and immutable, explicit

By default, variables in Flow are immutable:

```flow
let sum: f32 = 0.0
sum = sum + 1.0  // This would be an error
```

If you need to modify a variable, you use `mut`:

```flow
let mut sum: f32 = 0.0
sum = sum + 1.0  // Fine
```

This is a small thing but it matters. When you see `let mut` in the code, you know that variable is going to change. When you see `let` without `mut`, you know it will not. It is a form of self-documenting code.

The pattern I noticed is that loop accumulators are always `mut`:

```flow
let mut best_inertia: f32 = 1e10
let mut best_centroids: ptr<ptr<f32>> = centroids
```

While things that are computed once and passed around are just `let`:

```flow
let n_features: i32 = X.cols
let n: i32 = X.rows
```

---

### The fit, predict, free pattern

Every estimator in flow-scikit follows the same three-function pattern:

```flow
export function something_fit(X: Matrix, y: ptr<f32>, ...) -> Something
export function something_predict(model: Something, X: Matrix) -> ptr<f32>
export function something_free(model: Something) -> void
```

Fit creates the model. Predict uses it. Free destroys it.

This is not enforced by the language. There is no interface, no trait, no abstract class. It is just a convention. But it is a convention that works because the language gives you no reason to do anything fancier.

In Python, scikit-learn has a `BaseEstimator` class with `fit`, `predict`, `score`, `get_params`, `set_params`. There is a whole meta-class system for parameter introspection. In Flow, you just... write the functions. The API is the function signatures. If you want to know what parameters an estimator takes, you look at the fit function.

I found this refreshing. There is less indirection. The code you read is the code that runs.

---

### Printing is weird

In Python, you do:

```python
print(f"R2 = {r2:.4f}")
```

In Flow, you do:

```flow
print("  R2 = ")
printf("%.4f", r2)
println("")
```

Three function calls to print one line. `print` does not add a newline. `println` does. `printf` is C's printf, imported through the extern block.

There is no string formatting. No f-strings. No `.format()`. No string interpolation. If you want to print a number with specific formatting, you use `printf` with a C format string.

This is clunky. But it is also familiar to anyone who has written C. And since Flow compiles to C, it makes sense that the I/O story is basically "here is printf, good luck."

---

### What I actually learned

After writing 12,000 lines of Flow across 25 modules, here is what I think.

Flow forces you to be explicit. About memory. About types. About mutability. About everything. There is no magic. No decorators. No metaclasses. No context managers that hide setup and teardown. Every allocation is visible. Every free is visible. Every type cast is visible.

This makes the code verbose. A KMeans implementation that is 20 lines in Python is 80 lines in Flow. A t-SNE implementation that is 50 lines in Python is 200 lines in Flow.

But it also makes the code honest. You can trace every byte of memory from allocation to free. You can see every type conversion. You know exactly what the compiler is going to produce, because it is going to produce C, and you can read C.

The patterns are simple. Structs for data. Free functions for behavior. Manual memory management. Extern blocks for C interop. Explicit casts. Explicit mutability.

None of it is clever. That is the point.

---

*flow-scikit is a private project. It covers 25 modules with 50+ estimators and metrics, matching a large chunk of the scikit-learn API surface. The code is not clever. It is just typed.*
