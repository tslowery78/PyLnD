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
    f06_list.append(F06(file=f06file, outreqs=['cbar_forces', 'cbeam_forces',
                                               'celas2_forces']))

# Determine the number of time steps
if bytype == 'alpha':
    num_time_steps = len(f06_list)
elif bytype == 'oper':
    num_time_steps = f06_list[0].num_subcases
else:
    raise Exception('No time step for this type {0}'.format(bytype))
time_steps = range(1, num_time_steps + 1)

# Parse the output order, default to by alpha.
outside_loop = opers
inside_loop = time_steps
if 'oper' in args.order[0]:
    outside_loop = time_steps
    inside_loop = opers
    print('The output order will be alpha then oper.\n')
else:
    print('The output order will be oper then alpha.\n')

# Print out the CBAR_FORCES.TXT file.
if f06_list[0].bar_elements:
    print('Creating CBAR_FORCES.TXT\n')
    n_elems = len(f06_list[0].bar_elements)
    with open('CBAR_FORCES.TXT', 'w+') as f:
        f.write('\n              Ele.ID    A-M1     A-M2     B-M1     B-M2      SH1      SH2       FX       MT\n\n')
        for o, o_item in enumerate(outside_loop):
            for e in range(0, n_elems):
                for j, j_item in enumerate(inside_loop):
                    o_item_str = str(o_item)
                    j_item_str = str(j_item)
                    if 'oper' in args.order[0]:
                        c = o
                        d = j
                        col1 = j_item_str
                        col2 = o_item_str
                    else:
                        c = j
                        d = o
                        col1 = o_item_str
                        col2 = j_item_str
                    if bytype == 'alpha':
                        element = f06_list[c].bar_elements[e]
                        f.write('{0:10s} {1:4s}'.format(col1, col2) +
                                '{0:7d}'.format(f06_list[c].bar_elements[e]) +
                                (8*'{:9.0f}').format(
                                    f06_list[c].bar_forces[element][d, 0],          # MA1
                                    f06_list[c].bar_forces[element][d, 1],          # MA2
                                    f06_list[c].bar_forces[element][d, 2],          # MB1
                                    f06_list[c].bar_forces[element][d, 3],          # MB2
                                    f06_list[c].bar_forces[element][d, 4],          # SH1
                                    f06_list[c].bar_forces[element][d, 5],          # SH2
                                    f06_list[c].bar_forces[element][d, 6],          # FX
                                    f06_list[c].bar_forces[element][d, 7]) + '\n')  # MT
                    elif bytype == 'irregular':
                        element = f06_list[c].bar_elements[e]
                        f.write('{0:10s} {1:4s}'.format(col1, col2) +
                                '{0:7d}'.format(f06_list[c].bar_elements[e]) +
                                (8*'{:9.0f}').format(
                                    f06_list[d * 18 + c].bar_forces[element][0, 0],  # MA1
                                    f06_list[d * 18 + c].bar_forces[element][0, 1],  # MA2
                                    f06_list[d * 18 + c].bar_forces[element][0, 2],  # MB1
                                    f06_list[d * 18 + c].bar_forces[element][0, 3],  # MB2
                                    f06_list[d * 18 + c].bar_forces[element][0, 4],  # SH1
                                    f06_list[d * 18 + c].bar_forces[element][0, 5],  # SH2
                                    f06_list[d * 18 + c].bar_forces[element][0, 6],  # FX
                                    f06_list[d * 18 + c].bar_forces[element][0, 7])  # MT
                                + '\n')
                    if bytype == 'oper':
                        element = f06_list[d].bar_elements[e]
                        f.write('{0:10s} {1:4s}'.format(col1, col2) +
                                '{0:7d}'.format(f06_list[d].bar_elements[e]) +
                                (8*'{:9.0f}').format(
                                    f06_list[d].bar_forces[element][c, 0],          # MA1
                                    f06_list[d].bar_forces[element][c, 1],          # MA2
                                    f06_list[d].bar_forces[element][c, 2],          # MB1
                                    f06_list[d].bar_forces[element][c, 3],          # MB2
                                    f06_list[d].bar_forces[element][c, 4],          # SH1
                                    f06_list[d].bar_forces[element][c, 5],          # SH2
                                    f06_list[d].bar_forces[element][c, 6],          # FX
                                    f06_list[d].bar_forces[element][c, 7]) + '\n')  # MT

# Print out the CBEAM_FORCES.TXT file.
if f06_list[0].beam_elements:
    print('Creating CBEAM_FORCES.TXT\n')
    n_elems = len(f06_list[0].beam_elements)
    with open('CBEAM_FORCES.TXT', 'w+') as f:
        f.write('\n              Ele.ID    A-M1     A-M2     B-M1     B-M2      SH1      SH2       FX       MT\n\n')
        for o, o_item in enumerate(outside_loop):
            for e in range(0, n_elems):
                for j, j_item in enumerate(inside_loop):
                    o_item_str = str(o_item)
                    j_item_str = str(j_item)
                    if 'oper' in args.order[0]:
                        c = o
                        d = j
                        col1 = j_item_str
                        col2 = o_item_str
                    else:
                        c = j
                        d = o
                        col1 = o_item_str
                        col2 = j_item_str
                    if bytype == 'alpha':
                        element = f06_list[c].beam_elements[e]
                        f.write('{0:10s} {1:4s}'.format(col1, col2) +
                                '{0:7d}'.format(f06_list[c].beam_elements[e]) +
                                (8*'{:9.0f}').format(
                                    f06_list[c].beam_forces[element][d, 0],          # MA1
                                    f06_list[c].beam_forces[element][d, 1],          # MA2
                                    f06_list[c].beam_forces[element][d, 2],          # MB1
                                    f06_list[c].beam_forces[element][d, 3],          # MB2
                                    f06_list[c].beam_forces[element][d, 4],          # SH1
                                    f06_list[c].beam_forces[element][d, 5],          # SH2
                                    f06_list[c].beam_forces[element][d, 6],          # FX
                                    f06_list[c].beam_forces[element][d, 7]) + '\n')  # MT
                    elif bytype == 'irregular':
                        element = f06_list[c].beam_elements[e]
                        f.write('{0:10s} {1:4s}'.format(col1, col2) +
                                '{0:7d}'.format(f06_list[c].beam_elements[e]) +
                                (8*'{:9.0f}').format(
                                    f06_list[d * 18 + c].beam_forces[element][0, 0],  # MA1
                                    f06_list[d * 18 + c].beam_forces[element][0, 1],  # MA2
                                    f06_list[d * 18 + c].beam_forces[element][0, 2],  # MB1
                                    f06_list[d * 18 + c].beam_forces[element][0, 3],  # MB2
                                    f06_list[d * 18 + c].beam_forces[element][0, 4],  # SH1
                                    f06_list[d * 18 + c].beam_forces[element][0, 5],  # SH2
                                    f06_list[d * 18 + c].beam_forces[element][0, 6],  # FX
                                    f06_list[d * 18 + c].beam_forces[element][0, 7])  # MT
                                + '\n')
                    if bytype == 'oper':
                        element = f06_list[d].beam_elements[e]
                        f.write('{0:10s} {1:4s}'.format(col1, col2) +
                                '{0:7d}'.format(f06_list[d].beam_elements[e]) +
                                (8*'{:9.0f}').format(
                                    f06_list[d].beam_forces[element][c, 0],          # MA1
                                    f06_list[d].beam_forces[element][c, 1],          # MA2
                                    f06_list[d].beam_forces[element][c, 2],          # MB1
                                    f06_list[d].beam_forces[element][c, 3],          # MB2
                                    f06_list[d].beam_forces[element][c, 4],          # SH1
                                    f06_list[d].beam_forces[element][c, 5],          # SH2
                                    f06_list[d].beam_forces[element][c, 6],          # FX
                                    f06_list[d].beam_forces[element][c, 7]) + '\n')  # MT

# Print out the CELAS2_FORCES.TXT file.
if f06_list[0].celas2_elements:
    print('Creating CELAS2_FORCES.TXT\n')
    n_elems = len(f06_list[0].celas2_elements)
    with open('CELAS2_FORCES.TXT', 'w+') as f:
        f.write('\n              Ele.ID    FORCE\n\n')
        for o, o_item in enumerate(outside_loop):
            for e in range(0, n_elems):
                for j, j_item in enumerate(inside_loop):
                    o_item_str = str(o_item)
                    j_item_str = str(j_item)
                    if 'oper' in args.order[0]:
                        c = o
                        d = j
                        col1 = j_item_str
                        col2 = o_item_str
                    else:
                        c = j
                        d = o
                        col1 = o_item_str
                        col2 = j_item_str
                    if bytype == 'alpha':
                        element = f06_list[c].celas2_elements[e]
                        f.write('{0:10s} {1:4s}'.format(col1, col2) +
                                '{0:7d}'.format(f06_list[c].celas2_elements[e]) +
                                '{0:9.4f}'.format(
                                f06_list[c].celas2_forces[element][0]) + '\n')  # FORCE
                    elif bytype == 'irregular':
                        element = f06_list[c].celas2_elements[e]
                        f.write('{0:10s} {1:4s}'.format(col1, col2) +
                                '{0:7d}'.format(f06_list[c].celas2_elements[e]) +
                                '{0:9.4f}'.format(
                                f06_list[d * 18 + c].celas2_forces[element][0]) + '\n')  # FORCE
                    if bytype == 'oper':
                        element = f06_list[d].celas2_elements[e]
                        f.write('{0:10s} {1:4s}'.format(col1, col2) +
                                '{0:7d}'.format(f06_list[d].celas2_elements[e]) +
                                '{0:9.4f}'.format(
                                f06_list[d].celas2_forces[element][0]) + '\n')  # FORCE

