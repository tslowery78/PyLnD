#!/ots/sw/osstoolkit/15.1/sles11-x86_64/bin/python3.5

import numpy as np
import argparse
import sys
#import utilities.unit_test as ut
import os
from numpy import unravel_index


class TXT:
    """Class of loads txt file output from TSL process."""

    def __init__(self, name):
        """Method to initialize TXT."""
        self.name = name
        self.txt_type = ''
        self.elements = []
        self.opers = []
        self.txt = []
        self.read_txt()

    def read_txt(self):
        """Method to read the txt file."""

        # Determine what type the txt file is.
        if 'DEFLS' and 'WS' in self.name:
            self.txt_type = 'mt_rail'
        elif 'FLOAT' in self.name:
            self.txt_type = 'float'
        elif 'MAX' in self.name:
            self.txt_type = 'maxes'

        # Read the data
        if self.txt_type == 'mt_rail':
            with open(self.name) as f:
                lines = f.readlines()
            # Determine the header lines in the list
            i_headers = [i for i, val in enumerate(lines) if 'GRID' in val]
            n_tsteps = i_headers[1] - i_headers[0] - 2
            i_headers = np.asarray(i_headers)
            i_opers = i_headers - 1
            np_lines = np.asarray(lines)
            self.opers = np_lines[i_opers]
            n_opers = self.opers.__len__()
            line1 = lines[2]
            self.elements.append(int(line1[0:7]))
            self.elements.append(int(line1[32:38]))
            self.elements.append(int(line1[63:69]))
            self.elements.append(int(line1[94:100]))
            # Extract the values
            self.txt = np.zeros([n_opers * n_tsteps, 12])
            l_format = np.array([7, 8, 8, 8])
            l_format = np.tile(l_format, 4)
            j = 0
            for i, line in enumerate(lines):
                start = 0; stop = 0
                if i not in i_headers and i not in i_opers:
                    j += 1; k = 0
                    for e in l_format:
                        stop = stop + e
                        line_str = line[start:stop]
                        start = stop
                        if e == 8:
                            k += 1
                            self.txt[j - 1, k - 1] = float(line_str)
        elif self.txt_type == 'float':
            with open(self.name) as f:
                lines = f.readlines()
            # Determine the header lines in the list
            i_opers = [i for i, val in enumerate(lines) if val[0:1] != ' ']
            np_lines = np.asarray(lines)
            n_tsteps = i_opers[1] - i_opers[0] - 1
            self.opers = np_lines[i_opers]
            n_opers = self.opers.__len__()
            # Extract the values
            self.txt = np.zeros([n_opers * n_tsteps, 9])
            j = 0
            for i, line in enumerate(lines):
                if i not in i_opers:
                    l_split = line.split()
                    new_row = list(map(float, l_split))
                    self.txt[j, :] = new_row
                    j += 1
        elif self.txt_type == 'maxes':
            with open(self.name) as f:
                lines = f.readlines()
            n_rows = lines.__len__() - 1
            n_cols = lines[0].split().__len__() - 1
            self.txt = np.zeros([n_rows, n_cols])
            for i, line in enumerate(lines):
                if 'Ele.ID' not in line[0:10]:
                    l_split = line.split()
                    self.elements.append(int(l_split[0]))
                    new_row = list(map(float, l_split[1:]))
                    self.txt[i - 1, :] = new_row
        else:
            # Read the TXT file and determine it's type.
            with open(self.name) as f:
                lines = f.readlines()
            n_rows = lines.__len__()
            n_cols = lines[0].split().__len__()
            self.txt = np.zeros([n_rows, n_cols])
            for i, line in enumerate(lines):
                self.txt[i, :] = list(map(float, line.split()))


def txt_compare(**kwargs):
    """Function to compare two loads txt files."""

    if 'old_txt' not in kwargs.keys():
        parser = argparse.ArgumentParser()
        parser.add_argument('func', help='name of function: txt_compare')
        parser.add_argument('old_txt', help='old txt file')
        parser.add_argument('new_txt', help='new txt file')
        args = parser.parse_args()
        old_txt_file = args.old_txt
        new_txt_file = args.new_txt
    else:
        old_txt_file = kwargs['old_txt']
        new_txt_file = kwargs['new_txt']

    # Load the old and new as TXT objects.
    old_txt = TXT(old_txt_file)
    new_txt = TXT(new_txt_file)

    # Check if they are compatible.
    if old_txt.txt_type != new_txt.txt_type:
        raise Exception('!!! old txt is type %s and new txt is type %s !!!'
                        % (old_txt.txt_type, new_txt.txt_type))
    if old_txt.txt.shape != new_txt.txt.shape:
        raise Exception('!!! old txt is shape %s and new txt is shape %s !!!'
                        % (old_txt.txt.shape, new_txt.txt.shape))

    # Check if the MAXBARFORCES have the same element list.
    if old_txt.txt_type == 'MAXBARFORCES':
        if set(old_txt.elements) != set(new_txt.elements):
            raise Exception('!!! These MAXBARFORCES have different elements !!!')

    # Find the difference between the matrices
    diff = new_txt.txt - old_txt.txt

    # Determine the pct difference from old to new.
    np.seterr(divide='ignore', invalid='ignore')
    pct_diff = np.divide(diff, old_txt.txt)
    pct_diff[np.isnan(pct_diff)] = 0
    pct_diff = 100 * pct_diff

    # Find the stats and print.
    diff_max = np.max(diff)
    diff_min = np.min(diff)
    max_old_pos = unravel_index(diff.argmax(), diff.shape)
    min_old_pos = unravel_index(diff.argmin(), diff.shape)
    max_old_val = old_txt.txt[max_old_pos]
    min_old_val = old_txt.txt[min_old_pos]
    pct_diff_max = 100 * diff_max / max_old_val
    pct_diff_min = 100 * diff_min / min_old_val
    max_old_pos = tuple([x + 1 for x in list(max_old_pos)])
    min_old_pos = tuple([x + 1 for x in list(min_old_pos)])
    if old_txt.txt_type == '':
        print('max: %13.5f, %8.3f%% @ (%3d, %3d) |\tmin: %13.5f, %8.3f%% @ (%3d, %3d)'
          % (diff_max, pct_diff_max, max_old_pos[0], max_old_pos[1], diff_min,
             pct_diff_min, min_old_pos[0], min_old_pos[1]))
    else:
        print('max: %13.5f, %8.3f%% |\tmin: %13.5f, %8.3f%%'
          % (diff_max, pct_diff_max, diff_min, pct_diff_min))


def list_compare():
    """Method function to compare lists of txt files in two columns."""

    parser = argparse.ArgumentParser()
    parser.add_argument('func', help='name of function: list_compare')
    parser.add_argument('list_file', help='2-col list of txt files to compare')
    args = parser.parse_args()

    # Open the list file and read.
    with open(args.list_file) as f:
        c_list = f.readlines()

    # Loop over and compare
    for line in c_list:
        l_split = line.split()
        old_txt = l_split[0]
        new_txt = l_split[1]
        txt_compare(old_txt=old_txt, new_txt=new_txt)


if __name__ == '__main__':

    nargs = sys.argv.__len__()
    if nargs > 2 and sys.argv[1] == 'txt_compare':
        txt_compare()
    if nargs > 2 and sys.argv[1] == 'list_compare':
        list_compare()
    elif nargs == 1:
        print('usage: loads_txt <function>\n')
        print('\tfunctions:\n')
        print('\t\ttxt_compare <old_txt> <new_txt>')
        print('\t\tlist_compare <list of txt to compare in 2-col>')

    # Testing ------------------------------------------------------------------------
    # Unit Test #1: standard txt
    if nargs == 2 and sys.argv[1] == 'test1':
        mytxt = TXT('loads_txt_files/SH1_260417.txt')
        ut.unit_test(test='test1', func='loads_txt', cwd=os.getcwd(), obj=mytxt)

    # Unit Test #3: MAXBARFORCES
    elif nargs == 2 and sys.argv[1] == 'test3':
        mytxt = TXT('loads_txt_files/MAXBARFORCES.TXT')
        ut.unit_test(test='test3', func='loads_txt', cwd=os.getcwd(), obj=mytxt)

    # Unit Test #6: mt_rails
    elif nargs == 2 and sys.argv[1] == 'test6':
        mytxt = TXT('loads_txt_files/S3_WS1_DEFLS.TXT')
        ut.unit_test(test='test6', func='loads_txt', cwd=os.getcwd(), obj=mytxt)

    # Unit Test #8: float
    elif nargs == 2 and sys.argv[1] == 'test8':
        mytxt = TXT('loads_txt_files/FLOATS1S3.TXT')
        ut.unit_test(test='test8', func='loads_txt', cwd=os.getcwd(), obj=mytxt)

    # Unit Test #10: float
    elif nargs == 2 and sys.argv[1] == 'test10':
        mytxt = TXT('loads_txt_files/MAXQUADSTRESSES.TXT')
        ut.unit_test(test='test10', func='loads_txt', cwd=os.getcwd(), obj=mytxt)
