#!/usr/bin/python
## SourceObject ##
###############################################################################
#
# CConfigDefGenerator
#
# Configuration Definition Generator
#
###############################################################################

from cobjectgen import *
from cfunctiongen import *
from cstructgen import *
import util

class CConfigDefGenerator(CObjectGenerator):
    objectType = 'cdef'


    ############################################################
    #
    # Generation Methods
    #
    ############################################################
    def Define(self):

        docString = self.name
        if isinstance(self.doc, str):
            docString += "\n\n" + self.doc

        s = self.f.Comment(docString)
        s += "\n#ifndef %s\n#define %s %s\n#endif\n" % (self.name, 
                                                      self.name, 
                                                      self.default)
        return s

    def TableEntry(self, macroName, macroVal, indent=4):
        s  = ""
        s += "#ifdef %s\n" % self.name
        s += " " * indent
        s += "{ %s(%s), %s(%s) },\n" % (macroName, self.name, 
                                        macroVal, self.name)
        s += "#else\n"
        s += "{ %s(%s), \"__undefined__\" },\n" % (self.name, macroName)
        s += "#endif\n"
        return s



class CConfigDefLookupFunction(CFunctionGenerator):

    def Init(self):

        ctn = self.cobj.ConfigTableName()

        self.rv = "const char*"
        self.name = self.cobj.basename + "Lookup"
        self.args = [ ["const char*", 'setting'] ]
        self.body = """    int i;
    for(i = 0; %s[i].name; i++) {
        if(%s(%s[i].name, setting)) {
            return %s[i].value;
        }
    }
    return NULL;""" % (ctn, self.f.GlobalStringCompare(), ctn, ctn)
                       
    
    

class CConfigDefShowFunction(CFunctionGenerator):

    def Init(self):
        self.rv = "int"
        self.name = self.cobj.basename + "Show"
        self.args = [ [ "int", "(*prn)(const char* fmt, ...)" ] ]
        self.body = """    int i;
    for(i = 0; %s[i].name; i++) {
        prn("%%s = %%s\\n", %s[i].name, %s[i].value);
    }
    return i;""" % (self.cobj.ConfigTableName(), 
                    self.cobj.ConfigTableName(), 
                    self.cobj.ConfigTableName())


        
class CConfigDefsGenerator(CObjectGenerator):
    objectType = 'cdefs'

    def Init(self):
        self.struct = CStructStringMap(name=self.basename + "Settings")

    def ConfigTableName(self):
        return "%s_settings" % self.basename
    
    def CDefConstruct(self, d):
        k = d.keys()[0]
        return CConfigDefGenerator(name=k, initargs=d[k])

    ############################################################
    #
    # Generation Methods
    #
    ############################################################
    def Define(self):

        s = ""
        for cdef in self.defs:
            s += self.CDefConstruct(cdef).Define()
            s += "\n"
        s += "\n"
        return s

    
    def DefineStruct(self):
        return self.struct.Define()

    def ExternTable(self):
        return self.struct.ExternTable(self.ConfigTableName())

    def DefineTable(self):
        stringname = "__%s_STRINGIFY_NAME" % self.basename
        stringval = "__%s_STRINGIFY_VALUE" % self.basename

        s = ""
        s += "#define %s(_x) #_x\n" % stringname
        s += "#define %s(_x) %s(_x)\n" % (stringval, stringname)
        s += ""
        s += self.struct.DefineTable(self.ConfigTableName())
        s += "{\n"
        for cdef in self.defs:
            s += self.CDefConstruct(cdef).TableEntry(stringname, stringval)
        s += "    { NULL, NULL }\n"
        s += "};\n"
        s += "#undef %s\n" % stringval
        s += "#undef %s\n" % stringname

        return s

    def DefineLookup(self):
        return CConfigDefLookupFunction(cobj=self).Define()

    def PrototypeLookup(self):
        return CConfigDefLookupFunction(cobj=self).Prototype()

    def DefineShow(self):
        return CConfigDefShowFunction(cobj=self).Define()

    def PrototypeShow(self):
        return CConfigDefShowFunction(cobj=self).Prototype()

    def Header(self):
        s = ""
        s += self.Define() + "\n"
        s += self.f.Comment("""All compile time options can be queried or displayed
""")
        s += self.DefineStruct() + "\n"
        s += self.ExternTable() + "\n"
        s += self.PrototypeLookup() + "\n"
        s += self.PrototypeShow() + "\n"
        return s

    def Source(self):
        s = ""

        s += self.DefineTable() + "\n"
        s += self.DefineLookup() + "\n"
        s += self.DefineShow() + "\n"
        
        return s

###############################################################################
# 
# Sanity Check
#
###############################################################################
import cm

if __name__ == "__main__":

    print "/* ConfigDefGenerator Test */"
    m = CConfigDefGenerator(name="CONFIG_FOOBAR", 
                            default=0x42, 
                            doc ="""
This is the helpstring for CONFIG_FOOBAR
You should always understand CONFIG_FOOBAR settings
""")

    print m.Define()
    
    data = [ { 'CONFIG1' : { 'default':0x42, 'doc': "C1" } }, 
             { 'CONFIG2' : { 'default':0x41, 'doc': "C2" } }, 
             { 'CONFIG3' : { 'default':0x10, 'doc': "C3" } } 
             ]

    print "/* ConfigDefsGenerator Test */"
    m = CConfigDefsGenerator(basename="CDEFTEST", defs=data)
                          
    print m.Define()
    

