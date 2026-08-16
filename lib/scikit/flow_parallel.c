/* flow_parallel.c - Parallel for wrapper using GCD (macOS) or pthreads (Linux).
 * Linked into Flow programs that use lib/scikit/threading.flow.
 */
#include <stdlib.h>

#ifdef __APPLE__
#include <dispatch/dispatch.h>

void flow_parallel_for(int n_tasks, void (*callback)(void *, size_t), void *ctx) {
    if (n_tasks <= 1) {
        for (int i = 0; i < n_tasks; i++) callback(ctx, (size_t)i);
        return;
    }
    dispatch_queue_t q = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0);
    dispatch_apply_f((size_t)n_tasks, q, ctx, callback);
}

#else
/* Linux/Android: simple pthreads barrier-based parallel for */
#include <pthread.h>

typedef struct {
    void (*callback)(void *, size_t);
    void *ctx;
    int n_tasks;
    int n_threads;
    pthread_mutex_t mutex;
    int next_task;
} flow_pf_state;

static void *flow_pf_worker(void *arg) {
    flow_pf_state *st = (flow_pf_state *)arg;
    for (;;) {
        pthread_mutex_lock(&st->mutex);
        int task = st->next_task++;
        pthread_mutex_unlock(&st->mutex);
        if (task >= st->n_tasks) break;
        st->callback(st->ctx, (size_t)task);
    }
    return NULL;
}

void flow_parallel_for(int n_tasks, void (*callback)(void *, size_t), void *ctx) {
    if (n_tasks <= 1) {
        for (int i = 0; i < n_tasks; i++) callback(ctx, (size_t)i);
        return;
    }
    int n_threads = n_tasks;
    if (n_threads > 8) n_threads = 8;
    flow_pf_state st;
    st.callback = callback;
    st.ctx = ctx;
    st.n_tasks = n_tasks;
    st.n_threads = n_threads;
    st.next_task = 0;
    pthread_mutex_init(&st.mutex, NULL);
    pthread_t *threads = (pthread_t *)malloc(sizeof(pthread_t) * n_threads);
    for (int i = 0; i < n_threads; i++)
        pthread_create(&threads[i], NULL, flow_pf_worker, &st);
    for (int i = 0; i < n_threads; i++)
        pthread_join(threads[i], NULL);
    free(threads);
    pthread_mutex_destroy(&st.mutex);
}
#endif
