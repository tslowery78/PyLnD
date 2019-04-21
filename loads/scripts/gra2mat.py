#!/ots/sw/osstoolkit/15.4/sles12-x86_64/bin/python3.6

# Add loads path
import sys
sys.path.append('/project/issloads/')
import argparse
from PyLnD.loads.gra import GRA

# Get the input GRA file.
parser = argparse.ArgumentParser()
parser.add_argument("gra", help="Screening code output gra time history")
parser.add_argument("out", help="MAT file to be output")
args = parser.parse_args()

# Load the results from the screening code
print('\n... converting GRA file into .mat file ...\n\tinput: {0}'
    .format(args.gra))
gra = GRA(args.gra)
gra.save2mat(args.out)
print('... complete ...\n\toutput: {0}'.format(args.out))
