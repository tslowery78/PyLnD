#!/ots/sw/osstoolkit/15.1/sles11-x86_64/bin/python3.5
import sys
import os
import utilities.unit_test as ut
import numpy as np
import argparse


class BETA_CODE:
    """Class for object that represents a beta code.
        beta, code (corresponding to OPER Case Matrix)
    """

    def __init__(self, bc_file):
        """Method to initialize BETA_CODE class."""
        self.bc_file = bc_file
        self.beta = []
        self.code = []
        self.load_bc()

    def load_bc(self):
        """Method to load the beta code file."""

        # Open the file and read all the lines.
        array = np.loadtxt(self.bc_file)

        # Convert the columns to appropriate type.
        self.beta = array[:, 0]
        self.code = array[:, 1].astype(int)


def bc_recode(**kwargs):
    """Function to recode a beta code using a different Case Matrix."""

    # Get the command line arguments or function arguments.
    if not bool(kwargs):
        parser = argparse.ArgumentParser()
        parser.add_argument('bc_recode', help='name of function: bc_recode')
        parser.add_argument('beta_code', help='2-col list of beta, code (case matrix code)')
        parser.add_argument('reorder', help='2-col list of old code, new code')
        parser.add_argument('new_bc', help='file name of new beta code output')
        args = parser.parse_args()
        beta_code = args.beta_code
        reorder = args.reorder
        new_bc = args.new_bc
    else:
        beta_code = kwargs['beta_code']
        reorder = kwargs['reorder']
        new_bc = kwargs['new_bc']

    # Create beta_code object and read the reorder codes.
    bc = BETA_CODE(beta_code)
    reo = np.loadtxt(reorder, dtype='int')

    # Create new code for each entry in the original beta code.
    new_code = np.zeros_like(bc.code)
    for i, beta in enumerate(bc.beta):
        index = bc.code[i] == reo[:, 0]
        new_code[i] = reo[index, 1][0]
        pass

    # Output new recoded beta code.
    with open(new_bc, 'w') as f:
        for i, beta in enumerate(bc.beta):
            f.write('%s\t%s\n' % (beta, new_code[i]))


if __name__ == '__main__':

    nargs = sys.argv.__len__()
    if nargs >= 2 and sys.argv[1] == 'bc_recode':
        bc_recode()
    elif nargs == 1:
        print('usage: beta_code <function>\n')
        print('\tfunctions:\n')
        print('\t\tbc_recode <beta_code> <reorder> <new_bc>')

    # Testing ------------------------------------------------------------------------
    # Unit Test #1
    if nargs == 2 and sys.argv[1] == 'test1':
        mybc= BETA_CODE('beta_codes/beta_code_20a.txt')
        ut.unit_test(test='test1', func='beta_code', cwd=os.getcwd(), obj=mybc)

    # Unit Test #2
    # python beta_code.py bc_recode beta_codes/beta_code_20a.txt beta_codes/reorder_bc_20a.txt
    #  beta_codes/beta_code_20a_elcs.txt >test/beta_code/test2/test2_out.txt

    # Unit Test #3
    if nargs == 2 and sys.argv[1] == 'test3':
        os.makedirs('test/beta_code/test3/',exist_ok=True)
        bc_recode(beta_code='beta_codes/beta_code_20a.txt', reorder='beta_codes/reorder_bc_20a.txt',
                  new_bc='test/beta_code/test3/beta_code_20a_elcs.txt')
