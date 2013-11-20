#!/usr/bin/python
## SourceObject ##
#################################################################
#
#        Copyright 2013, Big Switch Networks, Inc.
#
# Licensed under the Eclipse Public License, Version 1.0 (the
# "License"); you may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#        http://www.eclipse.org/legal/epl-v10.html
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific
# language governing permissions and limitations under the
# License.
#
#################################################################
#
# CLogGen.py
#
# Generic Code Utilities generator.
#
#################################################################

from cobjectgen import *
import util
from cfunctiongen import *
from cenumgen import *
from cmacrogen import *

class CLogGenerator(CObjectGenerator):
    objectType = 'logger'

    logFlags = [  ['ERROR',   "1<<1"],
                  ['WARN',    "1<<2"],
                  ['INFO',    "1<<3"],
                  ['VERBOSE', "1<<4"],
                  ['TRACE',   "1<<5"],
                  ['INTERNAL', "1<<6"],
                  ['BUG',      "1<<6"],
                  # Lots and lots
                  ['FTRACE',   "1<<20"],
                  # Log Options
                  ['FILE_LINE', "1<<30"],
                  ['FUNC',    "1<<31"],
                  ];

    def Init(self):
        self.logEnum = CEnumGenerator(name="%s_log_flag" % self.name,
                                      members=self.logFlags);


    ############################################################
    #
    # Generation Methods
    #
    ############################################################
    def Header(self):
        # prototypes for all selected utilities
        NAME = self.name.upper()
        name = self.name

        s = ""
        s += "#include <stdint.h>\n"
        s += "#include <AIM/aim_valist.h>\n\n"
        s += self.logEnum.Define();
        s += "extern uint32_t %s_log_flags;\n\n" % name

        s += "#ifndef %s_LOG_PREFIX1\n" % NAME
        s += "#define %s_LOG_PREFIX1 \"\"\n" % NAME
        s += "#endif\n"
        s += "#ifndef %s_LOG_PREFIX2\n" % NAME
        s += "#define %s_LOG_PREFIX2 \"\"\n" % NAME
        s += "#endif"


        s += """
/*
 * Module-level macros.
 */
"""
        for f in self.logFlags:
            FLAG = f[0].upper()
            flag = f[0];

            if flag == "func" or flag == "file_line":
                # These are options, not loggables
                continue

            s += """
#define %(NAME)s_LOG_%(FLAG)s(...) \\
    %(NAME)s_LOG_OUTPUT(%(NAME)s_LOG_FLAG_%(flag)s, __func__, __FILE__, __LINE__, \\
                  "%(name)s" %(NAME)s_LOG_PREFIX1 %(NAME)s_LOG_PREFIX2 ": " "%(FLAG)s: " AIM_VA_ARGS_FIRST(__VA_ARGS__) AIM_VA_ARGS_REST(__VA_ARGS__));\n""" % dict(
                NAME=NAME, FLAG=FLAG, flag=flag, name=name)

            s += """
#define %(NAME)s_OBJ_LOG_%(FLAG)s(_object, ...) \\
    %(NAME)s_LOG_OUTPUT(%(NAME)s_LOG_FLAG_%(flag)s, __func__, __FILE__, __LINE__, \\
                  "%(name)s" %(NAME)s_LOG_PREFIX1 %(NAME)s_LOG_PREFIX2 "(%%s): " "%(FLAG)s: " AIM_VA_ARGS_FIRST(__VA_ARGS__), \\
                  (_object)->log_string AIM_VA_ARGS_REST(__VA_ARGS__))\n""" % dict(
                NAME=NAME, FLAG=FLAG, flag=flag, name=name)

            s += """
/*
 * Shortcut macros for function enter/exit tracing.
 */
#define %(NAME)s_FENTER(...) \\
     %(NAME)s_LOG_OUTPUT(%(NAME)s_LOG_FLAG_FTRACE, __func__, __FILE__, __LINE__, \\
                  "%(name)s" %(NAME)s_LOG_PREFIX1 %(NAME)s_LOG_PREFIX2 ": " "ENTER(%%s): " AIM_VA_ARGS_FIRST(__VA_ARGS__), __func__ AIM_VA_ARGS_REST(__VA_ARGS__))\n""" % dict(
                NAME=NAME, name=name)

            s += """
#define %(NAME)s_FEXIT(...) \\
     %(NAME)s_LOG_OUTPUT(%(NAME)s_LOG_FLAG_FTRACE, __func__, __FILE__, __LINE__, \\
                  "%(name)s" %(NAME)s_LOG_PREFIX1 %(NAME)s_LOG_PREFIX2 ": " "EXIT(%%s): " AIM_VA_ARGS_FIRST(__VA_ARGS__), __func__ AIM_VA_ARGS_REST(__VA_ARGS__))\n""" % dict(
                      NAME=NAME, name=name)

            s += """
/*
 * %(NAME)s_LOG_%(FLAG)s and %(NAME)s_OBJ_LOG_%(FLAG)s can always be called, but they're hard on the
 * carpal tunnel.
 *
 * These are short versions that are customizable --
 */
#ifdef %(NAME)s_LOG_OBJ_DEFAULT
/*
 * The default log uses the object instance
 */
#define %(NAME)s_%(FLAG)s   %(NAME)s_OBJ_LOG_%(FLAG)s

/*
 * Call the message log, without an object, using the 'M' prefix
 */
#define %(NAME)s_M%(FLAG)s  %(NAME)s_LOG_%(FLAG)s

#else
/*
 * The default log is the message-only log
 */
#define %(NAME)s_%(FLAG)s   %(NAME)s_LOG_%(FLAG)s

/*
 * You can still call the object log by using the 'O' prefix
 */
#define %(NAME)s_O%(FLAG)s  %(NAME)s_OBJ_LOG_%(FLAG)s

#endif
""" % dict(NAME=NAME, FLAG=FLAG)

            s += """
#if %(NAME)s_CONFIG_INCLUDE_LOGGING == 1
#define %(NAME)s_LOG_OUTPUT %(name)s_log_output
#else
#define %(NAME)s_LOG_OUTPUT(...)
#endif
""" % dict(NAME=NAME, name=name)

        s += """

/*
 * This function processes log messages for this module.
 */
void %(name)s_log_output(%(name)s_log_flag_t flag, const char* fname, const char* file,
                       int line, const char* fmt, ...);
""" % dict(name=name)



        s += """
/*
* This datastructure encapsulates this module's log info.
* External log providers can access this structure to affect
* the module's log output.
*/

#include <AIM/aim.h>

typedef struct %(name)s_log_info_s {
    /* Name of the module. For programmatic registration purposes. */
    const char* module_name;

    /* Current log flags. */
    int flags;

    /* global enable/disable without changing flags */
    int enabled;

    /* Change the output vector for all log messages */
    aim_pvs_t* pvs;
} %(name)s_log_info_t;

extern %(name)s_log_info_t %(name)s_log_info;
""" % dict(name=self.name)

        return s;

    def Source(self):

        name = self.name;
        NAME = self.name.upper()

        s = ""

        s += """
/*
 * %s Log Info Structure
 */
""" % self.name.upper()

        s += """
#ifndef %s_CONFIG_LOG_FLAGS_DEFAULT
#define %s_CONFIG_LOG_FLAGS_DEFAULT 0xFFFF
#endif
""" % (NAME, NAME)

        s += """
%s_log_info_t %s_log_info = {
    \"%s\",
    %s_CONFIG_LOG_FLAGS_DEFAULT,
    1,
    &aim_pvs_stderr
};
""" % (name, name, name, NAME )

        s += """
#ifndef %s_CONFIG_LOG_MESSAGE_SIZE
#define %s_CONFIG_LOG_MESSAGE_SIZE 256
#endif

void %s_log_output(%s_log_flag_t flag, const char* fname, const char* file,
                       int line, const char* fmt, ...)
{
    char log_msg[%s_CONFIG_LOG_MESSAGE_SIZE];
    char* ptr = log_msg;
    int size = sizeof(log_msg);
    va_list vargs;
    va_start(vargs, fmt);
    int rv = 0;

    if(%s_log_info.pvs && %s_log_info.flags & flag) {
        rv = %s_VSNPRINTF(ptr, size, fmt, vargs);
        if(%s_log_info.flags & %s_LOG_FLAG_FUNC) {
            rv = %s_SNPRINTF(ptr+=rv, size-=rv, " [%%s]", fname);
        }
        if(%s_log_info.flags & %s_LOG_FLAG_FILE_LINE) {
            rv = %s_SNPRINTF(ptr+=rv, size-=rv, " [%%s:%%d]", file, line);
        }
        %s_SNPRINTF(ptr+=rv, size-=rv, "\\n");
        aim_printf(%s_log_info.pvs, log_msg);
    }
    va_end(vargs);
}
""" % (NAME, NAME, name, name, NAME, name, name, NAME, name, NAME, NAME,
       name, NAME, NAME, NAME, name)

        return s;


###############################################################################
#
# Sanity Check
#
###############################################################################
import cm

if __name__ == "__main__":

    m = CLogGenerator(name="module");
    print m.Header();
    print m.Source();




