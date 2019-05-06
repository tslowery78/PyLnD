#!/ots/sw/osstoolkit/15.1/sles11-x86_64/bin/python3.5

from PyLnD.thermal.inc import compare, compare_list
import argparse

# Script to compare inc files.

# Get the command line input options.
parser = argparse.ArgumentParser()
parser.add_argument('--pair', help='Compare two inc files: <old_inc> <new_inc>', nargs='+')
parser.add_argument('--list', help='2-col list of inc files to compare')
args = parser.parse_args()

# Compare the inc files.
if args.pair:
    compare(old_inc=args.pair[0], new_inc=args.pair[1])
elif args.list:
    compare_list(c_list=args.list)
