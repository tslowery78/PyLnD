#!/ots/sw/osstoolkit/15.1/sles11-x86_64/bin/python3.5
from PyLnD.loads.f06_results import USET
import sys
import argparse
import json


def make_merge_vec():
    """Function to create the merge vec from a list of dofs and a uset table."""
    parser = argparse.ArgumentParser()
    parser.add_argument('func', help='name of function: lookup_mvec')
    parser.add_argument('mvec_dofs', help='merge vec dofs (case, grid, idof)')
    parser.add_argument('uset', help='uset table f06 file')
    parser.add_argument('set', help='set the merge vec belongs to')
    parser.add_argument('ot4', help='output ot4 merge vec')
    args = parser.parse_args()

    # Create the MVEC object
    mvec = MVEC(args.mvec_dofs)
    mvec.read_mvec_dof(uset=args.uset, mvec_dof=args.mvec_dofs)
    mvec.find_u_pos(set=args.set)
    mvec.write_merge_vec(ot4=args.ot4)

def lookup_mvec():
    """Function to lookup the mvec in the uset table."""
    parser = argparse.ArgumentParser()
    parser.add_argument('func', help='name of function: lookup_mvec')
    parser.add_argument('uset', help='uset table f06 file')
    parser.add_argument('mvec', help='merge vec ot4 file')
    parser.add_argument('set', help='set the merge vec belongs to')
    args = parser.parse_args()

    # Create the MVEC and find the uset dof the indices represent.
    mvec = MVEC(args.mvec)
    mvec.find_uset_pos(args.mvec)
    mvec.find_mvec_in_uset(uset=args.uset, set=args.set)

    # Print the list of dof to the screen.
    for m, mvdof in mvec.mvec_dof.items():
        print('\nMerge Vec %s' % m)
        print('i_mvec\tdof')
        for i, d in enumerate(mvdof):
            print('%s\t%s' % (mvec.u_pos[m][i], d))


class MVEC:
    """Class representing a merge vector ot4 file."""

    def __init__(self, name):
        """Method to initialize the MVEC object."""
        self.name = name
        self.u_pos = {}
        self.mvec_dof = {}
        self.uset = []
        self.set_size = 0

    def find_uset_pos(self, mvecfile):
        """Method to read in the merge vec ot4."""

        # Open the merge vec and read.
        with open(mvecfile) as f:
            i = 0
            for line in f:
                if line.__len__() > 25:
                    if line[31:36] == '1PNAM':
                        i += 1
                        if i not in self.u_pos.keys():
                            self.u_pos[i] = []
                            self.mvec_dof[i] = []
                if line[15:24] == '1       1':
                    self.u_pos[i].append(int(line[0:8]))
            for j in range(1, i + 1):
                self.u_pos[j] = sorted(set(self.u_pos[j]))
                del self.u_pos[j][-1]

    def read_mvec_dof(self, **kwargs):
        """Method to read the merge vec dof and determine their index in the uset table."""
        if 'mvec_dof' not in kwargs.keys():
            raise Exception('!!! You must supply a merge vec dof list !!!')
        mvec_dof = kwargs['mvec_dof']
        if 'uset' not in kwargs.keys():
            raise Exception('!!! You must supply a uset file !!!')
        uset = kwargs['uset']

        # Read in the merge vec dof
        with open(mvec_dof) as f:
            for line in f:
                n = int(line.split(sep=',')[0])
                grid = int(line.split(sep=',')[1])
                dof = int(line.split(sep=',')[2])
                if n not in self.mvec_dof.keys():
                    self.mvec_dof[n] = []
                self.mvec_dof[n].append((grid, dof))

        # Create the uset object.
        self.uset = USET(uset)

    def find_u_pos(self, **kwargs):
        """Method to find the index of the mvec dof in the uset table and output merge vec."""
        if 'set' not in kwargs.keys():
            raise Exception('!!! You must specify which set to look for in the uset table.')
        get_set = kwargs['set']

        # For each dof in the merge vec dof look up the index in the uset table for the selected set.
        for i, case in self.mvec_dof.items():
            if i not in self.u_pos.keys():
                self.u_pos[i] = []
            for dof in case:
                if get_set == 'aset':
                    self.u_pos[i].append(self.uset.aset.index(dof) + 1)
                    self.set_size = self.uset.aset.__len__()
                if get_set == 'gset':
                    self.u_pos[i].append(self.uset.gset.index(dof) + 1)
                    self.set_size = self.uset.gset.__len__()
                if get_set == 'oset':
                    self.u_pos[i].append(self.uset.oset.index(dof) + 1)
                    self.set_size = self.uset.oset.__len__()

    def write_merge_vec(self, **kwargs):
        """Method to write out the merge vec ot4."""
        if 'ot4' not in kwargs.keys():
            raise Exception('!!! You must supply an ot4 outfile for the merge vec.')
        ot4 = kwargs['ot4']

        # Open and write out the merge vec ot4.
        with open(ot4, 'w') as f:
            for i, case in self.u_pos.items():
                f.write('%8d       1       2       1PNAM\n' % self.set_size)
                for idof in case:
                    # Determine the index of the dof in the uset table.
                    f.write('%8d       1       1\n' % idof)
                    f.write(' 0.100000000E+01\n')
            f.write('%8d       1       1\n' % (self.set_size + 1))
            f.write(' 0.100000000E+01\n')

    def find_mvec_in_uset(self, **kwargs):
        """Method to find the merge vec dof in the uset f06 table."""
        if 'uset' not in kwargs.keys():
            raise Exception('!!! USET table f06 not specified !!!')
        uset = kwargs['uset']
        if self.u_pos is {}:
            raise Exception('!!! Merge vec object has not been created !!!')
        if 'set' not in kwargs.keys():
            raise Exception('!!! Set must be defined (oset, aset, gset) !!!')
        get_set = kwargs['set']

        # Create the uset object.
        self.uset = USET(uset)

        # For each merge vec index find the associated dof in the uset table.
        for m, upos in self.u_pos.items():
            for d in upos:
                if get_set == 'aset':
                    self.mvec_dof[m].append(self.uset.aset[d - 1])
                elif get_set == 'oset':
                    self.mvec_dof[m].append(self.uset.oset[d - 1])
                elif get_set == 'gset':
                    self.mvec_dof[m].append(self.uset.gset[d - 1])
                else:
                    raise Exception('!!! Unrecognized set: %s !!!' % get_set)


if __name__ == '__main__':

    # If only 'test' is supplied
    if sys.argv.__len__() == 2 and sys.argv[1] == 'test1':
        # Unit Test #1: s3cvvec
        mymvec = MVEC('s3cvvec')
        mymvec.find_uset_pos('merge_vecs/s3cvvec.ot4')
        mymvec.find_mvec_in_uset(uset='uset/s3_uset.f06', set='oset')
        outfile = "test/merge_vec/test1/test1_out.txt"
        json.dump(mymvec.u_pos, open(outfile, 'w'), indent=4, sort_keys=True)
        json.dump(mymvec.mvec_dof, open(outfile, 'a'), indent=4, sort_keys=True)
        json.dump(mymvec.set_size, open(outfile, 'a'), indent=4, sort_keys=True)
        json.dump(mymvec.name, open(outfile, 'a'), indent=4, sort_keys=True)

    # Unit Test #2: merge_vec lookup_mvec uset/s3_uset.f06 merge_vecs/s3cvvec.ot4 oset
    #   >test/merge_vec/test2/test2_out.txt

    elif sys.argv.__len__() == 2 and sys.argv[1] == 'test3':
        # Unit Test #3: p3mrgvec_noceta
        mymvec = MVEC('p3mrgvec_noceta')
        mymvec.find_uset_pos('merge_vecs/p3mrgvec_noceta.ot4')
        mymvec.find_mvec_in_uset(uset='uset/p1_uset.f06', set='gset')
        outfile = "test/merge_vec/test3/test3_out.txt"
        json.dump(mymvec.u_pos, open(outfile, 'w'), indent=4, sort_keys=True)
        json.dump(mymvec.mvec_dof, open(outfile, 'a'), indent=4, sort_keys=True)
        json.dump(mymvec.set_size, open(outfile, 'a'), indent=4, sort_keys=True)
        json.dump(mymvec.name, open(outfile, 'a'), indent=4, sort_keys=True)

    # Unit Test #4: merge_vec lookup_mvec uset/p1_uset.f06 merge_vecs/p3mrgvec_noceta.ot4 gset
    #   >test/merge_vec/test4/test4_out.txt

    elif sys.argv.__len__() == 2 and sys.argv[1] == 'test5':
        # Unit Test #5: p3cvvec
        mymvec = MVEC('p3cvvec')
        mymvec.read_mvec_dof(uset='uset/p3red_0_pas_no_dla.f06', mvec_dof='merge_vecs/p3cvvec_dofs.txt')
        mymvec.find_u_pos(set='oset')
        mymvec.write_merge_vec(ot4='test/merge_vec/test5/p3cvvec_pas_no_dla.ot4')
        mytest = MVEC('p3cvvec_test')
        mytest.find_uset_pos('merge_vecs/p3cvvec_pas_no_dla.ot4')
        mytest.find_mvec_in_uset(uset='uset/p3red_0_pas_no_dla.f06', set='oset')
        outfile = "test/merge_vec/test5/test5_out.txt"
        json.dump(mymvec.mvec_dof, open(outfile, 'w'), indent=4, sort_keys=True)
        json.dump(mymvec.u_pos, open(outfile, 'a'), indent=4, sort_keys=True)
        json.dump(mymvec.set_size, open(outfile, 'a'), indent=4, sort_keys=True)
        json.dump(mymvec.name, open(outfile, 'a'), indent=4, sort_keys=True)
        json.dump(mytest.mvec_dof, open(outfile, 'a'), indent=4, sort_keys=True)
        json.dump(mytest.u_pos, open(outfile, 'a'), indent=4, sort_keys=True)
        json.dump(mytest.set_size, open(outfile, 'a'), indent=4, sort_keys=True)
        json.dump(mytest.name, open(outfile, 'a'), indent=4, sort_keys=True)

    # Unit Test #6: merge_vec make_merge_vec merge_vecs/p3cvvec_dofs.txt uset/p3red_0_pas_no_dla.f06
    #                         oset test/merge_vec/test6/p3cvvec_pas_no_dla.ot4

    elif sys.argv.__len__() > 2 and sys.argv[1] == 'lookup_mvec':
        lookup_mvec()
    elif sys.argv.__len__() > 2 and sys.argv[1] == 'make_merge_vec':
        make_merge_vec()
    else:
        print('usage: merge_vec <function>\n')
        print('\tfunctions:\n')
        print('\t\tlookup_mvec <uset> <mvec> <set>')
        print('\t\tmake_merge_vec <mvec_dofs> <uset> <set> <ot4 output>')
