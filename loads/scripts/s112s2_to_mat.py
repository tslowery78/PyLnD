#!/ots/sw/osstoolkit/15.2/sles11-x86_64/bin/python3.5

# Add loads path
import sys
sys.path.append('/project/issloads/')
import argparse
from PyLnD.loads.sort2_sol112 import SORT2_112

# Get the input SORT2 pch file.
parser = argparse.ArgumentParser()
parser.add_argument("pchfile", help="NASTRAN SORT2 PCH file")
parser.add_argument("matfile", help="MAT file to be output")
args = parser.parse_args()

# Create s2 112 object and output into mat file.
print("\n... converting file to .mat format ...\n\tinput: " + args.pchfile)
my112 = SORT2_112(args.pchfile)
my112.save2mat(args.matfile)
print("... complete ...\n\toutput: " + args.matfile)
