#!/ots/sw/osstoolkit/15.4/sles12-x86_64/bin/python3.6

import argparse
from PyLnD.thermal.inc import INCSet
import numpy as np

# Get the command line inputs
parser = argparse.ArgumentParser()
parser.add_argument("element", help="element: p1, s1, s0, ect.")
parser.add_argument("inc_tarfile", help='tar file containing inc to max-min')
parser.add_argument("bytype", help='byalpha or byoper')
parser.add_argument("request", help='what do you want?  Ex: byelement, byinc')
parser.add_argument("-excluded", help='elements no-ot to be considered in the max-mins')
parser.add_argument("-operlist", help='oper list for the incset')

# Set the arguments
args = parser.parse_args()
element = args.element
inc_tarfile = args.inc_tarfile
bytype = args.bytype
request = args.request
print('Inputs')
print('\telement: {0}'.format(element))
print('\tinc_tar_file: {0}'.format(inc_tarfile))
print('\tbytype: {0}'.format(bytype))
print('\trequest: {0}'.format(request))

# If the operlist is provided, get the name of the file
operlist = None
if args.operlist is not None:
    operlist = args.operlist
    print('\toperlist: {0}'.format(operlist))

# If the exclusion list is provided, read the elements.
excluded = []
if args.excluded is not None:
    raise Exception('This needs to be added!')
    # print('excluding elements from {0}'.format(args.excluded))
    # excluded = open(args.excluded, 'r').read().split('\n')
    # excluded = list(filter(None, excluded))

# Make the incset object based on the component model element types
incset = None
if element == 'p6ls' or element == 's6ls':
    incset = INCSet(tarzip=inc_tarfile, bytype=bytype, operlist=operlist, etype='beams')

# Implement the requested max/min format.
print('... retrieving request: {0}'.format(request))
if request == 'byelement':
    output_list = ['element max_oper max_ts max_temp min_oper min_ts min_temp\n']
    # For each etype, find the max/min temperature per element
    for elem in incset.elements:
        data = incset.inc_set[incset.elements == elem, :, :]
        max_temperature = np.amax(data)
        i_max = np.unravel_index(np.argmax(data, axis=None), data.shape)
        max_oper = incset.opers[i_max[1]]
        max_time_step = incset.time_steps[i_max[2]]
        min_temperature = np.amin(data)
        i_min = np.unravel_index(np.argmin(data, axis=None), data.shape)
        min_oper = incset.opers[i_min[1]]
        min_time_step = incset.time_steps[i_min[2]]
        output_list.append(
            '{0} {1} {2} {3} {4} {5} {6}\n'.format(elem, max_oper, max_time_step, max_temperature,
                                                   min_oper, min_time_step, min_temperature)
        )
    # Print the results
    outfile = '{0}_maxmin_temps_byelement.txt'.format(element)
    with open(outfile, 'w') as f:
        f.writelines(output_list)
    print('\ncompleted output: {0}'.format(outfile))

elif request == 'byinc':
    raise Exception('Need to add.')
else:
    raise Exception('Unrecognized request type: {0}'.format(request))
