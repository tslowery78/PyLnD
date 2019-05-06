#!/ots/sw/osstoolkit/15.1/sles11-x86_64/bin/python3.5

# Script to calculate the difference between two txt files.
import argparse
import numpy as np

# Read in the two txt files that will be subtracted.
parser = argparse.ArgumentParser()
parser.add_argument("txt1", help="1st txt file: txt1 - txt2")
parser.add_argument("txt2", help="2nd txt file: txt1 - txt2")
parser.add_argument("txtout", help="output txt file")
args = parser.parse_args()

# Read in the txt files.
txt1 = np.loadtxt(args.txt1)
txt2 = np.loadtxt(args.txt2)

# Subtract and write to the output file.
txt_diff = txt1 - txt2
np.savetxt(args.txtout, txt_diff, fmt='%8.2f', delimiter='  ')
print("--- %s =  %s - %s" % (args.txtout, args.txt1, args.txt2))
print("--- number of OPERs:\t %i" % txt_diff.shape[0])
print("--- number of time steps:\t %i" % txt_diff.shape[1])
