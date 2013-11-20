#!/usr/bin/python
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
# CObjectGenerator.py
#
# Base generator class for C Language Objects
#
#################################################################
from sourceobjectgen import *
from cdefaultsourceformatter import *
from cknfsourceformatter import *

class CObjectGenerator(SourceObjectGenerator):

    def __init__(self, **kwargs):
        self.SetFormatter(kwargs.get('formatter', None))
        SourceObjectGenerator.__init__(self, **kwargs)

    def SetFormatter(self, formatter=None):
        """ Sets the source formatter object to use in code generation"""
        self.f = CKNFSourceFormatter()


class CObjectFactory(SourceObjectFactory):
    objectLanguage = "c"


if __name__ == "__main__":

    import argparse
    import cm
    import sys

    ap = argparse.ArgumentParser(description="CObjectGenerator")
    ap.add_argument("-i", nargs='+', help="source metadata files")
    ap.add_argument("-e", nargs='+', help="object expression",
                    required=True)

    cm = cm.ConfigManager()
    options = ap.parse_args()
    if options.i:
        for f in options.i:
            cm.Import(f)

    sof = CObjectFactory(cm)
    for e in options.e:
        print "/* expr: %s */" % e
        print sof.Eval(e)
