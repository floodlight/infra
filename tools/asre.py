#!/usr/bin/python
############################################################
#
# AIM Syslog Reference Extractor
#
# Extracts AIM_SYSLOG_REFERENCE meta strings from compiled
# binaries.
#
############################################################
import os
import sys
import argparse
import re
import subprocess
import logging
import json
import pprint
import yaml

logging.basicConfig()
LOGGER=logging.getLogger("asre")

#
# All meta strings start with this tag.
#
TAG="AIM_SYSLOG_REFERENCE:"

#
# All extracted entries.
#
DATA=[]


def aim_syslog_reference_data(binary):
    # Get all strings from the binary
    try:
        strings = subprocess.check_output(['strings', binary])
    except subprocess.CalledProcessError:
        LOGGER.error("string extraction failed on file %s." % binary)
        sys.exit(1)

    # Eval all matching strings and return the data
    data = []
    for s in strings.split('\n'):
        if s.startswith(TAG):
            ds = s.replace(TAG, '')
            # The reference data is formatted as a native python dict
            data.append(eval(ds))
    return data


def process_file(f):
    if not os.path.exists(f):
        LOGGER.error("The file '%s' does not exist.", f)
        sys.exit(1)

    global DATA
    DATA = DATA + aim_syslog_reference_data(f)


ap = argparse.ArgumentParser(description="AIM Syslog Reference Extractor.")

ap.add_argument("target", help="Extract references from the given file or all files in the given directory.")
ap.add_argument("--out", help="Append data to the given file.")
ap.add_argument("--overwrite", help="Overwrite the output file. The default is to append.", action='store_true')
ap.add_argument("--format", help="Output format. The default is JSON", choices=['j', 'p', 'y', 'json', 'python', 'yaml' ], default='json')
ops = ap.parse_args()

if os.path.isdir(ops.target):
    for root, dirs, files in os.walk(ops.target):
        for f in files:
            process_file("%s/%s" % (root, f))
else:
    process_file(ops.target)


if ops.format in ['json', 'j']:
    OUTPUT = json.dumps(DATA, indent=1)
elif ops.format in ['python', 'p']:
    OUTPUT = pprint.pformat(DATA)
elif ops.format in ['yaml', 'y' ]:
    OUTPUT = yaml.dump(DATA)
else:
    LOGGER.error("Format option '%s' is not implemented." % ops.format)
    sys.exit(1)

if ops.out:
    mode = "w" if ops.overwrite else "a"
    with open(ops.out, mode) as f:
        f.write(OUTPUT)

else:
    print OUTPUT



