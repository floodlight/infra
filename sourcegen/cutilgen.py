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
# CUtilGen.py
#
# Generic Code Utilities generator.
#
#################################################################

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

class CUtilOcPrintf(CFunctionGenerator):
    def Init(self):
        self.rv = "int"
        self.args = [ "void* oc", "const char* fmt", "..." ];
        self.name = "%s_oc_printf" % self.prefix
        self.body = """    va_list vargs;
    int rv;
    va_start(vargs, fmt);
    if(oc == NULL && fmt == NULL) {
        int (**voutp)(void*,const char*,va_list) = va_arg(vargs,
            int (**)(void*,const char*, va_list));
        *voutp = %s_oc_vprintf;
        rv = 0;
    } else {
        rv = %s_VPRINTF(fmt, vargs);
    }
    va_end(vargs);
    return rv; """ % (self.prefix, self.prefix.upper())

class CUtilOcVPrintf(CFunctionGenerator):
    def Init(self):
        self.rv = "int"
        self.args = [ "void* oc", "const char* fmt", "va_list vargs" ];
        self.name = "%s_oc_vprintf" % self.prefix
        self.body = """    return %s_VPRINTF(fmt, vargs);
""" % (self.prefix.upper())


class CUtilArraySize(CMacroGenerator):
    def Init(self):
        self.comment = ""
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
        self.pobjects['oc_printf'] = CUtilOcPrintf(prefix=self.name)
        self.pobjects['oc_vprintf'] = CUtilOcVPrintf(prefix=self.name)

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




