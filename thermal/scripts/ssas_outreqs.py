#!/ots/sw/osstoolkit/15.4/sles12-x86_64/bin/python3.6

from PyLnD.thermal.ot4 import OT4
import argparse
import numpy as np
import sys

# Get the command line arguments.
parser = argparse.ArgumentParser()
parser.add_argument("-ot4files", help="List of ot4 files", nargs=1)
parser.add_argument("-operlist", help="List of opers", nargs=1)
parser.add_argument("-bytype", help="alpha oper irregular", nargs=1)
args = parser.parse_args()

# Display the help if no arguments given.
if len(sys.argv) == 1:
    parser.print_help(sys.stderr)
    sys.exit(1)

# Parse the bytype option.
bytype = None
if 'alpha' in args.bytype[0]:
    bytype = 'alpha'
elif 'oper' in args.bytype[0]:
    bytype = 'oper'
elif 'irr' in args.bytype[0]:
    bytype = 'irregular'

# Read in the operlist
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
if bytype == 'alpha':
    num_time_steps = len(ot4_list)
elif bytype == 'oper':
    num_time_steps = ot4_list[0].ot4['FS10'].shape[1]
else:
    raise Exception('Need to determine the time steps of this type.')

# Write out each SSAS loads TXT file.
ssas_files = ["S0S1.TXT", "S0P1.TXT", "P1P3.TXT", "S1S3.TXT"]
ssas_grids = [
    [261001, 261002, 261005, 261006],
    [266001, 266002, 266005, 266006],
    [650001, 650002, 650005, 650006],
    [250001, 250002, 250005, 250006]]
ssas_mats = ["FS10", "FP10", "FP30", "FS30"]
for i, ssas_file in enumerate(ssas_files):
    grids = ssas_grids[i]
    matrix = ssas_mats[i]
    print("Creating {0} from matrix {1}".format(ssas_file, matrix))
    with open(ssas_file, 'w+') as f:
        for o, oper in enumerate(opers):
            f.write(oper + '\n')
            f.write("   GRID         FT        FY        FP        MT        MY        MP\n")
            for g, grid in enumerate(grids):
                if bytype == 'alpha':
                    for j in range(0, num_time_steps):
                        ft = ot4_list[j].ot4[matrix][0 + 5*g, o]
                        fy = ot4_list[j].ot4[matrix][1 + 5*g, o]
                        if g < len(grids) - 1:
                            fp = 0.0
                            mt = ot4_list[j].ot4[matrix][2 + 5*g, o]
                            my = ot4_list[j].ot4[matrix][3 + 5*g, o]
                            mp = ot4_list[j].ot4[matrix][4 + 5*g, o]
                        else:
                            fp = ot4_list[j].ot4[matrix][2 + 5*g, o]
                            mt = ot4_list[j].ot4[matrix][3 + 5*g, o]
                            my = ot4_list[j].ot4[matrix][4 + 5*g, o]
                            mp = ot4_list[j].ot4[matrix][5 + 5*g, o]
                        if j == 0:
                            leader = grid.__str__()
                        else:
                            leader = ''
                        f.write("{0:8s}".format(leader) + (6*"  {:9.1f}").format(
                            ft, fy, fp, mt, my, mp) + "\n")
                elif bytype == 'irregular':
                    for j in range(0, num_time_steps):
                        ft = ot4_list[j + o * 18].ot4[matrix][0 + 5*g, 0]
                        fy = ot4_list[j + o * 18].ot4[matrix][1 + 5*g, 0]
                        if g < len(grids) - 1:
                            fp = 0.0
                            mt = ot4_list[j + o * 18].ot4[matrix][2 + 5*g, 0]
                            my = ot4_list[j + o * 18].ot4[matrix][3 + 5*g, 0]
                            mp = ot4_list[j + o * 18].ot4[matrix][4 + 5*g, 0]
                        else:
                            fp = ot4_list[j + o * 18].ot4[matrix][2 + 5*g, 0]
                            mt = ot4_list[j + o * 18].ot4[matrix][3 + 5*g, 0]
                            my = ot4_list[j + o * 18].ot4[matrix][4 + 5*g, 0]
                            mp = ot4_list[j + o * 18].ot4[matrix][5 + 5*g, 0]
                        if j == 0:
                            leader = grid.__str__()
                        else:
                            leader = ''
                        f.write("{0:8s}".format(leader) + (6*"  {:9.1f}").format(
                            ft, fy, fp, mt, my, mp) + "\n")
                elif bytype == 'oper':
                    for j in range(0, num_time_steps):
                        ft = ot4_list[o].ot4[matrix][0 + 5 * g, j]
                        fy = ot4_list[o].ot4[matrix][1 + 5 * g, j]
                        if g < len(grids) - 1:
                            fp = 0.0
                            mt = ot4_list[o].ot4[matrix][2 + 5 * g, j]
                            my = ot4_list[o].ot4[matrix][3 + 5 * g, j]
                            mp = ot4_list[o].ot4[matrix][4 + 5 * g, j]
                        else:
                            fp = ot4_list[o].ot4[matrix][2 + 5 * g, j]
                            mt = ot4_list[o].ot4[matrix][3 + 5 * g, j]
                            my = ot4_list[o].ot4[matrix][4 + 5 * g, j]
                            mp = ot4_list[o].ot4[matrix][5 + 5 * g, j]
                        if j == 0:
                            leader = grid.__str__()
                        else:
                            leader = ''
                        f.write("{0:8s}".format(leader) + (6 * "  {:9.1f}").format(
                            ft, fy, fp, mt, my, mp) + "\n")

# Find the absolute max across each time step for each oper.
mxmn_files = ['MXMNS0S1.TXT', 'MXMNS0P1.TXT', 'MXMNP1P3.TXT', 'MXMNS1S3.TXT']
for i, mxmn_file in enumerate(mxmn_files):
    matrix = ssas_mats[i]
    print("Creating absolute max file {0} from matrix {1}".format(mxmn_file, matrix))
    with open(mxmn_file, 'w+') as f:
        f.write('                             LONG     LONG      MT      MT       MT6\n')
        f.write('                             SHEAR    AXIAL    SHEAR   AXIAL     SHEAR\n\n')
        for o, oper in enumerate(opers):
            if bytype == 'alpha':
                # LONG SHEAR
                g1_ft = np.abs([x.ot4[matrix][0, o] for x in ot4_list]).max()
                g2_ft = np.abs([x.ot4[matrix][5, o] for x in ot4_list]).max()
                axlngt = max(g1_ft, g2_ft)
                # LONG AXIAL
                g1_fy = np.abs([x.ot4[matrix][1, o] for x in ot4_list]).max()
                g2_fy = np.abs([x.ot4[matrix][6, o] for x in ot4_list]).max()
                axlngy = max(g1_fy, g2_fy)
                # MT SHEAR
                g3_ft = np.abs([x.ot4[matrix][10, o] for x in ot4_list]).max()
                g4_ft = np.abs([x.ot4[matrix][15, o] for x in ot4_list]).max()
                axmtt = max(g3_ft, g4_ft)
                # MT AXIAL
                g3_fy = np.abs([x.ot4[matrix][11, o] for x in ot4_list]).max()
                g4_fy = np.abs([x.ot4[matrix][16, o] for x in ot4_list]).max()
                axmty = max(g3_fy, g4_fy)
                # MT6 SHEAR
                axmt6p = np.abs([x.ot4[matrix][17, o] for x in ot4_list]).max()

                f.write(' {0:24s}'.format(oper) + (5*"{:9.1f}").format(
                    axlngt, axlngy, axmtt, axmty, axmt6p
                ) + '\n')
            elif bytype == 'irregular':
                c = o * 18
                # LONG SHEAR
                g1_ft = np.abs([x.ot4[matrix][0, 0] for x in ot4_list[c:c + 18]]).max()
                g2_ft = np.abs([x.ot4[matrix][5, 0] for x in ot4_list[c:c + 18]]).max()
                axlngt = max(g1_ft, g2_ft)
                # LONG AXIAL
                g1_fy = np.abs([x.ot4[matrix][1, 0] for x in ot4_list[c:c + 18]]).max()
                g2_fy = np.abs([x.ot4[matrix][6, 0] for x in ot4_list[c:c + 18]]).max()
                axlngy = max(g1_fy, g2_fy)
                # MT SHEAR
                g3_ft = np.abs([x.ot4[matrix][10, 0] for x in ot4_list[c:c + 18]]).max()
                g4_ft = np.abs([x.ot4[matrix][15, 0] for x in ot4_list[c:c + 18]]).max()
                axmtt = max(g3_ft, g4_ft)
                # MT AXIAL
                g3_fy = np.abs([x.ot4[matrix][11, 0] for x in ot4_list[c:c + 18]]).max()
                g4_fy = np.abs([x.ot4[matrix][16, 0] for x in ot4_list[c:c + 18]]).max()
                axmty = max(g3_fy, g4_fy)
                # MT6 SHEAR
                axmt6p = np.abs([x.ot4[matrix][17, 0] for x in ot4_list[c:c + 18]]).max()

                f.write(' {0:24s}'.format(oper) + (5*"{:9.1f}").format(
                    axlngt, axlngy, axmtt, axmty, axmt6p
                ) + '\n')
            elif bytype == 'oper':
                # leaving off here! 8-8-18
                # LONG SHEAR
                g1_ft = np.abs(ot4_list[o].ot4[matrix][0, :]).max()
                g2_ft = np.abs(ot4_list[o].ot4[matrix][5, :]).max()
                axlngt = max(g1_ft, g2_ft)
                # LONG AXIAL
                g1_fy = np.abs(ot4_list[o].ot4[matrix][1, :]).max()
                g2_fy = np.abs(ot4_list[o].ot4[matrix][6, :]).max()
                axlngy = max(g1_fy, g2_fy)
                # MT SHEAR
                g3_ft = np.abs(ot4_list[o].ot4[matrix][10, :]).max()
                g4_ft = np.abs(ot4_list[o].ot4[matrix][15, :]).max()
                axmtt = max(g3_ft, g4_ft)
                # MT AXIAL
                g3_fy = np.abs(ot4_list[o].ot4[matrix][11, :]).max()
                g4_fy = np.abs(ot4_list[o].ot4[matrix][16, :]).max()
                axmty = max(g3_fy, g4_fy)
                # MT6 SHEAR
                axmt6p = np.abs(ot4_list[o].ot4[matrix][17, :]).max()

                f.write(' {0:24s}'.format(oper) + (5*"{:9.1f}").format(
                    axlngt, axlngy, axmtt, axmty, axmt6p
                ) + '\n')

# Find the SSAS FLOAT time history.
float_files = ['FLOATS0S1.TXT', 'FLOATS0P1.TXT', 'FLOATP1P3.TXT', 'FLOATS1S3.TXT']
float_mats = [('DS10', 'DSPS'), ('DP10', 'DPPS'), ('DP30', 'DP10'), ('DS30', 'DS10')]
mat_locs = [[(72, 2), (73, 8), (74, 14)],
            [(0, 2), (1, 8), (2, 14)],
            [(12, 5), (13, 11), (14, 17)],
            [(0, 2), (1, 8), (2, 14)]
            ]
for i, float_file in enumerate(float_files):
    matrix1 = float_mats[i][0]
    matrix2 = float_mats[i][1]
    locs = mat_locs[i]
    print("Creating SSAS FLOAT file {0} from matrix {1} - {2}"
          .format(float_file, matrix1, matrix2))
    with open(float_file, 'w+') as f:
        for o, oper in enumerate(opers):
            f.write('{0}\n'.format(oper))
            if bytype == 'alpha':
                for j in range(0, num_time_steps):
                    del11 = ot4_list[j].ot4[matrix1][locs[0][0], o]
                    del12 = ot4_list[j].ot4[matrix2][locs[0][1], o]
                    del1 = del11 - del12
                    del21 = ot4_list[j].ot4[matrix1][locs[1][0], o]
                    del22 = ot4_list[j].ot4[matrix2][locs[1][1], o]
                    del2 = del21 - del22
                    del31 = ot4_list[j].ot4[matrix1][locs[2][0], o]
                    del32 = ot4_list[j].ot4[matrix2][locs[2][1], o]
                    del3 = del31 - del32
                    f.write((9*" {:10.5f}").format(
                        del11, del12, del1,
                        del21, del22, del2,
                        del31, del32, del3,
                    ) + '\n')
            if bytype == 'irregular':
                for j in range(o * 18, o * 18 + 18):
                    del11 = ot4_list[j].ot4[matrix1][locs[0][0], 0]
                    del12 = ot4_list[j].ot4[matrix2][locs[0][1], 0]
                    del1 = del11 - del12
                    del21 = ot4_list[j].ot4[matrix1][locs[1][0], 0]
                    del22 = ot4_list[j].ot4[matrix2][locs[1][1], 0]
                    del2 = del21 - del22
                    del31 = ot4_list[j].ot4[matrix1][locs[2][0], 0]
                    del32 = ot4_list[j].ot4[matrix2][locs[2][1], 0]
                    del3 = del31 - del32
                    f.write((9*" {:10.5f}").format(
                        del11, del12, del1,
                        del21, del22, del2,
                        del31, del32, del3,
                    ) + '\n')
            elif bytype == 'oper':
                for j in range(0, num_time_steps):
                    del11 = ot4_list[o].ot4[matrix1][locs[0][0], j]
                    del12 = ot4_list[o].ot4[matrix2][locs[0][1], j]
                    del1 = del11 - del12
                    del21 = ot4_list[o].ot4[matrix1][locs[1][0], j]
                    del22 = ot4_list[o].ot4[matrix2][locs[1][1], j]
                    del2 = del21 - del22
                    del31 = ot4_list[o].ot4[matrix1][locs[2][0], j]
                    del32 = ot4_list[o].ot4[matrix2][locs[2][1], j]
                    del3 = del31 - del32
                    f.write((9*" {:10.5f}").format(
                        del11, del12, del1,
                        del21, del22, del2,
                        del31, del32, del3,
                    ) + '\n')

