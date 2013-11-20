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
# Utility routines
#
#################################################################
import copy
import types

def comma(member, memberList):
    """ Convenience function for processing comma lists.
    A comma is returned for all but the last member in the list """
    if not (member is memberList[-1]):
        return ','
    else:
        return ''

def commaspace(member, memberList):
    """ Just like comma, but returns a comma+space """
    if member is memberList[-1]:
        return ''
    else:
        return ', '

def listifyElements(list_):
    """ Converts a list of objects to a list of lists """
    if isinstance(list_, str):
        # support a single entry
        return [ list_ ]

    if isinstance(list_, list):
        n = []
        for e in list_:
            if isinstance(e, str):
                n.append([ e ])
            elif isinstance(e, list):
                n.append(e)
            elif isinstance(e, dict):
                for k, v in e.iteritems():
                    n.append([ k, v ])
        return n

    return None


def uniqueElements(l):
    """Fixes lists of constants to have unique elements"""
    return [ "%s" % x for x in l]

def fcall(name, args):
    """Function call"""
    if isinstance(args, str):
        args = [args]

    if len(args) == 1 and isinstance(args[0], list):
        args = args[0]

    c = name + "("
    largs = uniqueElements(args)
    for arg in largs:
        c += str(arg)
        c += commaspace(arg, largs)
    c += ")"
    return c


def ifndef(def_, val):
    return "#ifndef %s\n#define %s %s\n#endif\n" % (def_, def_, val)


class DotDict(dict):
    """ Access keys in a nested dictionary using dot notation """

    def __getattr__(self, attr):
        item = self.get(attr, None)
        if type(item) == types.DictType:
            item = DotDict(item)
        return item

    __setattr__= dict.__setitem__
    __delattr__= dict.__delitem__

