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
# CTypesGen
#
# Basic Types Generator
#
#################################################################

from cobjectgen import *
import util

#Fixme
_typemap = {
    'uint32' : 'uint32_t',
    'int' : 'int',
    'int32' : 'int32_t',
    'byte' : 'uint8',
    'byte*' : 'uint8*',
    'uchar' : 'unsigned char',
    }

class CVarGenerator(CObjectGenerator):

    _type = None
    _varname = None
    global_ = False
    local_ = False
    static_ = False

    def extern(self):
        return "extern %s %s;\n" % (self._type, self._varname)

    def define(self):
        return "%s%s %s;\n" % (self.f.Static() + "_" if self.static else "",
                               self._varname)
    def name(self):
        return _varname

    def __str__(self):
        return self.name()

    def Init(self):

        if self._type is None:
            self._type = self.type_
            if self._type in _typemap:
                self._type = _typemap[self._type]

        if self._varname is None:
            self._varname = self.name
            if self.global_:
                self._varname = self.f.GlobalVariable(self._varname)
            if self.local_:
                self._varname = self.f.LocalVariable(self._varname)
            if self.static_:
                self._varname = self.f.StaticVariable(self._varname)



class CppGenerator(CObjectGenerator):
    _default = None
    _name = None

    def Init(self):
        if self._name is None:
            self._name = self.f.CppIdentifier(self.name)

    def __str__(self):
        return self._name

    def define(self, ifndef=False):
        s = ""
        if ifndef:
            s += "#ifndef %s\n" % self._name
        s += "#define %s %s\n" % (self._name, self.value)
        if ifndef:
            s += "#endif\n"
        return s;

    def ifndefine(self):
        return self.define(ifndef=True)


