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
# CAIMLogGen.py
#
# Log Generator for AIM infrastructure.
#
#################################################################

from cobjectgen import *
import util
from cfunctiongen import *
from cenumgen import *
from cmacrogen import *

class CAIMCommonLogMacroGenerator(CObjectGenerator):
    objectType = 'aim_common_log_macro'


    def Init(self):
        pass

    ############################################################
    #
    # Generation Methods
    #
    ############################################################
    def Header(self):

        s = """
/******************************************************************************
 *
 * Common Module Log Macros
 *
 *****************************************************************************/
"""
        for f in self.flags:
            s += """
/** Log a module-level %(name)s */
#define AIM_LOG_MOD_%(NAME)s(...) \\
    AIM_LOG_MOD_COMMON(%(NAME)s, __VA_ARGS__)
/** Log a module-level %(name)s with ratelimiting */
#define AIM_LOG_MOD_RL_%(NAME)s(_rl, _time, ...)           \\
    AIM_LOG_MOD_RL_COMMON(%(NAME)s, _rl, _time, __VA_ARGS__)

""" % dict(NAME=f.upper(), name=f.lower())

        s += """
/******************************************************************************
 *
 * Common Object Log Macros
 *
 *****************************************************************************/
"""
        for f in self.flags:
            s += """
/** Log an object-level %(name)s */
#define AIM_LOG_OBJ_%(NAME)s(_obj, ...) \\
    AIM_LOG_OBJ_COMMON(_obj, %(NAME)s, __VA_ARGS__)
/** Log an object-level %(name)s with ratelimiting */
#define AIM_LOG_OBJ_RL_%(NAME)s(_obj, _rl, _time, ...) \\
    AIM_LOG_OBJ_RL_COMMON(_obj, _rl, _time, %(NAME)s, __VA_ARGS__)

""" % dict(NAME=f.upper(), name=f.lower())

        s += """
/******************************************************************************
 *
 * Default Macro Mappings
 *
 *****************************************************************************/
#ifdef AIM_LOG_OBJ_DEFAULT
"""
        for f in self.flags:
            s += """
/** %(NAME)s -> OBJ_%(NAME)s */
#define AIM_LOG_%(NAME)s AIM_LOG_OBJ_%(NAME)s
/** RL_%(NAME)s -> OBJ_RL_%(NAME)s */
#define AIM_LOG_RL_%(NAME)s AIM_LOG_RL_OBJ_%(NAME)s

""" % dict(NAME=f.upper(), name=f.lower())

        s += """
#else
"""
        for f in self.flags:
            s += """
/** %(NAME)s -> MOD_%(NAME)s */
#define AIM_LOG_%(NAME)s AIM_LOG_MOD_%(NAME)s
/** RL_%(NAME)s -> MOD_RL_%(NAME)s */
#define AIM_LOG_RL_%(NAME)s AIM_LOG_MOD_RL_%(NAME)s
""" % dict(NAME=f.upper(), name=f.lower())

        s += """
#endif
"""
        return s;




class CAIMCustomLogMacroGenerator(CObjectGenerator):
    objectType = 'aim_custom_log_macro'


    def _dict(self, flag):
        return dict(PREFIX=self.name.upper(),
                    NAME=flag.upper(),
                    name=flag.lower(),
                    FID=self.prefix+flag.upper())

    ############################################################
    #
    # Generation Methods
    #
    ############################################################
    def Header(self):
        s = ""

        s += """
/******************************************************************************
 *
 * Custom Module Log Macros
 *
 *****************************************************************************/
"""
        for f in self.flags:
            s += """
/** Log a module-level %(name)s */
#define %(PREFIX)s_LOG_MOD_%(NAME)s(...) \\
    AIM_LOG_MOD_CUSTOM(%(FID)s, "%(NAME)s", __VA_ARGS__)
/** Log a module-level %(name)s with ratelimiting */
#define %(PREFIX)s_LOG_MOD_RL_%(NAME)s(_rl, _time, ...)           \\
    AIM_LOG_MOD_RL_CUSTOM(%(FID)s, "%(NAME)s", _rl, _time, __VA_ARGS__)
""" % self._dict(f)

        s += """
/******************************************************************************
 *
 * Custom Object Log Macros
 *
 *****************************************************************************/
"""
        for f in self.flags:
            s += """
/** Log an object-level %(name)s */
#define %(PREFIX)s_LOG_OBJ_%(NAME)s(_obj, ...) \\
    AIM_LOG_OBJ_CUSTOM(_obj, %(FID)s, "%(NAME)s", __VA_ARGS__)
/** Log an object-level %(name)s with ratelimiting */
#define %(PREFIX)s_LOG_OBJ_RL_%(NAME)s(_obj, _rl, _time, ...) \\
    AIM_LOG_OBJ_RL_CUSTOM(_obj, %(FID)s, "%(NAME)s", _rl, _time, __VA_ARGS__)
""" % self._dict(f)

        s += """
/******************************************************************************
 *
 * Default Macro Mappings
 *
 *****************************************************************************/
#ifdef AIM_LOG_OBJ_DEFAULT
"""
        for f in self.flags:
            s += """
/** %(NAME)s -> OBJ_%(NAME)s */
#define %(PREFIX)s_LOG_%(NAME)s %(PREFIX)s_LOG_OBJ_%(NAME)s
/** RL_%(NAME)s -> OBJ_RL_%(NAME)s */
#define %(PREFIX)s_LOG_RL_%(NAME)s %(PREFIX)s_LOG_RL_OBJ_%(NAME)s

""" % self._dict(f)

        s += """
#else
"""
        for f in self.flags:
            s += """
/** %(NAME)s -> MOD_%(NAME)s */
#define %(PREFIX)s_LOG_%(NAME)s %(PREFIX)s_LOG_MOD_%(NAME)s
/** RL_%(NAME)s -> MOD_RL_%(NAME)s */
#define %(PREFIX)s_LOG_RL_%(NAME)s %(PREFIX)s_LOG_MOD_RL_%(NAME)s
""" % self._dict(f)

        s += """
#endif
"""




        return s;









###############################################################################
#
# Sanity Check
#
###############################################################################
import cm

if __name__ == "__main__":

    m = CAIMCommonLogMacroGenerator(flags = ["WARN", "ERROR", "INFO"])
    print m.Header();
    #print m.Source();




