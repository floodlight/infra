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
# CFlagsGenerator.py
#
# Flags object generator.
#
#################################################################
from cobjectgen import *
import util

class CFlagsGenerator(CObjectGenerator):
    objectType = 'flags'

    ############################################################
    #
    # Generation Methods
    #
    ############################################################
    def Init(self):
        self.width = 0
        for entry in self.members:
            name=entry.keys()[0]
            if len(name) > self.width:
                self.width = + len(name)


    def Define(self):
        s = ""
        bitcount = 0
        for entry in self.members:
            name = entry.keys()[0]
            flag = entry[name]
            value = None

            if 'doc' in flag:
                s += self.f.Comment(flag['doc']) # + "\n"
            if 'value' in flag:
                value = "%s" % (flag['value'])
            elif 'shift' in flag:
                value = "(1<<%d)" % (flag['shift'])
            elif 'combine' in flag:
                value = "("
                for fname in flag['combine']:
                    value += "%s | " % (fname)
                value += "0)"
            else:
                value = "(1<<%d)" % (bitcount)
                bitcount = bitcount+1

            widename = name + " "*(self.width-len(name))
            if not 'no-prefix' in flag:
                widename = self.name + "_" + widename;
            else:
                widename += " "*(1+len(self.f.InMacro(self.name)))

            s += "#define %s %s\n" % (self.f.InMacro(widename), value)

        return s;

    #
    # Todo -- Flags Parser/Lookup/Output Routines
    #


###############################################################################
#
# Sanity Check
#
###############################################################################
import yaml
import cm

if __name__ == "__main__":

    d = { 'name' : 'foFlags',
          'members' : [
            { 'foo' : { 'doc': 'This is the comment'} },
            { 'dsfsdfsdf' : {} },
            { 'spam': { 'no-prefix' : 1} },
            { 'eegs': {} },
            { 'special' : { 'shift' : 20 } },
            { 'value' : { 'value' : '0xFF' } },
            { 'all' : { 'combine' : [ 'foo', 'bar', '0x47' ] } },
            ]
          }

    m = CFlagsGenerator(initargs=d)
    print m.Define()

