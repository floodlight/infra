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
# CFunctionGenerator.py
#
# Function object generator.
#
#################################################################

from cobjectgen import *
import util

class CFunctionGenerator(CObjectGenerator):
    objectType = 'function'

    def Construct(self):
        self.comments = ""
        self.static = False
        self.body = None
        self.rv = None
        self.args = None



    def Signature(self, proto=True):
        """ Generates the function signature """
        s = ""
        if self.static:
            s = "static "
        return s + self.f.FunctionSignature(self.rv,
                                            self.name,
                                            self.args,
                                            proto=proto);

    def Name(self):
        """ Returns the name of this function in the generated code """
        return self.f.FunctionName(self.name)


    def Call(self, *args):
        """ Generates a call to this function with the given parameters """
        c = self.Name() + "(" + ", ".join(args) + ")"
        return c


    ############################################################
    #
    # Generation Methods
    #
    ############################################################

    def Header(self):
        return self.Prototype();

    def Prototype(self):
        """ Generates our function prototype """
        return self.comments + self.Signature(proto=True) + ';\n'


    def Declare(self):
        """ Generate our function declaration """
        return self.Signature(proto=False)


    def Body(self):
        """ Generate our function body. """
        # If you don't override the Body() method, you must specify the
        # body of the function as a string in 'self.body'
        if self.body == None:
            raise Exception("No function body defined in Body()")

        return self.body


    def Define(self):
        """ Generate our entire function definition """
        s = ""
        s += self.Declare() + "\n" + "{\n" + self.Body() + "\n}\n"
        return s



###############################################################################
#
# Sanity Check
#
###############################################################################

if __name__ == "__main__":

    class CTestFunction(CFunctionGenerator):

        def Init(self):
            self.rv = 'int';
            self.name = 'testFunction'
            self.args = [ [ 'int', 'arg1' ],
                          [ 'long', 'arg2' ] ]

            self.body = """    return arg1+arg2;"""



    f = CTestFunction()
    print f.Prototype();
    print
    print f.Define()
    print
    print f.Call('a', 'b') + ';'


    class CTestVoidFunction(CFunctionGenerator):
        def Init(self):
            self.rv = 'void'
            self.name = 'testVoidFunction'
            self.args = None

            self.body = """    /* Nothing */"""


    f = CTestVoidFunction()
    print f.Prototype()
    print
    print f.Define()
    print
    print f.Call()




