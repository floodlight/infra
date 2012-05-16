###############################################################################
#
# Utility routines
#
###############################################################################
import types
import copy

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


class DotDict(dict):
    """ Access keys in a nested dictionary using dot notation """

    def __getattr__(self, attr):
        item = self.get(attr, None)
        if type(item) == types.DictType:
            item = DotDict(item)
        return item

    __setattr__= dict.__setitem__
    __delattr__= dict.__delitem__

