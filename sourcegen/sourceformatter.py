###############################################################################
#
# SourceFormatter.py
#
# Base class for all source formatter objects
#
###############################################################################
#
# SourceFormatter objects allow the customization of the look and feel
# for the generated source code. 
#
# This base class provides base functionality. The real definition for 
# a formatting object starts with a language base class. 
#
###############################################################################

class SourceFormatter:
    """ Base class for source formatting decisions during code generation.
    This class should produce only string results"""

    def __init__(self):
        pass
