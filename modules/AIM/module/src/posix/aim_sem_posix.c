/****************************************************************
 *
 *        Copyright 2013, Big Switch Networks, Inc.
 *
 * Licensed under the Eclipse Public License, Version 1.0 (the
 * "License"); you may not use this file except in compliance
 * with the License. You may obtain a copy of the License at
 *
 *        http://www.eclipse.org/legal/epl-v10.html
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
 * either express or implied. See the License for the specific
 * language governing permissions and limitations under the
 * License.
 *
 ***************************************************************/

#include <AIM/aim_config.h>

#if AIM_CONFIG_INCLUDE_OS_POSIX == 1

#include <AIM/aim.h>
#include <AIM/aim_time.h>
#include <AIM/aim_sem.h>
#include <AIM/aim_memory.h>
#include <AIM/aim_error.h>
#include <semaphore.h>
#include <errno.h>
#include <time.h>

#include <sys/eventfd.h>
#include <unistd.h>
#include <poll.h>

struct aim_sem_s {
    sem_t sem;
    int efd;
};

#define EFD_INVALID -1
#define USES_EFD(sem) ((sem->efd != EFD_INVALID))

aim_sem_t
aim_sem_create_flags(int count, uint32_t flags)
{
    aim_sem_t s = aim_zmalloc(sizeof(*s));

    if(flags & AIM_SEM_CREATE_F_TRUE_RELATIVE_TIMEOUTS) {
        s->efd = eventfd(count, EFD_SEMAPHORE | EFD_NONBLOCK);
        if(s->efd == -1) {
            AIM_DIE("eventfd() failed - %s", strerror(errno));
        }
    }
    else {
        s->efd = EFD_INVALID;
        sem_init(&s->sem, 0, count);
    }
    return s;
}

aim_sem_t
aim_sem_create(int count)
{
    return aim_sem_create_flags(count, 0);
}


#define VALIDATE(_sem) AIM_TRUE_OR_DIE(_sem != NULL, "null semaphore passed to  %s", __func__)

void
aim_sem_destroy(aim_sem_t sem)
{
    VALIDATE(sem);

    if(USES_EFD(sem)) {
        close(sem->efd);
    } else {
        sem_destroy(&sem->sem);
    }

    aim_free(sem);
}

int
aim_sem_take(aim_sem_t sem)
{
    VALIDATE(sem);

    for(;;) {

        if(USES_EFD(sem)) {
            return aim_sem_take_timeout(sem, 0);
        }
        else {
            if(sem_wait(&sem->sem) == 0) {
                return 0;
            }
        }

        switch(errno)
            {
            case EINTR:
                break;
            case EINVAL:
                AIM_DIE("Invalid or corrupted semaphore in aim_sem_take().");
                break;
            default:
                AIM_DIE("Unhandled error condition in aim_sem_take(): errno=%s", strerror(errno));
                break;
            }
    }
}

void
aim_sem_give(aim_sem_t sem)
{
    VALIDATE(sem);

    if(USES_EFD(sem)) {
        eventfd_write(sem->efd, 1);
    }
    else {
        sem_post(&sem->sem);
    }
}


/**
 * Initialize a timespec structure for the given timeout interval.
 */
static void
timespec_init_timeout__(struct timespec* ts, uint64_t us)
{
    clock_gettime(CLOCK_REALTIME, ts);
    ts->tv_sec += (us / 1000000);
    us %= 1000000;
    ts->tv_nsec += (us*1000);
    ts->tv_sec += (ts->tv_nsec / 1000000000);
    ts->tv_nsec %= 1000000000;
}

static int
aim_sem_take_timeout_efd__(aim_sem_t sem, uint64_t usecs)
{
    AIM_TRUE_OR_DIE(USES_EFD(sem), "timeout_efd__ called when efd is not valid.");

    /** poll() with timeout (in ms) */
    struct pollfd fds;

    fds.fd = sem->efd;
    fds.events = POLLIN;
    fds.revents = 0;

    uint64_t t_start = aim_time_monotonic();
    int timeout_ms;

    if(usecs == 0) {
        /* Infinite timeout value when calling poll() */
        timeout_ms = -1;
    }
    else {
        timeout_ms = usecs / 1000;
    }

    for(;;) {

        int rv = poll(&fds, 1, timeout_ms);

        if(rv == 0) {
            /* Timed out */
            return -1;
        }
        if(rv == 1) {
            if(fds.revents & POLLIN) {
                /* Descriptor Ready */
                uint64_t v;
                if(eventfd_read(sem->efd, &v) == 0) {
                    /* Acquired. */
                    return 0;
                }
                else {
                    /**
                     * Acquired by someone else.
                     * Retry handled along with EINTR below.
                     */
                }
            }
        }
        if(rv == 1 || errno == EINTR) {
            /*
             * Calculate remaining timeout (if necessary) and retry.
             */
            if(timeout_ms != -1) {
                uint64_t now = aim_time_monotonic();
                if( (now - t_start) >= usecs ) {
                    /* Total timeout has elapsed */
                    return -1;
                }
                else {
                    /* Remaining time to wait. */
                    timeout_ms = (usecs - (now - t_start) + 999)/1000;
                }
            }
            continue;
        }
        else {
            AIM_DIE("Unexpected return value from poll(): %s", strerror(errno));
        }
    }
}



static int
aim_sem_take_timeout_sem__(aim_sem_t sem, uint64_t usecs)
{
    AIM_TRUE_OR_DIE(!USES_EFD(sem), "timout_sem__ called while EFD in use.");

    if(usecs == 0) {
        /** Normal wait */
        return aim_sem_take(sem);
    }
    else {

        struct timespec ts;
        timespec_init_timeout__(&ts, usecs);

        for(;;) {
            if(sem_timedwait(&sem->sem, &ts) == 0) {
                return 0;
            }
            switch(errno)
                {
                case EINTR:
                    break;
                case ETIMEDOUT:
                    return -1;

                case EINVAL:
                    AIM_DIE("Invalid or corrupted semaphore or the timespec was invalid in aim_sem_take_timeout().");
                    break;
                default:
                    AIM_DIE("Unhandled error condition in aim_sem_take() for errno=%{errno}", errno);
                    break;
                }
        }
    }
}

int
aim_sem_take_timeout(aim_sem_t sem, uint64_t usecs)
{
    VALIDATE(sem);
    if(USES_EFD(sem)) {
        return aim_sem_take_timeout_efd__(sem, usecs);
    }
    else {
        return aim_sem_take_timeout_sem__(sem, usecs);
    }
}

#else
int not_empty;
#endif
