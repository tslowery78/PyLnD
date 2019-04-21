#!/ots/sw/osstoolkit/15.1/sles11-x86_64/bin/python3.5

# Add loads path
import sys
sys.path.append('/project/issloads/')

from PyLnD.loads.op4 import OP4
import argparse

# Script to convert an OP4 file into a Matlab .mat file.

# Get the command line input options.
parser = argparse.ArgumentParser()
parser.add_argument('--file', help='Convert one op4 file: <op4 file> <mat file>', nargs='+')
args = parser.parse_args()

op4file = args.file[0]
matfile = args.file[1]

# Load the op4 and convert to a mat file.
op4 = OP4(op4=op4file, type='ascii')
op4.save2mat(matfile)
