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
#################################################################
#
# SourceFormatter.py
#
# Base class for all source formatter objects
#
#################################################################
#
# SourceFormatter objects allow the customization of the look and feel
# for the generated source code.
#
# This base class provides base functionality. The real definition for
# a formatting object starts with a language base class.
#
#################################################################

class SourceFormatter:
    """ Base class for source formatting decisions during code generation.
    This class should produce only string results"""

    def __init__(self):
        pass
