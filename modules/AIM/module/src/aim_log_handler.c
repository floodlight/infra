/****************************************************************
 *
 *        Copyright 2013,2014,2015,2016 Big Switch Networks, Inc.
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
 ****************************************************************/

#include <AIM/aim_config.h>
#include <AIM/aim_map.h>
#include <AIM/aim_error.h>
#include <AIM/aim_log.h>
#include <AIM/aim_sem.h>
#include <AIM/aim_log_handler.h>
#include <AIM/aim_memory.h>
#include <AIM/aim_string.h>

#include <unistd.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <time.h>
#include <syslog.h>
#include <errno.h>


/**
 * This lock is used to syncronized output to stdout/stderr.
 */
static aim_sem_t stdio_lock__ = NULL;

void
aim_log_handler_init(void)
{
    if(stdio_lock__ == NULL) {
        stdio_lock__ = aim_sem_create(1);
    }
}

void
aim_log_handler_denit(void)
{
    if(stdio_lock__) {
        aim_sem_destroy(stdio_lock__);
        stdio_lock__ = NULL;
    }
}

struct aim_log_handler_s {
    aim_log_handler_config_t config;
    aim_sem_t debug_lock;
    FILE* debug_fp;
};

aim_log_handler_t
aim_log_handler_create(aim_log_handler_config_t* config)
{
    aim_log_handler_t rv;

    rv = aim_zmalloc(sizeof(*rv));
    AIM_MEMCPY(&rv->config, config, sizeof(rv->config));

    if(config->debug_log_name) {
        rv->config.debug_log_name = aim_strdup(config->debug_log_name);
        rv->debug_fp = fopen(rv->config.debug_log_name, "a");
        rv->debug_lock = aim_sem_create(1);
    }

    return rv;
}

void
aim_log_handler_destroy(aim_log_handler_t handler)
{
    if(handler->config.debug_log_name) {
        aim_free(handler->config.debug_log_name);
    }

    if(handler->debug_fp) {
        fclose(handler->debug_fp);
    }

    if(handler->debug_lock) {
        aim_sem_destroy(handler->debug_lock);
    }

    aim_free(handler);
}

static void
rotate_debug_log__(aim_log_handler_t handler)
{
    struct stat fp_log_stat;
    if (stat(handler->config.debug_log_name, &fp_log_stat) != -1) {
        if (fp_log_stat.st_size >= handler->config.max_debug_log_size) {

            int debug_log_name_len = strlen(handler->config.debug_log_name);
            char* src = aim_malloc(debug_log_name_len + 16);
            char* dst = aim_malloc(debug_log_name_len + 16);

            int i;

            /* move older logs first */
            for (i = handler->config.max_debug_logs-1; i >= 1; i--) {
                sprintf(src, "%s.%d", handler->config.debug_log_name, i);
                sprintf(dst, "%s.%d", handler->config.debug_log_name, i+1);
                rename(src, dst);
            }

            /* close log, move it to .1, and open a new file */
            sprintf(dst, "%s.1", handler->config.debug_log_name);
            fclose(handler->debug_fp);
            rename(handler->config.debug_log_name, dst);
            handler->debug_fp = fopen(handler->config.debug_log_name, "a");

            aim_free(src);
            aim_free(dst);
        }
    }
}

/* prepend time to log message and flush out to debug log file */
static void
debug_log__(aim_log_handler_t handler,
            aim_log_flag_t flag, const char* str)
{
    struct timeval timeval;
    struct tm *loctime;
    char lt[128];

    if(handler->debug_fp == NULL) {
        return;
    }

    gettimeofday(&timeval, NULL);
    loctime = localtime(&timeval.tv_sec);
    strftime(lt, sizeof(lt), "%FT%T", loctime);

    aim_sem_take(handler->debug_lock);

    fprintf(handler->debug_fp, "%s.%.06d %s %s", lt,
            (int)timeval.tv_usec, aim_log_flag_name(flag), str);
    fflush(handler->debug_fp);

    rotate_debug_log__(handler);

    aim_sem_give(handler->debug_lock);
}


void
aim_log_handler_logf(void* cookie, aim_log_flag_t flag, const char* str)
{
    aim_log_handler_t handler = (aim_log_handler_t)cookie;
    uint32_t priority = handler->config.syslog_facility;
    int to_syslog = 0;

    if(!strcmp(str, "\n")) {
        return;
    }

    /* generate severity from flag */
    switch (flag) {
    case AIM_LOG_FLAG_SYSLOG_EMERG:
        to_syslog = 1;
        priority |= LOG_EMERG;
        break;
    case AIM_LOG_FLAG_SYSLOG_ALERT:
        to_syslog = 1;
        priority |= LOG_ALERT;
        break;
    case AIM_LOG_FLAG_SYSLOG_CRIT:
        to_syslog = 1;
        priority |= LOG_CRIT;
        break;
    case AIM_LOG_FLAG_SYSLOG_ERROR:
        to_syslog = 1;
        priority |= LOG_ERR;
        break;
    case AIM_LOG_FLAG_SYSLOG_WARN:
        to_syslog = 1;
        priority |= LOG_WARNING;
        break;
    case AIM_LOG_FLAG_SYSLOG_NOTICE:
        to_syslog = 1;
        priority |= LOG_NOTICE;
        break;
    case AIM_LOG_FLAG_SYSLOG_INFO:
        to_syslog = 1;
        priority |= LOG_INFO;
        break;
    case AIM_LOG_FLAG_SYSLOG_DEBUG:
        to_syslog = 1;
        priority |= LOG_DEBUG;
        break;
    default:
        to_syslog = 0;
        break;
    }

    if (to_syslog && handler->config.flags & AIM_LOG_HANDLER_FLAG_TO_SYSLOG) {
        syslog(priority, "%s", str);
    }

    if(handler->config.flags & (AIM_LOG_HANDLER_FLAG_TO_STDOUT + AIM_LOG_HANDLER_FLAG_TO_STDERR)) {
        aim_sem_take(stdio_lock__);
        if (handler->config.flags & AIM_LOG_HANDLER_FLAG_TO_STDOUT) {
            fprintf(stdout, "%s", str);
        }
        if (handler->config.flags & AIM_LOG_HANDLER_FLAG_TO_STDERR) {
            fprintf(stderr, "%s", str);
        }
        aim_sem_give(stdio_lock__);
    }

    if (handler->config.flags & AIM_LOG_HANDLER_FLAG_TO_DBGLOG) {
        debug_log__(handler, flag, str);
    }
}



static aim_log_handler_t basic_handler__ = NULL;

int
aim_log_handler_basic_init_all(const char* ident,
                           const char* debug_log,
                           int max_debug_log_size,
                           int max_debug_logs)
{
    aim_log_handler_config_t config;
    AIM_MEMSET(&config, 0, sizeof(config));

    if(isatty(1)) {
        /** Assume interactive and log to stdout */
        config.flags |= AIM_LOG_HANDLER_FLAG_TO_STDOUT;
    }
    else if(ident) {
        /** Assume daemonized and send to syslog */
        openlog(ident, LOG_PID, LOG_DAEMON);
        config.flags |= AIM_LOG_HANDLER_FLAG_TO_SYSLOG;
        config.syslog_facility = LOG_DAEMON;
    }

    if(debug_log) {
        /** Log to debug log file */
        config.flags |= AIM_LOG_HANDLER_FLAG_TO_DBGLOG;
        config.debug_log_name = aim_strdup(debug_log);
        config.max_debug_log_size = max_debug_log_size;
        config.max_debug_logs = max_debug_logs;
    }

    basic_handler__ = aim_log_handler_create(&config);
    aim_logf_set_all("{aim_log_handler}", aim_log_handler_logf, basic_handler__);
    aim_log_option_set_all(AIM_LOG_OPTION_TIMESTAMP, 0);
    return 0;
}


void
aim_log_handler_basic_denit_all(void)
{
    aim_log_pvs_set_all(&aim_pvs_stderr);
    aim_log_handler_destroy(basic_handler__);
    basic_handler__ = NULL;
}
