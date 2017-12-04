#!/usr/bin/python2
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
# PyEnumGenerator.py
#
# Enum-specific Python code generation objects
# Simple WIP
#
#################################################################
from cenumgen import *

import re

IDENT_RE = re.compile("^[a-zA-Z_][a-zA-Z0-9_]*$")

class PyEnumGenerator(CEnumGenerator):
    """ Python Enum Generator Subclass """

    objectType='pyenum'

    def Construct(self):
        self.novalue = False;
        self.strings = True;

    def Init(self):
        pass

    ############################################################
    #
    # Generation Directives
    #
    # These methods generate code for this enumeration
    #
    ############################################################
    def Define(self):
        """ Generate an Enum Definition """
        #
        # The default behavior is to typedef all enums.
        # If you don't want a typedef, specify 'typedef:False'
        # in the enum specification
        #
        v = 0
        s = "class %s(Enumeration):\n" % (self.name.upper())
        for member in self.members:
            name = self.f.EnumEntry(member.name, "")[1:]
            if not IDENT_RE.match(name):
                name = '_' + name
            s += "    %s" % name
            if member.value and (self.novalue == False):
                # Value specified
                if hasattr(self, 'hex'):
                    s += " = EnumerationItem(0x%x)" % int(member.value)
                else:
                    if hasattr(self, 'flags') and self.flags is True:
                        s += " = (1 << %d)" % int(member.value)
                    else:
                        s += " = %s" % member.value
            elif hasattr(self, 'flags'):
                if self.flags is True:
                    s += " = (1 << %d)" % (self.members.index(member))
                else:
                    raise Exception("Not handled.")
            else:
                s += " = %d" % v
                v += 1

            s += "\n"

        s += "\n"
        return s


    def __getitem__(self, item):
        for m in self.members:
            if m[0] == item:
                return self.f.EnumEntry(m[0], self.name)
        raise Exception("No enum entry named %s" % item)


###############################################################################
#
# Enum Unit testing
#
###############################################################################
if __name__ == "__main__":

    e = PyEnumGenerator(name="testEnum", members=[ ['member1'], ['member2'],
                                                  ['member3']])

    print e.Define()
