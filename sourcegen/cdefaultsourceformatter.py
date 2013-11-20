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
# CDefaultSourceFormatter.py
#
# Base Formatter Class for the C Language
#
# This base class provides all basic C language formatting
# used by the CSourceObjectGenerator and CSourceGenerator classes.
#
# Derive from this class to specify different formatting behavior
#
#################################################################
from sourceformatter import *
import re
import util

class CDefaultSourceFormatter(SourceFormatter):

    def __init__(self):
        SourceFormatter.__init__(self)


    ############################################################
    #
    # General Code and Keyword Formatting
    #
    ############################################################

    def Static(self):
        """ Optional override for static definitions """
        return 'static'

    def GlobalStringCompare(self):
        """ Return the function used for strcmp() """
        return 'strcmp'

    def GlobalSubstring(self):
        """ Return the function used for strstr() """
        return 'strstr'

    def Identifier(self, name):
        """ Basic Formatting for all identifiers """
        return name
    def CppIdentifier(self, name):
        """ Formatting for all Preprocessor Identifiers """
        return name.upper()

    def StaticVariable(self, name):
        """ Format static variable names """
        return "%s__" % self.Identifier(name)

    def GlobalVariable(self, name):
        """ Format for global variable names """
        return self.Identifier(name);

    def LocalVariable(self, name):
        """ Format for local variable names """
        return self.Identifier(name);
    ############################################################
    #
    # Structure Formatting
    #
    ############################################################
    def StructName(self, ident):
        # Default is the prepend "_s" to all struct basenames
        return ident + "_s"

    def TypedefStructName(self, ident):
        return ident + "_t"

    ############################################################
    #
    # Enumeration Formatting
    #
    ############################################################

    def EnumName(self, ident):
        """ What should an enum definition look like.
        The code will look like "enum <value> {"""

        # Default is to prepend "_e" to all enum basenames
        return ident + "_e"

    def TypedefEnumName(self, ident):
        """ The typedef'ed type name for an enum """
        # Default is to prepend "_t" to all basenames
        return ident + "_t"


    def EnumEntry(self, entry, ident):
        """ What should an enumeration entry look like """
        # Default is <ident><entry>
        return ident+entry


    def EnumCount(self, ident):
        """ What should the special <type>Count entry look like """
        # Default is <type>Count
        return ident+"Count"


    def EnumLast(self, ident):
        """ What should the special <type>Last entry look like """
        # Default is <type>Last
        return ident+"Last"


    def EnumInvalid(self,ident):
        """ What should the special <type>Invalid entry look like """
        return ident+"Invalid"

    def EnumMapTypeName(self, enum):
        """ What is the name of the ENUM_MAP structure. This
        structure is needed for enum management and description
        tables. You can define this structure separately in your code
        or ask the EnumObject generator to declare it for you.
        Either way, return what you call it here"""

        # Default
        return "enum_map_t"

    def EnumStringsMacroName(self, ident):
        """ What should the STRINGS macro name look like """

        # Default is "IDENT_STRINGS"
        return self.MacroName("%s_STRINGS" % (ident))


    def EnumStringsTableName(self, ident):
        """ What should the enum string table be called """
        # Default is "ident_strings[]"
        return "%s_strings" % (ident)


    def EnumMapName(self, enum):
        """ How should we declare a map_table for the given enum"""
        # Default is [enum]_map[]
        return "%s_map" % (enum)


    def EnumFindByNameHelper(self, enum):
        return "enum_find_by_name"

    def EnumFindByValueHelper(self, enum):
        """ What name should be used for the value lookup function """
        # Default is not specific to the enum.
        return "enum_find_by_value"


    ############################################################
    #
    # Macro Formatting
    #
    ############################################################

    def InMacro(self, ident):
        """ What an identifier should look like when referenced
        inside a macro"""

        #
        # Default:
        # spamAndEggs -> SPAM_AND_EGGS
        # spam_and_eggs -> SPAM_AND_EGGS
        #
        # If there are no lowercase letters in the identifier,
        # just return it.
        if re.search("[a-z]", ident):
            s = re.sub("([A-Z])", "_\\1", ident)
            return s.upper()
        else:
            return ident



    def MacroName(self, name):
        """ Transform a macro name based on local nameing conventions """
        # Default is the same as InMacro
        return self.InMacro(name)


    ############################################################
    #
    # Function Formatting
    #
    ############################################################

    def FunctionName(self, name):
        """ Transform a function name based on local naming conventions """
        # Default is no change
        return name


    def FunctionPList(self, argList):
        """ Format an argument list """
        # Default is "([type] arg, [type] arg, ...)"
        s = "("
        if argList is None or argList == 'void':
            s += 'void'
        else:
            for arg in argList:
                if isinstance(arg, list):
                    s += arg[0] + " " + arg[1]
                else:
                    s += arg
                s += util.commaspace(arg, argList)
        s += ")"
        return s

    def FunctionSignature(self, rv, name, argList, proto):
        """ Convenience function for function signature generation """
        if proto == True:
            return self.FunctionPrototype(rv, name, argList)
        else:
            return self.FunctionDeclaration(rv, name, argList)

    def MacroSignature(self, name, args):
        s = self.MacroName(name)
        if len(args):
            # Functional signature
            s = "%s(";
            for arg in args:
                s += "%s%s" % (arg, util.comma(arg, args))
            s += ")"
        return s


    def FunctionPrototype(self, rv, name, argList):
        """ Format a function prototype """
        # Default is:
        #
        # <returns>
        # functionName(arguments)
        #
        return "%s %s%s" % (rv,
                                  self.FunctionName(name),
                                  self.FunctionPList(argList))

    def FunctionDeclaration(self, rv, name, argList):
        """ Format a function declaration """
        # Default is:
        #
        # <returns> functionName(arguments)
        #
        return "%s\n%s%s" % (rv,
                                 self.FunctionName(name),
                                 self.FunctionPList(argList))



    ############################################################
    #
    # Comment Formatting
    #
    ############################################################

    def EndifComment(self,directive):
        """ Any additional comments at the end of an ifdef block """
        return "/* %s */" % (directive)

    def SingleLineComment(self, str):
        """ Format a single-line comment """
        return "/* %s */" % (str)

    def MultiLineComment(self, str):
        """ Format a multiple-line comment """
        lines = str.splitlines(str.count('\n'))
        s = "/*\n"
        for line in lines:
            s += " * %s" % (line)
        s += " */\n"
        return s


    def Comment(self, str):
        """ Format an arbitrary comment string """
        if '\n' in str:
            return self.MultiLineComment(str)
        else:
            return self.SingleLineComment(str)








