#!/usr/bin/python
###############################################################################
#
# CObjectGenerator.py
#
# Base generator class for C Language Objects
#
###############################################################################
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
