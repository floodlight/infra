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
# CXEnumGenerator.py
#
#################################################################

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


