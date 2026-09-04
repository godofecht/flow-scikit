/* flow_time.c - monotonic nanosecond clock for Flow timing harnesses.
 *
 * Harnesses used to declare `timespec_get` and `TIME_UTC` directly in Flow.
 * Flow emits its own prototype for an extern, so the generated C redeclared a
 * libc function with `int64_t *` where the SDK has `struct timespec *`, and
 * declared a constant whose name is already a libc macro. Clang 17 rejects
 * both. Routing through a shim keeps the Flow side free of libc names.
 *
 * CLOCK_MONOTONIC replaces the old realtime clock. Interval timing should not
 * be able to move backwards when the system clock is stepped.
 */
#include <stdint.h>
#include <time.h>

int64_t flow_now_ns(void) {
    struct timespec ts;
    if (clock_gettime(CLOCK_MONOTONIC, &ts) != 0) {
        return 0;
    }
    return (int64_t)ts.tv_sec * 1000000000LL + (int64_t)ts.tv_nsec;
}
