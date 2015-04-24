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
 ****************************************************************/

/******************************************************************************
 *
 *  /module/src/aim_log.c
 *
 *  AIM Logger
 *
 *****************************************************************************/
#include <AIM/aim_config.h>
#include <AIM/aim.h>
#include <AIM/aim_utils.h>
#include <AIM/aim_rl.h>
#include "aim_util.h"

#define AIM_LOG_MODULE_NAME aim
#include <AIM/aim_log.h>

#if AIM_CONFIG_LOG_INCLUDE_ENV_VARIABLES == 1
static void aim_log_env_init__(aim_log_t* l);
#endif


/**
 * All registered modules.
 */
static aim_log_t* aim_log_list__;

#define AIM_LOG_FOREACH(_lobj) \
    for(_lobj = aim_log_list__; _lobj; _lobj = _lobj->next)

/**
 * Find a module.
 */
aim_log_t*
aim_log_find(const char* name)
{
    aim_log_t* aml;
    AIM_LOG_FOREACH(aml) {
        if(!AIM_STRCMP(aml->name, name)) {
            return aml;
        }
    }
    return NULL;
}

/**
 * Register a module.
 */
void
aim_log_register(aim_log_t* log)
{
    /** Make sure we only register once */
    aim_log_t* aml;
    AIM_LOG_FOREACH(aml) {
        if(aml == log) {
            /* Already registered */
            return;
        }
    }

    /* Add to list */
    log->next = aim_log_list__;
    aim_log_list__ = log;

#if AIM_CONFIG_LOG_INCLUDE_ENV_VARIABLES == 1
    aim_log_env_init__(log);
#endif

}

/**
 * Get the global log list.
 */
aim_log_t*
aim_log_list(void)
{
    return aim_log_list__;
}

/**
 * Show log settings.
 */
void
aim_log_show(aim_log_t* lobj, aim_pvs_t* pvs)
{
    int i;
    int count;
    aim_map_si_t* map;

    aim_printf(pvs, "name: %s\n", lobj->name);
    aim_printf(pvs, "dest: %s\n", lobj->logf_desc);

    count = 0;
    aim_printf(pvs, "enabled options: ");
    /* @fixme */
    for(i = 0; i <= AIM_LOG_OPTION_TIMESTAMP; i++) {
        if(AIM_BIT_GET(lobj->options, i)) {
            aim_printf(pvs, "%s ", aim_log_option_name(i));
            count++;
        }
    }
    if(count == 0) {
        aim_printf(pvs, "none.");
    }
    aim_printf(pvs, "\n");


    count = 0;
    aim_printf(pvs, "disabled options: ");
    for(i = 0; i <= AIM_LOG_OPTION_TIMESTAMP; i++) {
        if(AIM_BIT_GET(lobj->options, i) == 0) {
            aim_printf(pvs, "%s ", aim_log_option_name(i));
            count++;
        }
    }
    if(count == 0) {
        aim_printf(pvs, "none. ");
    }
    aim_printf(pvs, "\n");

    aim_printf(pvs, "enabled: ");
    count = 0;
    for(i = 0; i < AIM_LOG_FLAG_COUNT; i++) {
        if(AIM_BIT_GET(lobj->common_flags, i)) {
            aim_printf(pvs, "%s ", aim_log_flag_name(i));
            count++;
        }
    }
    for(map = lobj->custom_map; map && map->s; map++) {
        if(AIM_BIT_GET(lobj->custom_flags, map->i)) {
            aim_printf(pvs, "%s ", map->s);
            count++;
        }
    }
    if(count == 0) {
        aim_printf(pvs, "none.");
    }
    aim_printf(pvs, "\n");

    aim_printf(pvs, "disabled: ");
    count = 0;
    for(i = 0; i < AIM_LOG_FLAG_COUNT; i++) {
        if(AIM_BIT_GET(lobj->common_flags, i) == 0) {
            aim_printf(pvs, "%s ", aim_log_flag_name(i));
            count++;
        }
    }
    for(map = lobj->custom_map; map && map->s; map++)  {
        if(AIM_BIT_GET(lobj->custom_flags, map->i) == 0) {
            aim_printf(pvs, "%s ", map->s);
            count++;
        }
    }
    if(count == 0) {
        aim_printf(pvs, "none");
    }
    aim_printf(pvs, "\n");
}

/**
 * Get the PVS; the cookie is the PVS, and each PVS supports a log function.
 */
aim_pvs_t*
aim_log_pvs_get(aim_log_t* lobj)
{
    return (lobj && lobj->logf == aim_pvs_logf) ?
        (aim_pvs_t*) lobj->log_cookie : NULL;
}

/**
 * Set the PVS; the cookie is the PVS, and each PVS supports a log function.
 */
aim_pvs_t*
aim_log_pvs_set(aim_log_t* lobj, aim_pvs_t* pvs)
{
    aim_pvs_t* rv = NULL;
    if(lobj) {
        rv = (aim_pvs_t*) lobj->log_cookie;
        lobj->logf = aim_pvs_logf;
        lobj->log_cookie = pvs;
    }
    return rv;
}
void
aim_log_pvs_set_all(aim_pvs_t* pvs)
{
    aim_log_t* lobj;
    AIM_LOG_FOREACH(lobj) {
        aim_log_pvs_set(lobj, pvs);
    }
}


/**
 * Get the log function and cookie
 */
void
aim_logf_get(aim_log_t* lobj, aim_log_f* logf, void** cookie)
{
    if(lobj) {
        *logf = lobj->logf;
        *cookie = lobj->log_cookie;
    }
}

/**
 * Set the PVS
 */
void
aim_logf_set(aim_log_t* lobj, char* desc, aim_log_f logf, void* cookie)
{
    if(lobj) {
        lobj->logf_desc = desc;
        lobj->logf = logf;
        lobj->log_cookie = cookie;
    }
}

void
aim_logf_set_all(char* desc, aim_log_f logf, void* cookie)
{
    aim_log_t* lobj;
    AIM_LOG_FOREACH(lobj) {
        aim_logf_set(lobj, desc, logf, cookie);
    }
}


/**
 * Which bits to check
 */
static int
aim_log_bits__(aim_log_t* alt, const char* flag, uint32_t* common,
               uint32_t* custom)
{
    /*
     * Check custom flags first, then common flags.
     */
    int i;
    *common = 0;
    *custom = 0;

    if(!AIM_STRCMP(flag, "all")) {
        *custom = ~0;
        *common = ~0;
        return 1;
    }

    if(alt->custom_map && aim_map_si_s(&i, flag, alt->custom_map, 0)) {
        *custom = (1 << i);
        return 1;
    }

    if(aim_map_si_s(&i, flag, aim_log_flag_map, 0)) {
        *common = (1 << i);
        return 1;
    }

    return 0;
}


/**
 * Get a log flag by name.
 */
int
aim_log_flag_get(aim_log_t* lobj, const char* flag)
{
    uint32_t common, custom;
    if(aim_log_bits__(lobj, flag, &common, &custom)) {
        if(common) {
            return (lobj->common_flags & common) ? 1 : 0;
        }
        else {
            return (lobj->custom_flags & custom) ? 1 : 0;
        }
    }
    return -1;
}

/**
 * Get a common log flag.
 */
int
aim_log_fid_get(aim_log_t* lobj, aim_log_flag_t fid)
{
    return (lobj) ? AIM_BIT_GET(lobj->common_flags, fid) : -1;
}

/**
 * Get a custom log flag.
 */
int
aim_log_custom_fid_get(aim_log_t* lobj, int fid)
{
    return (lobj) ? AIM_BIT_GET(lobj->custom_flags, fid) : -1;
}

/**
 * Set a log flag by name.
 */
int
aim_log_flag_set(aim_log_t* lobj, const char* flag, int value)
{
    uint32_t common, custom;
    if(aim_log_bits__(lobj, flag, &common, &custom)) {
        if(common) {
            AIM_BITS_SET(lobj->common_flags, common, value);
        }
        if(custom) {
            AIM_BITS_SET(lobj->custom_flags, custom, value);
        }
        return 1;
    }
    return 0;
}

int
aim_log_flag_set_all(const char* flag, int value)
{
    aim_log_t* lobj;
    AIM_LOG_FOREACH(lobj) {
        aim_log_flag_set(lobj, flag, value);
    }
    return 0;
}

/**
 * Set a common log flag.
 */
int
aim_log_fid_set(aim_log_t* lobj, aim_log_flag_t fid, int value)
{
    if(lobj) {
        AIM_BIT_SET(lobj->common_flags, fid, value);
        return 1;
    }
    return 0;
}

int
aim_log_fid_set_all(aim_log_flag_t fid, int value)
{
    aim_log_t* lobj;
    AIM_LOG_FOREACH(lobj) {
        aim_log_fid_set(lobj, fid, value);
    }
    return 0;
}

/**
 * Set a custom log flag.
 */
int
aim_log_custom_fid_set(aim_log_t* lobj, int fid, int value)
{
    if(lobj) {
        AIM_BIT_SET(lobj->custom_flags, fid, value);
        return 1;
    }
    return 0;
}

int
aim_log_custom_fid_set_all(int fid, int value)
{
    aim_log_t* lobj;
    AIM_LOG_FOREACH(lobj) {
        aim_log_custom_fid_set(lobj, fid, value);
    }
    return 0;
}

/**
 * Set a log option.
 */
int
aim_log_option_set(aim_log_t* lobj, aim_log_option_t option, int value)
{
    if(lobj) {
        AIM_BIT_SET(lobj->options, option, value);
        return 1;
    }
    return 0;
}

int
aim_log_option_set_all(aim_log_option_t option, int value)
{
    aim_log_t* lobj;
    AIM_LOG_FOREACH(lobj) {
        aim_log_option_set(lobj, option, value);
    }
    return 0;
}

/**
 * Set a log option by name.
 */
int
aim_log_option_name_set(aim_log_t* lobj, const char* name, int value)
{
    aim_log_option_t opt;
    if(aim_log_option_value(name, &opt, 0) < 0) {
        return -1;
    }
    return aim_log_option_set(lobj, opt, value);
}
int
aim_log_option_name_set_all(const char* name, int value)
{
    aim_log_t* lobj;
    AIM_LOG_FOREACH(lobj) {
        aim_log_option_name_set(lobj, name, value);
    }
    return 0;
}

/**
 * Get a log option.
 */
int
aim_log_option_get(aim_log_t* lobj, aim_log_option_t option)
{
    if(lobj) {
        return AIM_BIT_GET(lobj->options, option);
    }
    return 0;
}

/**
 * Get a log option by name.
 */
int
aim_log_option_name_get(aim_log_t* lobj, const char* name)
{
    aim_log_option_t opt;
    if(aim_log_option_value(name, &opt, 0) < 0) {
        return -1;
    }
    return aim_log_option_get(lobj, opt);
}

/**
 * Current timestamp.
 */
#if AIM_CONFIG_LOG_INCLUDE_LINUX_TIMESTAMP == 1

#include <time.h>
#include <sys/time.h>

#endif

static void
aim_log_time__(aim_pvs_t* pvs)
{
#if AIM_CONFIG_LOG_INCLUDE_LINUX_TIMESTAMP == 1
    struct timeval timeval;
    struct tm *loctime;
    char lt[128];

    gettimeofday(&timeval, NULL);
    loctime = localtime(&timeval.tv_sec);
    strftime(lt, sizeof(lt), "%m-%d %T", loctime);
    aim_printf(pvs, "%s.%.06d ", lt, (int)timeval.tv_usec);
#else
    AIM_REFERENCE(pvs);
    AIM_REFERENCE(size);
#endif
}

/**
 * Basic output function for all log messages.
 */
static void
aim_log_output__(aim_log_t* l, aim_log_flag_t flag,
                 const char* fname, const char* file,
                 int line, const char* fmt, va_list vargs)
{
    aim_pvs_t* msg;
    char* pmsg;

    if (!l->logf) {
        return;
    }

    msg = aim_pvs_buffer_create();
    if(AIM_BIT_GET(l->options, AIM_LOG_OPTION_TIMESTAMP)) {
        aim_log_time__(msg);
    }
    aim_vprintf(msg, fmt, vargs);
    if(l->options & (1 << AIM_LOG_OPTION_FUNC)) {
        aim_printf(msg, " [%s]", fname);
    }
    if(l->options & (1 << AIM_LOG_OPTION_FILE_LINE)
            || flag == AIM_LOG_FLAG_FATAL) {
        aim_printf(msg, " [%s:%d]", file, line);
    }
    aim_printf(msg, "\n");
    pmsg = aim_pvs_buffer_get(msg);
    l->logf(l->log_cookie, flag, pmsg);
    aim_free(pmsg);
    aim_pvs_destroy(msg);
}


#if AIM_CONFIG_LOG_INCLUDE_ENV_VARIABLES == 1

static void
aim_log_env_init__(aim_log_t* l)
{
    if(l->env == 0) {
        char envname[64];
        char* env;
        AIM_SNPRINTF(envname, sizeof(envname), "%s_log_flags", l->name);
        if((env = getenv(envname))) {
            int i;
            for(i = 0; aim_log_flag_map[i].s; i++) {
                if(AIM_STRSTR(env, aim_log_flag_map[i].s)) {
                    AIM_BIT_SET(l->common_flags, i, 1);
                }
            }
            if(AIM_STRSTR(env, "all")) {
                AIM_BITS_SET(l->common_flags, (1<<i)-1, 1);
            }
            for(i = 0; l->custom_map && l->custom_map[i].s; i++) {
                if(AIM_STRSTR(env, l->custom_map[i].s)) {
                    AIM_BIT_SET(l->custom_flags, i, 1);
                }
            }
            if(AIM_STRSTR(env, "all")) {
                AIM_BITS_SET(l->custom_flags, (1<<i)-1, 1);
            }
        }
        AIM_SNPRINTF(envname, sizeof(envname), "%s_log_options", l->name);
        if((env=getenv(envname))) {
            int i;
            for(i = 0; aim_log_option_map[i].s; i++) {
                if(AIM_STRSTR(env, aim_log_option_map[i].s)) {
                    AIM_BIT_SET(l->options, i, 1);
                }
            }
            if(AIM_STRSTR(env, "all")) {
                AIM_BITS_SET(l->options, (1<<i)-1, 1);
            }
        }
        l->env = 1;
    }
}

#endif

int
aim_log_enabled(aim_log_t* l, aim_log_flag_t flag)
{
#if AIM_CONFIG_LOG_INCLUDE_ENV_VARIABLES == 1
    if(l->env == 0) {
        aim_log_env_init__(l);
    }
#endif
    return (l && l->logf && AIM_BIT_GET(l->common_flags, flag));
}

int
aim_log_custom_enabled(aim_log_t* l, int fid)
{
#if AIM_CONFIG_LOG_INCLUDE_ENV_VARIABLES == 1
    if(l->env == 0) {
        aim_log_env_init__(l);
    }
#endif
    return (l && l->logf && AIM_BIT_GET(l->custom_flags, fid));
}


void
aim_log_common(aim_log_t* l, aim_log_flag_t flag,
               aim_ratelimiter_t* rl, uint64_t time,
               const char* fname, const char* file, int line,
               const char* fmt, ...)
{
    va_list vargs;
    va_start(vargs, fmt);
    aim_log_vcommon(l, flag, rl, time, fname, file, line, fmt, vargs);
    va_end(vargs);
}

void
aim_log_vcommon(aim_log_t* l, aim_log_flag_t flag,
                aim_ratelimiter_t* rl, uint64_t time,
                const char* fname, const char* file, int line,
                const char* fmt, va_list vargs)
{
    if(flag == AIM_LOG_FLAG_MSG || flag == AIM_LOG_FLAG_FATAL ||
       aim_log_enabled(l, flag)) {
        if(rl == NULL || aim_ratelimiter_limit(rl, time) == 0) {
            aim_log_output__(l, flag, fname, file, line, fmt, vargs);
        }
    }
}

void
aim_log_custom(aim_log_t* l, int fid,
               aim_ratelimiter_t* rl, uint64_t time,
               const char* fname, const char* file, int line,
               const char* fmt, ...)
{
    va_list vargs;
    va_start(vargs, fmt);
    aim_log_vcustom(l, fid, rl, time, fname, file, line, fmt, vargs);
    va_end(vargs);
}


void
aim_log_vcustom(aim_log_t* l, int fid,
                aim_ratelimiter_t* rl, uint64_t time,
                const char* fname, const char* file, int line,
                const char* fmt, va_list vargs)
{
    if(aim_log_custom_enabled(l, fid)) {
        if(rl == NULL || aim_ratelimiter_limit(rl, time) == 0) {
            aim_log_output__(l, AIM_LOG_FLAG_INFO,
                             fname, file, line, fmt, vargs);
        }
    }
}


int
aim_log_syslog_level_map(const char *syslog_str, uint32_t *flags)
{
    if (flags == NULL) {
        return -1;
    }

    /* Enable all syslog levels by default */
    *flags = AIM_LOG_BIT_SYSLOG_EMERG;
    *flags += AIM_LOG_BIT_SYSLOG_ALERT;
    *flags += AIM_LOG_BIT_SYSLOG_CRIT;
    *flags += AIM_LOG_BIT_SYSLOG_ERROR;
    *flags += AIM_LOG_BIT_SYSLOG_WARN;
    *flags += AIM_LOG_BIT_SYSLOG_NOTICE;
    *flags += AIM_LOG_BIT_SYSLOG_INFO;
    *flags += AIM_LOG_BIT_SYSLOG_DEBUG;

    /* Map string to level */
    *flags += AIM_LOG_BIT_FATAL;
    *flags += AIM_LOG_BIT_MSG;
    *flags += AIM_LOG_BIT_BUG;
    if (strcmp("emergencies", syslog_str) == 0) {
        return 0;
    }

    *flags += AIM_LOG_BIT_ERROR;
    *flags += AIM_LOG_BIT_INTERNAL;
    if ((strcmp("alerts", syslog_str) == 0) ||
        (strcmp("critical", syslog_str) == 0) ||
        (strcmp("errors", syslog_str) == 0)) {
        return 0;
    }

    *flags += AIM_LOG_BIT_WARN;
    if (strcmp("warnings", syslog_str) == 0) {
        return 0;
    }

    *flags += AIM_LOG_BIT_INFO;
    if (strcmp("notifications", syslog_str) == 0) {
        return 0;
    }

    *flags += AIM_LOG_BIT_VERBOSE;
    if ((strcmp("informational", syslog_str) == 0) ||
        (strcmp("verbose", syslog_str) == 0)) {
        return 0;
    }

    *flags += AIM_LOG_BIT_TRACE;
    if ((strcmp("debugging", syslog_str) == 0) ||
        (strcmp("trace", syslog_str) == 0)) {
        return 0;
    }

    return -1;
}

/**
 * This variable is used as an assignment location for
 * AIM SYSLOG meta documentation strings.
 */
char* aim_syslog_reference;

/**************************************************************************//**
 *
 * This is the log structure for the AIM module.
 *
 *
 *****************************************************************************/
AIM_LOG_STRUCT_DEFINE(
                      AIM_LOG_OPTIONS_DEFAULT,
                      AIM_LOG_BITS_DEFAULT,
                      NULL,
                      0x0       /* Initial Custom Flags */
                      );
