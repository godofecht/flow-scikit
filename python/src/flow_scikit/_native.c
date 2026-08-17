#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdint.h>

int32_t flow_scikit_linear_fit(
    float *x_data,
    float *y_data,
    int32_t rows,
    int32_t cols,
    float *coef_out,
    float *bias_out
);

int32_t flow_scikit_ridge_fit(
    float *x_data,
    float *y_data,
    int32_t rows,
    int32_t cols,
    float alpha,
    float *coef_out,
    float *bias_out
);

int32_t flow_scikit_linear_predict(
    float *x_data,
    int32_t rows,
    int32_t cols,
    float *coef,
    float bias,
    float *out
);

static float *flow_scikit_ptr(unsigned long long address)
{
    return (float *)(uintptr_t)address;
}

static PyObject *py_linear_fit(PyObject *self, PyObject *args)
{
    unsigned long long x_address;
    unsigned long long y_address;
    unsigned long long coef_address;
    unsigned long long bias_address;
    int rows;
    int cols;

    (void)self;

    if (!PyArg_ParseTuple(
            args,
            "KKiiKK",
            &x_address,
            &y_address,
            &rows,
            &cols,
            &coef_address,
            &bias_address))
    {
        return NULL;
    }

    return PyLong_FromLong(flow_scikit_linear_fit(
        flow_scikit_ptr(x_address),
        flow_scikit_ptr(y_address),
        (int32_t)rows,
        (int32_t)cols,
        flow_scikit_ptr(coef_address),
        flow_scikit_ptr(bias_address)));
}

static PyObject *py_ridge_fit(PyObject *self, PyObject *args)
{
    unsigned long long x_address;
    unsigned long long y_address;
    unsigned long long coef_address;
    unsigned long long bias_address;
    int rows;
    int cols;
    float alpha;

    (void)self;

    if (!PyArg_ParseTuple(
            args,
            "KKiifKK",
            &x_address,
            &y_address,
            &rows,
            &cols,
            &alpha,
            &coef_address,
            &bias_address))
    {
        return NULL;
    }

    return PyLong_FromLong(flow_scikit_ridge_fit(
        flow_scikit_ptr(x_address),
        flow_scikit_ptr(y_address),
        (int32_t)rows,
        (int32_t)cols,
        alpha,
        flow_scikit_ptr(coef_address),
        flow_scikit_ptr(bias_address)));
}

static PyObject *py_linear_predict(PyObject *self, PyObject *args)
{
    unsigned long long x_address;
    unsigned long long coef_address;
    unsigned long long out_address;
    int rows;
    int cols;
    float bias;

    (void)self;

    if (!PyArg_ParseTuple(
            args,
            "KiiKfK",
            &x_address,
            &rows,
            &cols,
            &coef_address,
            &bias,
            &out_address))
    {
        return NULL;
    }

    return PyLong_FromLong(flow_scikit_linear_predict(
        flow_scikit_ptr(x_address),
        (int32_t)rows,
        (int32_t)cols,
        flow_scikit_ptr(coef_address),
        bias,
        flow_scikit_ptr(out_address)));
}

static PyMethodDef flow_scikit_methods[] = {
    {"linear_fit", py_linear_fit, METH_VARARGS, "Fit Flow LinearRegression."},
    {"ridge_fit", py_ridge_fit, METH_VARARGS, "Fit Flow Ridge regression."},
    {"linear_predict", py_linear_predict, METH_VARARGS, "Run native linear prediction."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef flow_scikit_module = {
    PyModuleDef_HEAD_INIT,
    "_flow_scikit_native",
    "Native CPython bridge for flow-scikit.",
    -1,
    flow_scikit_methods
};

PyMODINIT_FUNC PyInit__flow_scikit_native(void)
{
    return PyModule_Create(&flow_scikit_module);
}
