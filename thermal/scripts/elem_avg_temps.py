#!/ots/sw/osstoolkit/15.1/sles11-x86_64/bin/python3.5

import argparse
from PyLnD.thermal.tth import TTH
import numpy as np

# Read in the inc filename and element id lists.
parser = argparse.ArgumentParser()
parser.add_argument("inc_lis", help="list of inc files")
parser.add_argument("elem_lis", help="list of element id's to average")
parser.add_argument("out_file", help="output name for avg temperatures")
args = parser.parse_args()

# Open the list of inc files and read.
print("--- reading from this inc file list:\t %s" % args.inc_lis)
with open(args.inc_lis) as f:
    inc_lis = f.read().splitlines()

# Open the list of elem id's and read.
print("--- using these element/grid id's in this list:\t %s" % args.elem_lis)
with open(args.elem_lis) as f:
    elem_lis = f.read().splitlines()

# Get the temperature time history of each element id and calculate the average.
tth = TTH(incfiles=inc_lis, elems=elem_lis)

# Write the element average temperatures to a txt file.
np.savetxt(args.out_file, tth.avg_tth.T, fmt='%8.2f', delimiter='  ')
print("--- average temperature txt file output:\t {0}".format(args.out_file))
print("--- number of OPERs:\t {0}".format(tth.n_sc))
print("--- number of time steps:\t {0}".format(tth.num_inc))
