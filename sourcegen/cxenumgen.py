#!/usr/bin/python
## SourceObject ##
###############################################################################
#
# CXEnumGenerator.py
#
###############################################################################

from cobjectgen import *
import util

class CXEnumGenerator(CObjectGenerator):
    objectType = 'xenum'

    def Construct(self):
        self.submacros = False

    def Name(self):
        return self.f.MacroName(self.name)

        
    ############################################################
    #
    # Generation Methods
    #
    ############################################################
    def Define(self):

        s = "#ifdef %s\n" % self.name
        for (k,v) in self.members.iteritems():
            desc = v['desc'] if 'desc' in v else ""
            s += util.fcall(self.name, "%s, \"%s\"" % (k, desc)) + "\n"
        s += "#undef %s\n" % self.name
        s += "#endif\n"
        return s


