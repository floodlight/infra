#!/usr/bin/python
## SourceObject ##
###############################################################################
#
# CPortingMacroGenerator.py
#
# Porting Macro object generator.
#
###############################################################################

from cobjectgen import *
import util

class CPortingMacroGenerator(CObjectGenerator):
    objectType = 'portingmacro'


    ############################################################
    #
    # Generation Methods
    #
    ############################################################
    def Define(self):
        prefix = self.name.upper()

        s = ""
        s += "#if %s_CONFIG_PORTING_INCLUDE_STDLIB_HEADERS == 1\n" % prefix
        s += "#include <stdlib.h>\n"
        s += "#include <string.h>\n"
        s += "#include <stdarg.h>\n"
        s += "#include <memory.h>\n"
        s += "#endif\n\n"
        
        for m in self.macros:
            name = m.upper()
            # Breaks macro formatting customization...
            macro = prefix + "_" + name
            s += "#ifndef %s\n" % macro
            s += "    #if defined(GLOBAL_%s)\n" % name
            s += "        #define %s GLOBAL_%s\n" % (macro, name)
            s += "    #elif %s_CONFIG_PORTING_STDLIB == 1\n" % (prefix)
            s += "        #define %s %s\n" % (macro, name.lower())
            s += "    #else\n"
            s += "        #error The macro %s is required but cannot be defined.\n" % macro
            s += "    #endif\n"
            s += "#endif\n"
            s += "\n"
        
        return s; 

###############################################################################
# 
# Sanity Check
#
###############################################################################
import cm

if __name__ == "__main__":
    data = { 'macros': [ 'strcpy', 
                         'strncpy', 
                         'malloc', 
                         'memset', 
                         'memcpy', 
                         'memcmp' ]
             }
    m = CPortingMacroGenerator(name="module", initargs=data); 
    print m.Define(); 

             
           
            
