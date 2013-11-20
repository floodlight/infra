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
# cm.py
#
# Configuration data manager.
#
# Allows source definitions to be imported via
# - Python Modules
# - YAML files
# - Direct dicts
#
#################################################################

from util import *
import yaml

class ConfigManager:
    def __init__(self):
        self.configs = []

    def ImportPModule(self, filename):
        """Import a Python definition Module"""
        self.configs.append(imp.load_source("X", filename))

    def ImportYModule(self, filename):
        """Import a YAML definition file"""
        fp = open(filename);
        self.configs.append(DotDict(yaml.load(fp)))
        fp.close()

    def ImportDict(self, d):
        """ Import a dict definition """
        if isinstance(d, dict):
            d = DotDict(d)
        if isinstance(d, DotDict):
            if not definitions in d:
                d = { definitions : d }
            self.configs.append(d)
        else:
            raise Exception("ImportDict: not a dict")


    def Import(self, x):
        """ Import and object or file """
        if isinstance(x, dict) or isinstance(x, DotDict):
            return self.ImportDict(x)
        elif isinstance(x, str):
            if x.endswith(".py"):
                return self.ImportPModule(x)
            elif ( x.endswith(".y") or x.endswith(".yaml") or
                   x.endswith(".yml")):
                return self.ImportYModule(x)

        raise Exception("Cannot import object '%s'" % str(x))


    def FindTypedEntry(self, type_, name, data=None):
        """ Find a config type definition """
        if data is not None:
            return data

        for c in self.configs:
            if type_ in c.definitions:
                if name in c.definitions[type_]:
                    return c.definitions[type_][name]

        return None

    def ObjectNameList(self, type_, name="ALL"):
        """Returns a list of names for the given type

        If 'name' is "ALL" (the default), then the names of all objects
        of the given type in the configuration are returned.

        If 'name' matches an alias, as defined in the special
        __aliases__ section for the given type, then those names
        are returned.

        If 'name' is the name of an actual object, then that name
        is returned (in the list).

        The purpose of this function is to facilitate aliases, object
        lists, and multiple object construction during generation."""

        allList = []
        for c in self.configs:
            if type_ in c.definitions:

                # Check for an alias first, if they exist.
                # Note -- this allows you to redefine 'ALL' as you see fit
                if '__aliases__' in c.definitions[type_]:
                    if name in c.definitions[type_]['__aliases__']:
                        return c.definitions[type_]['__aliases__'][name]

                if name in c.definitions[type_]:
                    # Specific object name
                    return [ name ]

                # Append all keys and keep searching
                for k in c.definitions[type_].keys():
                    if not k.startswith('__'):
                        allList.append(k)

        if name == "ALL":
            return list(set(allList))
        else:
            return []



