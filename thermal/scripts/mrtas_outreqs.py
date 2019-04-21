#!/ots/sw/osstoolkit/15.4/sles12-x86_64/bin/python3.6

from PyLnD.thermal.ot4 import OT4
import argparse
import os
import numpy as np


def write_float(out_float, outfile, opers_out):
    """Function to write out the float txt files"""

    # Make the dir structure, open and write
    os.makedirs(os.path.dirname(outfile), exist_ok=True)
    with open(outfile, 'w') as o:
        for oper_out in opers_out:
            o.write('{0}\n'.format(oper_out))
            for j in range(0, out_float[oper_out].shape[1]):
                o.write((24*' ') + (5*'   {:8.5f}').format(
                        out_float[oper_out][0, j], out_float[oper_out][1, j],
                        out_float[oper_out][2, j], out_float[oper_out][3, j], out_float[oper_out][4, j]) +
                        '\n')


def write_loads(out_load, outfile, opers_out, elements):
    """Function to write out the loads txt files"""

    # Make the dir structure, open and write
    os.makedirs(os.path.dirname(outfile), exist_ok=True)
    with open(outfile, 'w') as o:
        o.write((2*'{:16s}').format('oper', 'step') +
                (4*'{:8d}').format(elements[0], elements[1], elements[2], elements[3]) + '\n')
        for oper_out in opers_out:
            for j in range(0, out_load[oper_out].shape[1]):
                o.write((2*'{:16s}').format(oper_out, str(j + 1)) +
                        (4*'{:8.0f}').format(out_load[oper_out][0, j], out_load[oper_out][1, j],
                                             out_load[oper_out][2, j], out_load[oper_out][3, j]) + '\n')


if __name__ == '__main__':

    # Get the command line arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument("-ot4files", help="List of ot4 files", nargs=1)
    parser.add_argument("-operlist", help="List of opers", nargs=1)
    parser.add_argument("-bytype", help="alpha oper irregular", nargs=1)
    args = parser.parse_args()

    # Echo inputs
    print('Inputs:\n\tot4files: {0}'.format(args.ot4files[0]))
    print('\toperlist: {0}'.format(args.operlist[0]))
    print('\tbytype: {0}\n'.format(args.bytype[0]))

    # Read in the oper list
    with open(args.operlist[0], 'r') as f:
        opers = f.read().splitlines()

    # Read in the ot4files
    with open(args.ot4files[0], 'r') as f:
        ot4files = f.read().splitlines()

    # Create ot4 objects and add to the list.
    ot4_list = []
    for ot4file in ot4files:
        ot4_list.append(OT4(ot4file))

    # Determine the number of time steps are available.
    num_time_steps = ot4_list[0].ot4[list(ot4_list[0].ot4.keys())[0]].shape[1]

    # For each oper determine the FLOAT calculation
    float_4_5 = {}
    float_5_6 = {}
    fax45 = {}
    fax56 = {}
    for i, oper in enumerate(opers):

        # MRTAS 45 FLOAT
        dsp54_index = np.array([8, 14, 15, 20, 21]) - 1
        dp40_index = np.array([4, 8, 9, 13, 14]) - 1
        float_4_5[oper] = ot4_list[i].ot4['DSP54'][dsp54_index, :] - ot4_list[i].ot4['DP4O'][dp40_index, :]

        # RTAS 56 FLOAT
        dsp56_index = np.array([8, 9, 14, 20, 21]) - 1
        dp60_index = np.array([4, 5, 9, 13, 14]) - 1
        float_5_6[oper] = ot4_list[i].ot4['DSP56'][dsp56_index, :] - ot4_list[i].ot4['DP6O'][dp60_index, :]

        # MRTAS FAX45 LOADS
        fp4x_index = np.array([1, 4, 6, 7]) - 1
        fax45[oper] = ot4_list[i].ot4['FP4X'][fp4x_index, :]

        # RTAS FAX56 LOADS
        fp6x_index = np.array([1, 4, 5, 7]) - 1
        fax56[oper] = ot4_list[i].ot4['FP6X'][fp6x_index, :]

    # Write out each float type
    write_float(float_4_5, 'mrtas_45/FLOAT_4_5.TXT', opers)
    write_float(float_5_6, 'rtas_56/FLOAT_5_6.TXT', opers)

    # Write out each axial load
    write_loads(fax45, 'mrtas_45/FAX45.TXT', opers, [1857, 1858, 1859, 1860])
    write_loads(fax56, 'rtas_56/FAX56.TXT', opers, [1410, 1412, 1414, 1416])

    # Echo outputs
    print('Outputs:\n\tfloats:\n\t\t{0}\n\t\t{1}'.format('mrtas_45/FLOAT_4_5.TXT', 'rtas_56/FLOAT_5_6.TXT'))
    print('\tloads:\n\t\t{0}\n\t\t{1}'.format('mrtas_45/FAX45.TXT', 'rtas_56/FAX56.TXT'))
