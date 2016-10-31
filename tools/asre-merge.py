#!/usr/bin/python
############################################################
#
# Collect and merge all asre documentation files from
# the given directory into a single asre file.
#
# This should be merged with the existing asre tool.
#
############################################################
import os
import sys
import json
import argparse
import gzip

ap = argparse.ArgumentParser("asre-merge")
ap.add_argument("dir", help="Source directory to search.")
ap.add_argument("out", help="Merged output file name.")

ops = ap.parse_args()

def asre_read(f):
    if f.endswith(".gz"):
        fh = gzip.open(f, 'rb')
    else:
        fh = open(f, "r")
    return fh.read()

DATA = []

#
# Find all package asre.json[.gz] files
#
for root, dirs, files in os.walk(ops.dir):
    for f in files:
        if f.startswith("asre.json"):
            js = asre_read(os.path.join(root, f))
            data = json.loads(js)
            DATA = DATA + data

if not os.path.exists(os.path.dirname(ops.out)):
    os.makedirs(os.path.dirname(ops.out))

with open(ops.out, "w") as f:
    f.write(json.dumps(DATA, indent=1))





