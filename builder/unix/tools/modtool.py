#!/usr/bin/python
############################################################
#
# Module Management Tool
#
############################################################
import os
import sys
import yaml
import json
import logging


class ModuleTool(object):
    def __init__(self, logger):
        self.modules = {}
        self.logger = logger

    def __load_module(self, fname):
        try:
            d = yaml.load(open(fname))
        except:
            self.logger.exception()

        if 'name' not in d:
            raise AttributeError("invalid module file")

        if d['name'] in self.modules:
            raise RuntimeError("duplicate module")

        if 'depends' in d and type(d['depends']) is str:
            d['depends'] = [ d['depends'] ]

        d['dir'] = os.path.dirname(fname)
        self.modules[d['name']] = d

    def load_modules(self, target):
        target = os.path.abspath(target)
        if os.path.isdir(target):
            for (root, dirs, files) in os.walk(target):
                for f in files:
                    if f == ".module":
                        self.__load_module(os.path.join(root, f))
        elif os.path.isfile(target):
            self.__load_module(target)

    def dbread(self, j):
        self.modules = json.load(open(j))

    def dbwrite(self, j):
        with open(j, "w") as f:
            f.write(json.dumps(self.modules, indent=2))

    def write_make_manifest(self, handle):
        for (mname, module) in sorted(self.modules.iteritems()):
            handle.write("%s_BASEDIR := %s\n" % (mname, module['dir']))

    def make_manifest(self, mk):
        if mk in [ '-', 'stdout' ]:
            self.write_make_manifest(sys.stdout)
        else:
            with open(mk, "w") as f:
                self.write_make_manifest(f)

    def dependmodules(self, modules):
        #
        # Dependent modules can only be added to the end of the list.
        # The original order of the explicit modules must remain unchanged.
        #
        # dp contains all of the dependent modules
        dp = []
        for module in modules:
            if module not in self.modules:
                raise AttributeError("module %s does not exist." % module)
            elif 'depends' in self.modules[module]:
                dp += self.dependmodules(self.modules[module]['depends'])

        # The input list and all resulting dependencies in original order
        allmodules = modules + list(set(dp))

        # This makes sure there are no duplicates between the original list
        # the dependency list that was just added (while keeping the original order)
        rv = sorted(set(allmodules),key=lambda x: allmodules.index(x))

        return rv


    def show_dependencies(self):
        for (nname, module) in sorted(self.modules.iteritems()):
            print "%s : %s" % (module['name'], module.get('depends', None))



if __name__ == '__main__':
    import argparse

    logging.basicConfig()
    logger = logging.getLogger("modtool")
    ap = argparse.ArgumentParser("modtool")

    ap.add_argument("--db", help="Load module db from the given file.")
    ap.add_argument("--dbroot", help="Generate the db from the given root if the db file is missing. This will also write the data to the file for future use.")
    ap.add_argument("--load-dir", help="Load data from the given directory.")
    ap.add_argument("--make-manifest", help="Generate the module manifest makefile.")
    ap.add_argument("--dependmodules", help="Generate all required modules based on inter-module dependencies", nargs='+')
    ap.add_argument("--show-dependencies", help="Show module dependencies.", action='store_true')
    ap.add_argument("--force", help="Force regeneration of existing files.", action='store_true')

    ops = ap.parse_args()

    mm = ModuleTool(logger)

    if ops.db:
        if os.path.exists(ops.db):
            mm.dbread(ops.db)
        else:
            if ops.dbroot:
                mm.load_modules(ops.dbroot)
                mm.dbwrite(ops.db)
            else:
                logger.error("The db file '%s' does not exist.", ops.db)
                sys.exit(1)

    if ops.load_dir:
        mm.load_modules(ops.load_dir)


    if ops.show_dependencies:
        mm.show_dependencies()

    if ops.dependmodules:
        print " ".join(mm.dependmodules(ops.dependmodules))

    if ops.make_manifest:
        if not os.path.exists(ops.make_manifest) or ops.force:
            mm.make_manifest(ops.make_manifest)
        print ops.make_manifest
