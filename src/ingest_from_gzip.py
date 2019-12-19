#!/bin/env python3


# +
# import(s)
# -

from src.ingest import do_ingest
from src.utils.utils import *

import argparse
import base64
import sys
import tarfile


# +
# __doc__ string
# -
__doc__ = """
    % python3 ingest_from_gzip.py --help
"""


# +
# logging
# -
logger = UtilsLogger('ingest_from_gzip').logger


# +
# function: read_avro_file()
# -
def read_avro_file(infile=''):

    # check input(s)
    if not os.path.isfile(infile):
        raise Exception('read_avros() entry: infile is empty')

    # read file
    with tarfile.open(name=infile, mode='r|gz') as _tar:

        # do while ...
        while True:

            member = _tar.next()
            if member is not None:
                logger.info('extracting {}'.format(member.name))
            else:
                logger.info('done extracting archive contents')
                break

            with _tar.extractfile(member) as _f:
                fencoded = base64.b64encode(_f.read()).decode('UTF-8')
                logger.info('ingesting {}'.format(member.name))
                do_ingest(fencoded)


# +
# main()
# -
if __name__ == '__main__':

    # get command line argument(s)
    _parser = argparse.ArgumentParser(description='Ingest AVRO file manually',
                                      formatter_class=argparse.RawTextHelpFormatter)
    _parser.add_argument('-f', '--file', default='', help="""Input file""")
    args = _parser.parse_args()

    # execute
    if os.path.isfile(os.path.abspath(os.path.expanduser(args.file))):
        read_avro_file(os.path.abspath(os.path.expanduser(args.file)))
    else:
        print(f'<<ERROR>> Insufficient command line arguments specified\nUse: python3 {sys.argv[0]} --help')
