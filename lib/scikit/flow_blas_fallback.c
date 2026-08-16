/* flow_blas_fallback.c - Scalar fallback for cblas functions when BLAS is not available.
 * Used on Android where Accelerate/OpenBLAS is not linked.
 * Provides the same symbols so the generated C compiles and links.
 */
#include <stdlib.h>
#include <string.h>

#define CBLAS_ROW_MAJOR 101
#define CBLAS_NO_TRANS 111
#define CBLAS_TRANS 112

void cblas_sgemv(int order, int trans, int m, int n, float alpha,
                 const float *a, int lda, const float *x, int incx,
                 float beta, float *y, int incy) {
    if (trans == CBLAS_NO_TRANS) {
        /* y = alpha * A * x + beta * y, A is m x n */
        for (int i = 0; i < m; i++) {
            float dot = 0.0f;
            for (int j = 0; j < n; j++) dot += a[i * lda + j] * x[j * incx];
            y[i * incy] = alpha * dot + beta * y[i * incy];
        }
    } else {
        /* y = alpha * A^T * x + beta * y, A is m x n, y is length n */
        for (int j = 0; j < n; j++) y[j * incy] = beta * y[j * incy];
        for (int i = 0; i < m; i++) {
            float xi = x[i * incx];
            for (int j = 0; j < n; j++)
                y[j * incy] += alpha * a[i * lda + j] * xi;
        }
    }
}

float cblas_sdot(int n, const float *x, int incx, const float *y, int incy) {
    float r = 0.0f;
    for (int i = 0; i < n; i++) r += x[i * incx] * y[i * incy];
    return r;
}

void cblas_saxpy(int n, float alpha, const float *x, int incx, float *y, int incy) {
    for (int i = 0; i < n; i++) y[i * incy] += alpha * x[i * incx];
}

void cblas_sscal(int n, float alpha, float *x, int incx) {
    for (int i = 0; i < n; i++) x[i * incx] *= alpha;
}

void cblas_scopy(int n, const float *x, int incx, float *y, int incy) {
    for (int i = 0; i < n; i++) y[i * incy] = x[i * incx];
}

void cblas_sgemm(int order, int transa, int transb, int m, int n, int k,
                 float alpha, const float *a, int lda, const float *b, int ldb,
                 float beta, float *c, int ldc) {
    /* C = alpha * A * B + beta * C, all row-major */
    for (int i = 0; i < m; i++)
        for (int j = 0; j < n; j++)
            c[i * ldc + j] = beta * c[i * ldc + j];
    if (transa == CBLAS_NO_TRANS && transb == CBLAS_TRANS) {
        /* A is m x k, B is n x k, C = alpha * A * B^T */
        for (int i = 0; i < m; i++)
            for (int j = 0; j < n; j++) {
                float dot = 0.0f;
                for (int p = 0; p < k; p++) dot += a[i * lda + p] * b[j * ldb + p];
                c[i * ldc + j] += alpha * dot;
            }
    } else {
        /* Simple A * B, both no-trans */
        for (int i = 0; i < m; i++)
            for (int j = 0; j < n; j++) {
                float dot = 0.0f;
                for (int p = 0; p < k; p++) dot += a[i * lda + p] * b[p * ldb + j];
                c[i * ldc + j] += alpha * dot;
            }
    }
}

void cblas_dgemm(int order, int transa, int transb, int m, int n, int k,
                 double alpha, const double *a, int lda, const double *b, int ldb,
                 double beta, double *c, int ldc) {
    for (int i = 0; i < m; i++)
        for (int j = 0; j < n; j++)
            c[i * ldc + j] = beta * c[i * ldc + j];
    for (int i = 0; i < m; i++)
        for (int j = 0; j < n; j++) {
            double dot = 0.0;
            for (int p = 0; p < k; p++) dot += a[i * lda + p] * b[j * ldb + p];
            c[i * ldc + j] += alpha * dot;
        }
}

void cblas_dgemv(int order, int trans, int m, int n, double alpha,
                 const double *a, int lda, const double *x, int incx,
                 double beta, double *y, int incy) {
    if (trans == CBLAS_NO_TRANS) {
        for (int i = 0; i < m; i++) {
            double dot = 0.0;
            for (int j = 0; j < n; j++) dot += a[i * lda + j] * x[j * incx];
            y[i * incy] = alpha * dot + beta * y[i * incy];
        }
    } else {
        for (int j = 0; j < n; j++) y[j * incy] = beta * y[j * incy];
        for (int i = 0; i < m; i++) {
            double xi = x[i * incx];
            for (int j = 0; j < n; j++)
                y[j * incy] += alpha * a[i * lda + j] * xi;
        }
    }
}

double cblas_ddot(int n, const double *x, int incx, const double *y, int incy) {
    double r = 0.0;
    for (int i = 0; i < n; i++) r += x[i * incx] * y[i * incy];
    return r;
}

void flow_parallel_for(int n_tasks, void (*callback)(void *, size_t), void *ctx) {
    for (int i = 0; i < n_tasks; i++) callback(ctx, (size_t)i);
}
