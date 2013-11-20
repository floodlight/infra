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
# SourceGenerator.py
#
# Base class for all language generators
#
##################################################################

import imp
import sys
import re
import StringIO
import tempfile
import shutil
import filecmp
import util
import yaml

class ParseError(Exception):
    def __init__(self, value):
        self.value = "parse error: " + value

    def __str__(self):
        return str(self.value)


class SourceGenerator:
    """ SourceGenerator class """

    def __init__(self, cManager, objectFactory):

        self.cm = cManager
        self.of = objectFactory

        self.directiveS = re.compile(
            r'(.*)<auto.start.(?P<expr>.*)>')
        self.directiveE = re.compile(
            r'(.*)<auto.end.(?P<expr>.*)>')

    def prn(self, str_, *args):
        self.outputFile.write(str_)


    def Generate(self, inputFileName, outputFileName=None):

        # Input File
        self.inputFile = open(inputFileName)

        replace = False

        # Output File
        if outputFileName is None or outputFileName in [ 'stdout', '-' ]:
            self.outputFile = sys.stdout
            self.outputFileName = 'stdout'
        elif outputFileName == inputFileName:
            # In place. Generate to tmpfile and check results
            self.outputFile = tempfile.NamedTemporaryFile()
            replace = True
            self.outputFileName = self.outputFile.name
        else:
            # Output file specified
            self.outputFile = open(outputFileName, "w")
            self.outputFileName = outputFileName
            replace = False

        # Process input file
        for line in self.inputFile:
            self.prn(line)

            if self.StartDirective(line):
                # Output code section
                self.HandleDirective(line)
                # Skip until the terminating directive
                while not self.EndDirective(line):
                    # Skip existing
                    try:
                        line = next(self.inputFile)
                    except StopIteration:
                        # End of file without finding terminator.
                        raise ParseError(
                            ('End of input while searching for '
                             'the following terminator: '
                             'auto.end.%s' % self.matchD.group('expr')))

                self.prn(line)


        diff = False
        self.outputFile.flush()

        if self.outputFileName != 'stdout':
            #
            # Diff results here
            #
            if filecmp.cmp(inputFileName, self.outputFileName):
                # Files are the same
                diff = False
            else:
                diff = True


        if diff and replace:
            self.inputFile.close()
            shutil.copyfile(self.outputFileName, inputFileName)

        if self.outputFile is not sys.stdout:
            self.outputFile.close()

        return diff


    def StartDirective(self, line):
        self.matchD = self.directiveS.match(line);
        return self.matchD

    def EndDirective(self, line):
        matchE = self.directiveE.match(line)
        if matchE:
            # Found an end directive. Verify
            if (matchE.group('expr') == self.matchD.group('expr')):
                return True;
        return False;

    def HandleDirective(self, line):
        expr = self.matchD.group('expr')
        x = self.of.Eval(expr)
        self.prn(x)
