#!/ots/sw/osstoolkit/15.1/sles11-x86_64/bin/python3.5
import sys
import os
import numpy as np
import argparse
from numpy import unravel_index


class OT4:
    """Class of object that contains NASTRAN op4 matrices."""

    def __init__(self, name):
        """Method to initialize the OT4 object."""
        self.name = name
        self.ot4 = {}
        self.ot4_names = []
        self.read_ot4()

    def read_ot4(self):
        """Method to read the ot4 file."""
        import time

        # Read the file
        with open(self.name) as f:
            lines = f.read().splitlines()

        # Determine the number of matrices in the ot4
        i_headers = [i for i, val in enumerate(lines) if ',' in val]

        # Determine the name and size of the matrices and allocate.
        for i in i_headers:
            matrix_name = lines[i][32:40].rstrip()
            n_cols = int(lines[i][0:8])
            n_rows = int(lines[i][8:16])
            rec_per_line = int(lines[i][43:44])
            rec_len = int(lines[i][45:47])
            if matrix_name not in self.ot4.keys():
                self.ot4[matrix_name] = np.zeros([n_rows, n_cols])
                self.ot4_names.append(matrix_name)

        # Loop over the data and extract the matrices
        h = 0
        for i, h in enumerate(i_headers):
            ns_cols = self.ot4[self.ot4_names[i]].shape[1]
            ns_rows = self.ot4[self.ot4_names[i]].shape[0]
            ns_per_rec = int(ns_rows / rec_per_line)
            ns_stinger = ns_rows % rec_per_line
            if ns_stinger > 0:
                ns_per_rec += 1
            p = h
            for c in range(0, ns_cols):
                start = 0
                for k in range(0, ns_per_rec + 1):
                    p += 1
                    if k == ns_per_rec and ns_stinger > 0:
                        seg_end = ns_stinger
                    else:
                        seg_end = rec_per_line
                    if k > 0:
                        line_chunk = [lines[p][m:m + rec_len] for m in range(0, len(lines[p]), rec_len)]
                        line_data = list(map(float, line_chunk[0:seg_end]))
                        self.ot4[self.ot4_names[i]][start:start + seg_end, c] = line_data
                        start += seg_end


def ot4_compare():
    """Function to compare two ot4 files and their matrices."""

    parser = argparse.ArgumentParser()
    parser.add_argument('func', help='name of function: ot4_compare')
    parser.add_argument('old_ot4', help='old ot4 file')
    parser.add_argument('new_ot4', help='new ot4 file')
    args = parser.parse_args()
    old_ot4_file = args.old_ot4
    new_ot4_file = args.new_ot4

    # Create the OT4 objects
    old_ot4 = OT4(old_ot4_file)
    new_ot4 = OT4(new_ot4_file)

    # Check to see if they have the same matrices
    if old_ot4.ot4_names != new_ot4.ot4_names:
        raise Exception('!!! Must have the same matrices !!!')

    # For each matrix find the difference
    for mat in old_ot4.ot4_names:
        diff = new_ot4.ot4[mat] - old_ot4.ot4[mat]
        diff_max = np.max(diff)
        diff_min = np.min(diff)
        max_old_pos = unravel_index(diff.argmax(), diff.shape)
        min_old_pos = unravel_index(diff.argmin(), diff.shape)
        max_old_val = old_ot4.ot4[mat][max_old_pos]
        min_old_val = old_ot4.ot4[mat][min_old_pos]
        pct_diff_max = 100 * diff_max / max_old_val
        pct_diff_min = 100 * diff_min / min_old_val
        max_old_pos = tuple([x + 1 for x in list(max_old_pos)])
        min_old_pos = tuple([x + 1 for x in list(min_old_pos)])
        print('%s dmax: %13.5f, %8.3f%% @ %s |\t%s dmin: %13.5f, %8.3f%% @ %s'
              % (mat, diff_max, pct_diff_max, max_old_pos, mat, diff_min, pct_diff_min, min_old_pos))


if __name__ == '__main__':

    nargs = sys.argv.__len__()
    if nargs > 2 and sys.argv[1] == 'ot4_compare':
        ot4_compare()
    elif nargs == 1:
        print('usage: ot4 <function>\n')
        print('\tfunctions:\n')
        print('\t\tot4_compare <old_ot4> <new_ot4>')

    # Testing ------------------------------------------------------------------------
    # Unit Test #1
    if nargs == 2 and sys.argv[1] == 'test1':
        myot4 = OT4('ot4s/s0red_0.ot4')
        ut.unit_test(test='test1', func='ot4', cwd=os.getcwd(), obj=myot4)