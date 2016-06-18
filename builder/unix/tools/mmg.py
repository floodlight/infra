#!/usr/bin/python
################################################################
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
################################################################

################################################################
#
# Module Manifest Generator v2.
#
################################################################
import sys
import os
import datetime
import re
import yaml

import logging

logging.basicConfig()
logger = logging.getLogger("MMC")

def generate_manifest_data(dirs=["."],
                           include_yamls=True,
                           include_makefiles=False,
                           generate_missing_yaml=False):

    modules = {}
    duplicates = []

    makefileRE = re.compile(r'\s*MODULE\s*:=\s*(?P<modname>.*)')

    for dirspec in dirs:
        for dir_ in dirspec.split(':'):
            for root, dirs, files in os.walk(os.path.abspath(dir_)):
                for file_ in files:

                    moduleName = None
                    fname = "%s/%s" % (root, file_)

                    root = os.path.realpath(root)

                    if include_makefiles and file_ == "Makefile":
                        for line in open(fname):
                                m = makefileRE.match(line)
                                if m:
                                    moduleName = m.group('modname')
                                    y = os.path.join(root, ".module")
                                    with open(y, "w") as f:
                                        f.write(yaml.dump(dict(name=moduleName), default_flow_style=False))

                    if include_yamls and file_ == ".module":
                        data = yaml.load(open(fname))
                        moduleName = data['name']

                    if moduleName:
                        if moduleName in modules:
                            duplicates.append((moduleName, root, fname))
                        else:
                            modules[moduleName] = root

        return (modules, duplicates)



class ManifestBase(object):
    """ Base class for all module manifest generators. """
    #
    # Provided by the derives classes.
    #

    # Target filename
    target = None

    # Description of file
    desc = None

    # Block comment start, if applicable
    commentStart=""

    # Block comment end, if applicable
    commentStop=""

    def generate_str(self):

        s = ""
        s += self.commentStart
        s += """
##############################################################################
#
# %(DESCRIPTION)s
#
##############################################################################
""" % dict(DESCRIPTION=self.desc)

        s += self.commentStop
        s += self.initsection()

        for modname, root in sorted(self.modules.items()):
            s += self.module(modname, root)

        s += self.denitsection()
        s += "\n"

        return s

    def module(self, modname, root):
        return ""
    def initsection(self):
        return ""
    def denitsection(self):
        return ""

    def generate_file(self, target):
        s = self.generate_str()
        if target == '-':
            print s
        else:
            with open(target, "w") as f:
                f.write(s)


class MakeManifest(ManifestBase):
    """Generates the Manifest.mk file used by the Builder."""
    desc = "Builder Module Manifest."

    def __init__(self, modules):
        self.modules = modules

    def initsection(self):
        return ""

    def module(self, modname, root):
        return "%s_BASEDIR := %s\n" % (modname, root)

    def denitsection(self):
        return "\n\nALL_MODULES := $(ALL_MODULES) %s" % (
            " ".join(sorted(self.modules.keys())))

if __name__ == "__main__":

    import argparse

    ap = argparse.ArgumentParser("Module Manifest Generator")
    ap.add_argument("config", help="Yaml Configuration File.")
    ap.add_argument("root", help="Relative root directory.")
    ap.add_argument("--only-if-missing", action='store_true')
    ops = ap.parse_args()
    config = yaml.load(open(ops.config))
    dirs = [ os.path.join(ops.root, d) for d in config['directories'] ]
    target = os.path.join(ops.root, config['manifest'])
    if not os.path.exists(target) or ops.only_if_missing is False:
        data = generate_manifest_data(dirs)[0]
        MakeManifest(data).generate_file(target)
    print target


