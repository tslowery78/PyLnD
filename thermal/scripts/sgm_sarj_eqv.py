#!/ots/sw/osstoolkit/15.1/sles11-x86_64/bin/python3.5

from PyLnD.thermal.inc import SGM
import argparse
import numpy as np
import sys

# Get the sgm angles output and the list of sgm files from user.
parser = argparse.ArgumentParser()
parser.add_argument("--sgm_files", help="List of sgm files", nargs='+')
args = parser.parse_args()
if len(sys.argv) == 1:
    parser.print_help(sys.stderr)
    sys.exit(1)

# Loop over each sgm file and create the equivalent sarj angle files (.esa).
for sgm_file in args.sgm_files:
    esa_file = sgm_file.replace('.sgm', '.esa')
    print('Creating {0}'.format(esa_file))
    sgm = SGM(sgm_file)
    out = np.asarray([sgm.sgm['PSARJ'], sgm.psarj, sgm.sgm['SSARJ'], sgm.ssarj]).transpose()
    np.savetxt(esa_file, out, delimiter=',', header='psarj_real, psarj_eqv, ssarj_real, ssarj_eqv', fmt='%5.1f')
