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
# sg.py
#
# Source Generator
#
#################################################################

import sourcegen
import cobjectgen
import argparse
import sys
import cm
import os

gParser = argparse.ArgumentParser(description='sg -- Source Generators')

gParser.add_argument('-c', help='C Language Generation', action='store_true',
                    default=True)
gParser.add_argument('-d', nargs="+", help='Definition files')
gParser.add_argument('-i', nargs="+", help='Input Source File')
gParser.add_argument('-o', help="""Output Source File. Default is to edit the
replace the input file with the output. Does not change the input file if
no changes are detected. Use --o stdout to output results to stdout""")
gParser.add_argument('-v', help='Verbose Output')
gParser.add_argument('-f', help="Formatter", default="default")
gArgs = gParser.parse_args()

cman = cm.ConfigManager()

if gArgs.d:
    for d in gArgs.d:
        cman.Import(d)

sg = sourcegen.SourceGenerator(cman, cobjectgen.CObjectFactory(cman))

if gArgs.i:

    if isinstance(gArgs.i, str):
        gArgs.i = [ gArgs.i ]

    for inf in gArgs.i:
        if not os.path.isfile(inf):
            continue

        of = gArgs.o
        if of is None:
            of = inf
        print "generate: %s:" % inf,

        diff = sg.Generate(inf, of)
        if inf is of:
            if diff:
                print "\x1B[35m" + "\x1B[1m" + "updated" + "\x1B[39m" + "\x1B[0m"
            else:
                print "\x1B[37m" + "no changes" + "\x1B[39m"



