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


class CUtilGenerator(CObjectGenerator):
    objectType = 'util'

    def Init(self):
        self.pobjects = {}
        self.pobjects['zmalloc'] = CUtilZMalloc(prefix=self.name)

        
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
                s += self.pobjects[u].Prototype(); 
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

             
           
            
