/****************************************************************
 *
 *        Copyright 2014, Big Switch Networks, Inc.
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
 * @file
 * @brief AIM Log Flag
 *
 *
 * @addtogroup aim-log
 * @{
 *
 *****************************************************************************/
#ifndef __AIM_LOG_FLAG_H__
#define __AIM_LOG_FLAG_H__

#include <AIM/aim_map.h>

/* <auto.start.enum(aim_log_flag).header> */
/** aim_log_flag */
typedef enum aim_log_flag_e {
    AIM_LOG_FLAG_MSG,
    AIM_LOG_FLAG_FATAL,
    AIM_LOG_FLAG_ERROR,
    AIM_LOG_FLAG_WARN,
    AIM_LOG_FLAG_INFO,
    AIM_LOG_FLAG_VERBOSE,
    AIM_LOG_FLAG_TRACE,
    AIM_LOG_FLAG_INTERNAL,
    AIM_LOG_FLAG_BUG,
    AIM_LOG_FLAG_FTRACE,
} aim_log_flag_t;

/** Enum names. */
const char* aim_log_flag_name(aim_log_flag_t e);

/** Enum values. */
int aim_log_flag_value(const char* str, aim_log_flag_t* e, int substr);

/** Enum descriptions. */
const char* aim_log_flag_desc(aim_log_flag_t e);

/** Enum validator. */
int aim_log_flag_valid(aim_log_flag_t e);

/** validator */
#define AIM_LOG_FLAG_VALID(_e) \
    (aim_log_flag_valid((_e)))

/** aim_log_flag_map table. */
extern aim_map_si_t aim_log_flag_map[];
/** aim_log_flag_desc_map table. */
extern aim_map_si_t aim_log_flag_desc_map[];

/* <auto.end.enum(aim_log_flag).header> */

#endif /* __AIM_LOG_FLAG_H__ */
/* @}*/
