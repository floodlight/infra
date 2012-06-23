#!/usr/bin/python
## SourceObject ##
###############################################################################
#
# CLogGen.py
#
# Generic Code Utilities generator. 
#
###############################################################################

from cobjectgen import *
import util
from cfunctiongen import *
from cenumgen import *
from cmacrogen import *
        
class CLogGenerator(CObjectGenerator):
    objectType = 'logger'

    logFlags = [  ['Error',   "1<<1"], 
                  ['Warn',    "1<<2"], 
                  ['Info',    "1<<3"], 
                  ['Verbose', "1<<4"], 
                  ['Trace',   "1<<5"], 
                  ['Internal', "1<<6"], 
                  ['Bug',      "1<<6"], 

                  # Log Options
                  ['FileLine', "1<<30"], 
                  ['Func',    "1<<31"], 
                  ]; 
        
    def Init(self):
        self.logEnum = CEnumGenerator(name="%sLogFlag" % self.name, 
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
        s += self.logEnum.Define(); 
        s += "extern unsigned int %s__log_flags;\n\n" % name

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

            if flag == "Func" or flag == "FileLine":
                # These are options, not loggables
                continue

            s += """
#define %s_LOG_%s(_fmt, ...) \\
    %s_LOG_OUTPUT(%sLogFlag%s, __func__, __FILE__, __LINE__, \\
                  \"%s\" %s_LOG_PREFIX1 %s_LOG_PREFIX2 \": \" \"%s: \" _fmt, ##__VA_ARGS__);\n""" % (
                NAME, FLAG, NAME, name, flag, name, NAME, NAME, FLAG)

            s += """
#define %s_LOG_%s0(_msg) \\
    %s_LOG_OUTPUT(%sLogFlag%s, __func__, __FILE__, __LINE__, \\
                  \"%s\" %s_LOG_PREFIX1 %s_LOG_PREFIX2 \": \" \"%s: \" _msg);\n""" % (
                NAME, FLAG, NAME, name, flag, name, NAME, NAME, FLAG)
     
            s += """
#define %s_OBJ_LOG_%s(_object, _fmt, ...) \\
    %s_LOG_OUTPUT(%sLogFlag%s, __func__, __FILE__, __LINE__, \\
                  \"%s\" %s_LOG_PREFIX1 %s_LOG_PREFIX2 "(%%s): " _fmt, \\
                  (_object)->logString, ##__VA_ARGS__)\n""" % (
                NAME, FLAG, NAME, name, flag, name, NAME, NAME)

            s += """
#define %s_OBJ_LOG%s0(_object, _msg) \\
    %s_LOG_OUTPUT(%sLogFlag%s, __func__, __FILE__, __LINE__, \\
                  \"%s\" %s_LOG_PREFIX1 %s_LOG_PREFIX2 "(%%s): " _msg, \\
                  (_object)->logString)\n""" % (
                NAME, FLAG, NAME, name, flag, name, NAME, NAME)
       

            s += """
/*
 * %s_LOG_%s and %s_OBJ_LOG_%s can always be called, but they're hard on the
 * carpal tunnel. 
 *
 * These are short versions that are customizable -- 
 */
#ifdef %s_LOG_OBJ_DEFAULT
/*
 * The default log uses the object instance
 */
#define %s_%s   %s_OBJ_LOG_%s
#define %s_%s0  %s_OBJ_LOG_%s0
/*
 * Call the message log, without an object, using the 'M' prefix
 */
#define %s_M%s  %s_LOG_%s
#define %s_M%s0 %s_LOG_%s0
#else
/*
 * The default log is the message-only log
 */
#define %s_%s   %s_LOG_%s
#define %s_%s0  %s_LOG_%s0
/*
 * You can still call the object log by using the 'O' prefix
 */
#define %s_O%s  %s_OBJ_LOG_%s
#define %s_O%s0 %s_OBJ_LOG_%s0
#endif
""" % (NAME, FLAG, NAME, FLAG, 
       NAME, 
       NAME, FLAG, NAME, FLAG, 
       NAME, FLAG, NAME, FLAG, 
       NAME, FLAG, NAME, FLAG, 
       NAME, FLAG, NAME, FLAG, 
       NAME, FLAG, NAME, FLAG, 
       NAME, FLAG, NAME, FLAG, 
       NAME, FLAG, NAME, FLAG, 
       NAME, FLAG, NAME, FLAG)

                  
        
        s += """
#if %s_CONFIG_INCLUDE_LOGGING == 1
#define %s_LOG_OUTPUT %s_log_output
#else
#define %s_LOG_OUTPUT(...)
#endif
""" % (NAME, NAME, name, NAME)

        s += """

/*
 * This function processes log messages for this module.
 */
void %s_log_output(%sLogFlag_t flag, const char* fname, const char* file, 
                       int line, const char* fmt, ...);
""" % (name, name)


          
        s += """
/*
* This datastructure encapsulates this module's log info. 
* External log providers can access this structure to affect
* the module's log output. 
*/
typedef struct %s_log_info_s {
    /* Name of the module. For programmatic registration purposes. */
    const char* moduleName; 

    /* Current log flags. */
    int flags;

    /* global enable/disable without changing flags */
    int enabled; 

    /* Change the output vector for all log messages */
    void (*output)(const char* msg); 
} %s_log_info_t; 

extern %s_log_info_t %s_log_info;
""" % (self.name, self.name, self.name, self.name)
            
        return s; 
    
    def Source(self):
        
        name = self.name; 
        NAME = self.name.upper()

        s = ""
        
        s += """
/*
 * This is the default log output vector
 */
static void %s_log_output_default(const char* msg)
{
    %s_CONFIG_LOG_OUTPUT_DEFAULT(\"%%s\\n\", msg); 
}
""" % (self.name, self.name.upper())

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
    %s_log_output_default
}; 
""" % (name, name, name, NAME, name)

        s += """
#ifndef %s_CONFIG_LOG_MESSAGE_SIZE
#define %s_CONFIG_LOG_MESSAGE_SIZE 256
#endif

void %s_log_output(%sLogFlag_t flag, const char* fname, const char* file, 
                       int line, const char* fmt, ...)
{
    char logMsg[%s_CONFIG_LOG_MESSAGE_SIZE]; 
    char* ptr = logMsg; 
    int size = sizeof(logMsg); 
    va_list vargs; 
    va_start(vargs, fmt); 
    int rv = 0;

    if(%s_log_info.output && %s_log_info.flags & flag) {
        rv = %s_VSNPRINTF(ptr, size, fmt, vargs); 
        if(%s_log_info.flags & %sLogFlagFunc) { 
            rv = %s_SNPRINTF(ptr+=rv, size-=rv, " [%%s]", fname); 
        }
        if(%s_log_info.flags & %sLogFlagFileLine) {         
            rv = %s_SNPRINTF(ptr+=rv, size-=rv, " [%%s:%%d]", file, line); 
        }
        %s_log_info.output(logMsg); 
    }
    va_end(vargs); 
}
""" % (NAME, NAME, name, name, NAME, name, name, NAME, name, name, NAME, 
       name, name, NAME, name)

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

             
           
            
