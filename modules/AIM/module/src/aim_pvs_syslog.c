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

#if AIM_CONFIG_INCLUDE_PVS_SYSLOG == 1

#include <AIM/aim_pvs_syslog.h>
#include <AIM/aim_utils.h>
#include <AIM/aim_string.h>
#include <AIM/aim_memory.h>
#include <AIM/aim_log_flag.h>
#include "aim_util.h"


AIM_OBJECT_ID_DEFINE(aim_syslog_pvs_obj, "aim_syslog_pvs");

typedef struct aim_pvs_syslog_s {
    aim_pvs_t pvs;
    uint32_t facility;
} aim_pvs_syslog_t;


/**
 * Destructor for our objects.
 */
static void aim_pvs_syslog_destroy__(aim_object_t*);


/**
 * Output buffer function.
 */
static int
aim_pvs_syslog_vprintf__(aim_pvs_t* _pvs, aim_log_flag_t flag, 
                         const char* fmt, va_list vargs)
{
    aim_pvs_syslog_t* pvs = (aim_pvs_syslog_t*)_pvs;
    int priority = pvs->facility;

    if(!strcmp(fmt, "\n")) {
        return 0;
    }

    /* generate severity from flag */
    switch (flag) {
    case AIM_LOG_FLAG_FATAL:
        priority |= LOG_CRIT;
        break;
    case AIM_LOG_FLAG_BUG:
    case AIM_LOG_FLAG_ERROR:
        priority |= LOG_ERR;
        break;
    case AIM_LOG_FLAG_WARN:
        priority |= LOG_WARNING;
        break;
    case AIM_LOG_FLAG_MSG:
    case AIM_LOG_FLAG_INFO:
        priority |= LOG_INFO;
        break;
    case AIM_LOG_FLAG_VERBOSE:
    case AIM_LOG_FLAG_TRACE:
    case AIM_LOG_FLAG_INTERNAL:
    case AIM_LOG_FLAG_FTRACE:
    default:
        priority |= LOG_DEBUG;
        break;
    }

    vsyslog(priority, fmt, vargs);
    return 0;
}


static char* ident__ = NULL;
static int refcount__ = 0;

aim_pvs_t*
aim_pvs_syslog_open(const char* ident, int option, int facility)
{
    aim_pvs_syslog_t* rv;

    if(ident__ == NULL) {
        openlog(ident, option, facility);
        ident__ = aim_strdup(ident);
    }

    /*
     * We could check to see if the requested parameters are the same
     * as the currently opened log and return an error if they aren't,
     * but there seems to be little point in losing the information.
     * Just return the existing settings.
     *
     */
    rv = aim_zmalloc(sizeof(*rv));
    AIM_OBJECT_INIT(rv, aim_syslog_pvs_obj, 0, NULL,
                    aim_pvs_syslog_destroy__);
    rv->facility = facility;
    rv->pvs.enabled = 1;
    rv->pvs.vprintf = aim_pvs_syslog_vprintf__;
    rv->pvs.description=aim_strdup("{syslog}");
    ++refcount__;
    return (aim_pvs_t*)rv;
}

aim_pvs_t*
aim_pvs_syslog_get(void)
{

    return aim_pvs_syslog_open(AIM_CONFIG_PVS_SYSLOG_IDENT_DEFAULT,
                               AIM_CONFIG_PVS_SYSLOG_OPTIONS_DEFAULT,
                               AIM_CONFIG_PVS_SYSLOG_FACILITY_DEFAULT);
}

void
aim_pvs_syslog_destroy__(aim_object_t* obj)
{
    if(--refcount__ <= 0) {
        closelog();
        refcount__ = 0;
        ident__ = NULL;
    }
    aim_free(((aim_pvs_t*) obj)-> description);
    aim_free(obj);
}

#else
int __not_empty__;
#endif /* AIM_CONFIG_INCLUDE_PVS_SYSLOG */



















