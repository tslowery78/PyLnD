#!/ots/sw/osstoolkit/15.4/sles12-x86_64/bin/python3.6

from PyLnD.thermal.f06 import F06
import argparse
import sys

# Get the user input arguments.
parser = argparse.ArgumentParser()
parser.add_argument("-f06files", help="List of f06 files", nargs=1)
parser.add_argument("-operlist", help="List of opers", nargs=1)
parser.add_argument("-bytype", help="alpha oper irregular", nargs=1)
parser.add_argument("-order", help="output by alpha or by oper", nargs=1)
args = parser.parse_args()

# Display the help if no arguments given.
if len(sys.argv) == 1:
    parser.print_help(sys.stderr)
    sys.exit(1)

# Parse the bytype option.
bytype = ''
if 'alpha' in args.bytype[0]:
    bytype = 'alpha'
elif 'oper' in args.bytype[0]:
    bytype = 'oper'
elif 'irr' in args.bytype[0]:
    bytype = 'irregular'
print('The f06 files are expected to be ordered by {0}'.format(bytype))

# Read in the operlist
with open(args.operlist[0], 'r') as f:
    opers = f.read().splitlines()

# Read in the f06files
with open(args.f06files[0], 'r') as f:
    f06files = f.read().splitlines()

# Create f06 objects and add to the list.
f06_list = []
print('Reading all the f06 files.')
for f06file in f06files:
    f06_list.append(F06(file=f06file, outreqs=['celas2_forces']))

# Determine the number of time steps
first_element = list(f06_list[0].celas2_forces.keys())[0]
num_time_steps = f06_list[0].celas2_forces[first_element].shape[0]
time_steps = range(1, num_time_steps + 1)

# If by alph make the time steps the sarj angles
if bytype == 'alpha':
    time_steps = range(0, 360, 30)

# Parse the output order, default to by alpha.
outside_loop = opers
inside_loop = time_steps
o_form = 'oper'
i_form = 'tstep'
if 'oper' in args.order[0]:
    outside_loop = time_steps
    inside_loop = opers
    o_form = 'tstep'
    i_form = 'oper'
    print('The output order will be alpha then oper.\n')
else:
    print('The output order will be oper then alpha.\n')

# Print out the TRUNDLES.TXT file.
trundle_celas = [
    (625501, 625513),
    (625502, 625514),
    (625503, 625515),
    (625504, 625516),
    (625505, 625517),
    (625506, 625518),
    (625507, 625519),
    (625508, 625520),
    (625509, 625521),
    (625510, 625522),
    (625511, 625523),
    (625512, 625524)
]
if f06_list[0].celas2_elements:
    print('Creating TRUNDLES.TXT\n')
    with open('TRUNDLES.TXT', 'w+') as f:
        f.write('          Ele.ID   Ele.ID    Fshear    Faxial  Fshear-Faxial\n\n')
        for o, o_item in enumerate(outside_loop):
            o_item_str = str(o_item)
            f.write('{0} = {1:8s}\n'.format(o_form, o_item_str))
            for j, j_item in enumerate(inside_loop):
                j_item_str = str(j_item)
                if 'oper' in args.order[0]:
                    c = o
                    d = j
                else:
                    c = j
                    d = o
                f.write('\t{0} = {1:8s}\n'.format(i_form, j_item_str))
                F_shear = 0
                F_axial = 0
                for e, trundle in enumerate(trundle_celas):
                    element_1 = trundle[0]
                    element_2 = trundle[1]
                    if bytype == 'alpha':
                        F_shear = f06_list[c].celas2_forces[element_1][d]
                        F_axial = f06_list[c].celas2_forces[element_2][d]
                    elif bytype == 'irregular':
                        F_shear = f06_list[d * 18 + c].celas2_forces[element_1][0]
                        F_axial = f06_list[d * 18 + c].celas2_forces[element_2][0]
                    if bytype == 'oper':
                        F_shear = f06_list[d].celas2_forces[element_1][c]
                        F_axial = f06_list[d].celas2_forces[element_2][c]
                    dF = F_shear - F_axial
                    f.write((3*'{:8d}').format(e + 1, element_1, element_2) +
                            (3*'{:10.1f}').format(F_shear, F_axial, dF) + '\n')
