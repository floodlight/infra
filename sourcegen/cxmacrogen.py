#!/usr/bin/python
## SourceObject ##
###############################################################################
#
# CXMacroGenerator.py
#
# XMacro object generator.
#
###############################################################################

from cobjectgen import *
import util

class CXMacroGenerator(CObjectGenerator):
    objectType = 'xmacro'

    def Construct(self):
        self.submacros = False

    def Name(self):
        return self.f.MacroName(self.name)

        
    ############################################################
    #
    # Generation Methods
    #
    ############################################################
    def XMacroEntries(self):
        s = ""
        for args in self.members:
            s += util.fcall(self.name, args) + "\n"
        return s

            
    def DefineSubmacros(self):

        s = ""
        members = util.listifyElements(self.members)

        for entry in members:
            s += "#ifndef %s\n#define %s %s\n#endif\n\n" % (entry[0], 
                                                            entry[0], 
                                                            self.name)
        for entry in members:
            subgen = CXMacroGenerator(name=entry[0], initargs=entry[1])
            s += subgen.XMacroEntries()
        
        s += "\n"
        for entry in members:
            s += "#undef %s\n" % entry[0]

        return s


    def Define(self):
        s = "#ifdef %s\n" % self.name
        if self.submacros:
            s += self.DefineSubmacros()
        else:
            self.members = util.listifyElements(self.members)
            s += self.XMacroEntries()
        s += "#undef %s\n" % self.name
        s += "#endif\n"
        return s



###############################################################################
# 
# Sanity Check
#
###############################################################################
import cm

if __name__ == "__main__":

    data = { 'members': [ 'ENTRY1', 
                          'ENTRY2', 
                          'ENTRY3', 
                          'ENTRY4', ] }
    
    m = CXMacroGenerator(name='MY_XMACRO', initargs=data); 
    print m.Define()


    data = { 'members' : [ [ 'E01', 'E02', 'E03' ], 
                           [ 'E11', 'E12', 'E13' ], 
                           [ 'E21', 'E22', 'E23' ] ] }
    m = CXMacroGenerator(name='MY_XMACRO2', initargs=data)
    print m.Define()
