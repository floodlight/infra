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
# CStructGen
#
#################################################################

from cobjectgen import *
from cfunctiongen import *
import util

class CStructGenerator(CObjectGenerator):
    objectType = 'struct'

    ############################################################
    #
    # Generation Methods
    #
    ############################################################
    def TypedefName(self):
        if hasattr(self, 'typedefname'):
            return self.typedefname
        return self.f.TypedefStructName(self.name)

    def StructName(self):
        if hasattr(self, 'structname'):
            return "struct %s" % self.structname
        return "struct %s" % self.f.StructName(self.name)

    def Define(self):
        s = ""
        s += self.comment
        s += "typedef %s {\n" % self.StructName()
        for member in self.members:
            if isinstance(member, str):
                s += "    %s;\n" % member
            elif isinstance(member, list):
                if member[0] == "__self__":
                    member[0] = "struct %s*" % self.StructName()
                s += """    /** %s */\n""" % (member[1])
                s += "    %s %s;\n" % (member[0], member[1])
            else:
                raise Exception("bad struct definition")
        s += "} %s;\n" % self.TypedefName()

        return s

    def Declare(self):
        return "typedef %s;\n" % self.TypedefName()

    def ExternTable(self, name):
        s =  "/** %s table. */\n" % name
        s += "extern %s %s[];\n" % (self.TypedefName(), name)
        return s

    def DefineTable(self, name):
        s = ""
        s += "%s %s[] =\n" % (self.TypedefName(), name)
        return s


###############################################################################
#
# Utility Struct Classes
#
###############################################################################

class CStructIntMap(CStructGenerator):
    """ Map integers to strings """

    def Construct(self):
        self.name = 'intmap'
        self.valueMember = "value"
        self.nameMember = "name"

    def Init(self):
        self.members = [ ['const char*', self.nameMember ],
                         ['int', self.valueMember ],
                         ]




class CStructStringMap(CStructGenerator):

    def Construct(self):
        self.name="strmap"
        self.nameMember = "name"
        self.valueMember = "value"


    def Init(self):
        self.members = [ [ "const char*", self.nameMember ],
                         [ "const char*", self.valueMember],
                         ]


if __name__ == "__main__":

    o = CStructGenerator(name='testStruct',
                         members= [ "int x", ['__self__', 'next'], "char* y"])
    print o.Define() + "\n"
    print o.TypedefName() + "\n"
    print o.StructName() + "\n"
    print o.Declare() + "\n"

    print CStructIntMap().Define() + "\n"
    print CStructStringMap().Define() + "\n"
