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
# CMacroGenerator.py
#
# Macro object generator.
#
#################################################################

from cobjectgen import *
import util

class CMacroGenerator(CObjectGenerator):
    objectType = 'macro'

    def Construct(self):
        self.body = None


    def Signature(self, proto=True):
        """ Macro Signature """
        return self.f.MacroSignature(self.name,
                                     self.args)

    def Name(self):
        return self.f.MacroName(self.name)


    def Call(self, *args):
        if len(args) == 1 and isinstance(args[0], list):
            args = args[0]

        c = self.Name() + "(" + ",  ".join(args) + ")"
        return c


    ############################################################
    #
    # Generation Methods
    #
    ############################################################

    def Body(self):
        """ Generate the body of our macro """
        # If you don't override the Body() method, you must specify the
        # body of the function as a string in 'self.body'
        if self.body == None:
            raise Exception("No macro body defined in Body()")

        return self.body


    def Define(self):
        if self.args != None:
            # Functional Macro
            s = self.comment;
            s += "#define %s \\\n" % self.Call(self.args)
            s += self.Body()
            s += '\n'
        return s

    def Header(self):
        return self.Define()

###############################################################################
#
# Sanity Check
#
###############################################################################
import yaml
import cm

if __name__ == "__main__":

    class CTestMacro(CMacroGenerator):

        def Construct(self):
            self.name = "TestMacro"
            self.args = [ '_a', '_b', '_c' ]
            self.body = """ (_a) + (_b) + (_c) """


    d = { 'name' : 'foo',
          'args' : ['_a'],
          'body' : '_a++'
          }

    m = CMacroGenerator(initargs=d)
    print m.Define()

    m = CMacroGenerator(name="cmg", args=[ '_a', '_b' ],
                        body = """ (_a) + (_b) + (_c) """)
    print m.Define()

    m = CTestMacro()
    print m.Define()
    print
    print m.Call('x', 'y', 'z')



