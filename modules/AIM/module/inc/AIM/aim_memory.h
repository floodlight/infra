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
 *  /module/inc/AIM/aim_memory.h
 *
 * @file
 * @brief Memory allocation.
 *
 * @addtogroup aim-memory
 * @{
 *
 *****************************************************************************/
#ifndef __AIM_MEMORY_H__
#define __AIM_MEMORY_H__

#include <AIM/aim_config.h>

/**
 * @brief Zero'ed memory alloc.
 * @param size Size.
 */
void *aim_zmalloc(int size);

/**
 * Free memory allocated by aim_zmalloc()
 * @param data The memory to free.
 */
void aim_free(void *data);

/**
 * @brief Duplicate memory.
 * @param src Source memory.
 * @param size Size.
 * @returns a new copy of the data.
 */
void *aim_memdup(void *src, int size);

/**
 * @brief Duplicate memory.
 * @param src Source memory;
 * @param src_size Size to copy.
 * @param alloc_size Size to allocate.
 */
void *aim_memndup(void *src, int src_size, int alloc_size);

#endif /* __AIM_MEMORY_H__ */
/*@}*/
