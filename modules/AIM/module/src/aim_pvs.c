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

/**************************************************************************//**
 *
 *
 *
 *
 *****************************************************************************/
#include <AIM/aim_config.h>
#include <AIM/aim_pvs.h>
#include <AIM/aim_printf.h>
#include <AIM/aim_utils.h>
#include <stdio.h>


/**
 * Log colors.
 * This is done functionality (instead of through a static array)
 * to avoid buffer overruns if the flags increase (since there is no
 * 'count' member defined) and to catch at compile time a missing entry.
 */

#define TTY_FG_BLACK  30
#define TTY_FG_RED    31
#define TTY_FG_GREEN  32
#define TTY_FG_YELLOW 33
#define TTY_FG_BLUE   34
#define TTY_FG_VIOLET 35
#define TTY_FG_CYAN   36
#define TTY_FG_WHITE  37
#define TTY_FG_NONE   00

#define TTY_BG_BLACK  40
#define TTY_BG_RED    41
#define TTY_BG_GREEN  42
#define TTY_BG_YELLOW 43
#define TTY_BG_BLUE   44
#define TTY_BG_VIOLET 45
#define TTY_BG_CYAN   46
#define TTY_BG_WHITE  47
#define TTY_BG_NONE   00

#define TTY_DULL      0
#define TTY_BRIGHT    1

#define _TTY_COLOR(_intensity, _fg) "\x1B[" #_intensity ";" #_fg "m"
#define TTY_COLOR(_i, _f) _TTY_COLOR(_i, _f)

static const char* color_reset__ = "\x1B[39m";
static const char*
aim_log_flag_color__(aim_log_flag_t flag)
{
#if AIM_CONFIG_LOG_INCLUDE_TTY_COLOR == 1
    switch(flag)
        {
        case AIM_LOG_FLAG_INTERNAL:
        case AIM_LOG_FLAG_BUG:
        case AIM_LOG_FLAG_ERROR:
        case AIM_LOG_FLAG_SYSLOG_ERROR:
            return TTY_COLOR(TTY_DULL, TTY_FG_RED);
        case AIM_LOG_FLAG_FATAL:
        case AIM_LOG_FLAG_SYSLOG_CRIT:
        case AIM_LOG_FLAG_SYSLOG_ALERT:
        case AIM_LOG_FLAG_SYSLOG_EMERG:
            return TTY_COLOR(TTY_BRIGHT, TTY_FG_RED);
        case AIM_LOG_FLAG_WARN:
        case AIM_LOG_FLAG_SYSLOG_WARN:
            return TTY_COLOR(TTY_DULL, TTY_FG_YELLOW);
        default:
            return NULL;
        }
#endif
    return NULL;
}


void
aim_pvs_logf(void* cookie, aim_log_flag_t flag, const char* str)
{
    const char* color = NULL;
    aim_pvs_t* pvs = (aim_pvs_t*)cookie;

    if(pvs && aim_pvs_isatty(pvs) == 1) {
        if((color = aim_log_flag_color__(flag))) {
            aim_printf(pvs, color);
        }
    }

    aim_printf(pvs, "%s", str);

    if(color) {
        aim_printf(pvs, color_reset__);
    }
}


int
aim_pvs_avprintf(aim_pvs_t* pvs, const char* fmt, aim_va_list_t* vargs)
{
    if(pvs == NULL) {
        return 0;
    }
    pvs->counter++;
    if(pvs->enabled == 0) {
        return 0;
    }
    return pvs->vprintf(pvs, fmt, vargs->val);
}

int
aim_pvs_vprintf(aim_pvs_t* pvs, const char* fmt, va_list vargs)
{
    if(pvs == NULL) {
        return 0;
    }
    pvs->counter++;
    if(pvs->enabled == 0) {
        return 0;
    }
    return pvs->vprintf(pvs, fmt, vargs);
}

int
aim_pvs_printf(aim_pvs_t* pvs, const char* fmt, ...)
{
    int rv;
    va_list vargs;
    va_start(vargs, fmt);
    rv = aim_pvs_vprintf(pvs, fmt, vargs);
    va_end(vargs);
    return rv;
}

int
aim_pvs_enable(aim_pvs_t* pvs, int enable)
{
    if(pvs == NULL) {
        return -1;
    }
    else {
        pvs->enabled = enable;
        return 0;
    }
}

void
aim_pvs_destroy(aim_pvs_t* pvs)
{
    if(pvs) {
        aim_object_destroy((aim_object_t*)pvs);
    }
}

int
aim_pvs_isatty(aim_pvs_t* pvs)
{
    if(!pvs || !pvs->isatty) {
        return -1;
    }
    else {
        return pvs->isatty(pvs);
    }
}

const char*
aim_pvs_desc_get(aim_pvs_t* pvs)
{
    return (pvs) ? (pvs->description) : "NULL";
}
