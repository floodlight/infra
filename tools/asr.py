#!/usr/bin/python2
############################################################
#
# AIM Syslog Reference Tool
#
# Extracts and manipulates AIM_SYSLOG_REFERENCE meta data
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
import StringIO

class AimSyslogReference(object):

    TAG="AIM_SYSLOG_REFERENCE:"
    ASR_NAME="asr.json"

    def __init__(self, logger=None, data=None):
        self.data = []

        self.logger = logger
        if self.logger is None:
            logging.basicConfig()
            self.logger = logging.getLogger(self.__class__.__name__)

        if data:
            self.__asr_merge(data)

    def __extract(self, binary, accumulate=True):
        self.logger.debug("Extracting %s..." % binary)
        # Get all strings from the binary
        try:
            strings = subprocess.check_output(['strings', binary])
        except subprocess.CalledProcessError:
            self.logger.error("string extraction failed on file %s." % binary)
            return None

        # Eval all matching strings and return the data
        data = []
        for s in strings.split('\n'):
            if s.startswith(self.TAG):
                ds = s.replace(self.TAG, '')
                # The reference data is formatted as a native python dict
                self.logger.info("%s:%s..." % (binary, ds))
                data.append(eval(ds))

        # Accumulate all data
        if accumulate:
            self.data += data

        # Return just this file's data
        return data

    def extract(self, target, accumulate=True):
        if os.path.isdir(target):
            for root, dirs, files in os.walk(target):
                for f in files:
                    self.__extract(os.path.join(root, f))
            return self.data
        else:
            return __extract(target, accumulate=accumulate)


    def _asr_read(self, fname):
        if fname.endswith(".gz"):
            fh = gzip.open(fname, 'rb')
        else:
            fh = open(fname, "r")
        return fh.read()

    def __asr_merge(self, fname):
        js = self._asr_read(fname)
        data = json.loads(js)
        self.data += data

    def merge(self, target):
        if type(target) is str:
            if os.path.exists(target):
                if os.path.isdir(target):
                    for root, dirs, files in os.walk(target):
                        for f in files:
                            if f.startswith(self.ASR_NAME):
                                self.__asr_merge(os.path.join(root, f))
                else:
                    self.__asr_merge(target)
            else:
                raise ValueError("target file %s does not exist." % target)
        elif type(target) is list:
            self.data += target
        else:
            raise ValueError("target type %s cannot be merged." % type(target))

    def get(self):
        return self.data


    JSON_FORMATS=['j', 'json']
    PYTHON_FORMATS=['p', 'python']
    YAML_FORMATS=['y', 'yaml']
    TEXT_FORMATS=['t', 'text']
    HTML_FORMATS=['h', 'html']
    ALL_FORMATS = JSON_FORMATS + PYTHON_FORMATS + YAML_FORMATS + TEXT_FORMATS + HTML_FORMATS
    DEFAULT_FORMAT='json'

    def formats(self, fmt):
        if fmt in self.JSON_FORMATS:
            out = json.dumps(self.data, indent=1)
        elif fmt in self.PYTHON_FORMATS:
            out = pprint.pformat(self.data)
        elif fmt in self.YAML_FORMATS:
            out = yaml.dump(self.data)
        elif fmt in self.TEXT_FORMATS:
            out = self._format_text()
        elif fmt in self.HTML_FORMATS:
            out = self._format_html()
        else:
            raise ValueError("unrecognized fmt '%s'" % fmt)
        return out

    def format(self, fname, fmt, mode='w'):
        out = self.formats(fmt)

        if fname:
            if type(fname) is file:
                fname.write(out)
            elif type(fname) is str:
                if fname == '-' or fname == 'stdout':
                    sys.stdout.write(out)
                else:
                    if mode not in ['w', 'a']:
                        raise ValueError("unrecognized write mode '%s'" % mode)
                    with open(fname, mode) as f:
                        f.write(out)

    def _format_text(self):
        s = ""
        for entry in self.data:
            s += "Level:  %s\n" % entry['level']
            s += "Format: %s\n" % entry['format']
            s += "Doc:    %s\n" % entry['doc']
            s += "\n"
        return s

    def _format_html(self):
        raise RuntimeError("Not implemented.")

    @staticmethod
    def main():
        import argparse

        ap = argparse.ArgumentParser("ASR Tool")
        ap.add_argument("--asr-in",  help="Input ASR data (json)")
        ap.add_argument("--extract", help="File or directory from which to extract ASR data.")
        ap.add_argument("--merge",   help="File or directory from which to merge asr.json files.")
        ap.add_argument("--format",  help="Output format. The default is JSON.", choices = AimSyslogReference.ALL_FORMATS, default=AimSyslogReference.DEFAULT_FORMAT)
        ap.add_argument("--out",     help="Output file.", default='stdout')
        ap.add_argument("--mode",    help="Output write mode.", default='w')
        ap.add_argument("--verbose", help="Verbose logging.", action='store_true')
        ap.add_argument("--quiet",   help="Quiet.", action='store_true')
        ops = ap.parse_args()

        logging.basicConfig()
        logger = logging.getLogger("asrtool")

        logger.setLevel(logging.WARN)
        if ops.quiet:
            logger.setLevel(logging.ERROR)
        if ops.verbose:
            logger.setLevel(logging.DEBUG)

        asro = AimSyslogReference(logger=logger)

        if ops.asr_in:
            asro.merge(ops.asr_in)

        if ops.merge:
            asro.merge(ops.merge)

        if ops.extract:
            asro.extract(ops.extract)

        asro.format(fname=ops.out, fmt=ops.format, mode=ops.mode)

if __name__ == '__main__':
    AimSyslogReference.main()








