#!/usr/bin/python
## SourceObject ##
###############################################################################
#
# CUtilGen.py
#
# Generic Code Utilities generator. 
#
###############################################################################

from cobjectgen import *
import util
from cfunctiongen import *
from cmacrogen import *

#
# zmalloc
#
class CUtilZMalloc(CFunctionGenerator):

    def Init(self):
        self.rv = "void*"
        self.args = [[ 'int', 'size' ]]
        self.name = "%s_zmalloc" % self.prefix
        self.body = """    void* p;
    p = %s_MALLOC(size); 
    if(p) { 
        %s_MEMSET(p, 0, size); 
    }
    return p; """ % (self.prefix.upper(), self.prefix.upper())


class CUtilStrlcpy(CFunctionGenerator):
    def Init(self):
        self.rv = "int"
        self.args = [ "char* dst", "const char* src", "int size" ]; 
        self.name = "%s_strlcpy" % self.prefix
        self.body = """    %s_STRNCPY(dst, src, size);
    if (size > 0)
        dst[size-1] = 0;
    return strlen(src); """ % (self.prefix.upper())


class CUtilArraySize(CMacroGenerator):
    def Init(self):
        self.name = "%s_ARRAYSIZE" % self.prefix.upper()
        self.args = [ '_array' ]
        self.body = """ (sizeof(_array)/sizeof(_array[0])) """

    # Fixme - to avoid multiple definitions (in header and source file)
    def Header(self):
        return CMacroGenerator.Define(self); 

    def Define(self):
        return ""



class CUtilGenerator(CObjectGenerator):
    objectType = 'util'

    def Init(self):
        self.pobjects = {}
        self.pobjects['zmalloc'] = CUtilZMalloc(prefix=self.name)
        self.pobjects['strlcpy'] = CUtilStrlcpy(prefix=self.name)
        self.pobjects['arraysize'] = CUtilArraySize(prefix=self.name)

    ############################################################
    #
    # Generation Methods
    #
    ############################################################
    def Header(self):
        # prototypes for all selected utilities
        s = ""
        for u in self.objects:
            if u in self.pobjects:
                s += self.pobjects[u].Header(); 
            else:
                # Requested something we don't have.
                s += "/* Utility '%s' does not exist */\n" % u
        return s; 
            
    def Define(self):
        s = ""
        for u in self.objects:
            if u in self.pobjects:
                s += self.pobjects[u].Define(); 
            else:
                s += "/* Utility '%s' does not exist */\n" % u
        return s; 

###############################################################################
# 
# Sanity Check
#
###############################################################################
import cm

if __name__ == "__main__":
    data = { 'objects': [ 'zmalloc', 'pingGod' ] }
    m = CUtilGenerator(name="module", initargs=data); 
    print m.Header(); 
    print m.Define(); 

             
           
            
