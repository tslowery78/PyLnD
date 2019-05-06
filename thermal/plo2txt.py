import argparse
from PyLnD.thermal.plo import PLO
import numpy as np
import sys
import os


def main():
    # Import arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('node_list', help='List of SINDA nodes for txt output.')
    parser.add_argument('plo_list', help='List of PLO files to extract temperature.')
    parser.add_argument('prefix', help='Output txt file prefix: ex: T1A')
    parser.add_argument('--skip', action='store_true', help='Skip every other temperature in the time history.')
    args = parser.parse_args()
    # Execute function with arguments.
    plo2txt(nodes=args.node_list, plos=args.plo_list, prefix=args.prefix, skip=args.skip)


def plo2txt(**kwargs):
    """Function to create txt file time histories from PLO temperature files."""

    # Obtain keyword arguments.
    node_list = kwargs['nodes']
    plo_list = kwargs['plos']
    prefix = kwargs['prefix']
    skip = kwargs.get('skip', False)

    # Read the list of nodes to output.
    print('...reading %s for requested SINDA nodes...' % node_list)
    with open(node_list) as f:
        nodes = f.readlines()
        nodes = list(map(int, nodes))
        n_nodes = nodes.__len__()
    print('\tnumber of nodes: %s' % n_nodes)
    print('...reading %s for the PLO temperature data...' % plo_list)
    with open(plo_list) as f:
        plo_files = f.readlines()
        n_plos = plo_files.__len__()
    print('\tnumber of PLO files: %s' % n_plos)

    # Make a PLO object out of each PLO in the plo_list and determine the time history of each requested node.
    nodal_temps = {}
    print('...extracting the nodal temperatures...')
    import time
    start = time.time()
    for i, pf in enumerate(plo_files):
        plo = PLO(pf.rstrip())
        for node in nodes:
            if node not in nodal_temps.keys():
                nodal_temps[node] = np.zeros([n_plos, plo.num_time_steps])
            nodal_temps[node][i, :] = np.asarray(plo.node[node])
    end = time.time()
    print(end - start)

    # Write out each nodal temperature to it's own txt file.
    if skip:
        s = 2
    else:
        s = 1
    print('...writing the nodal temperatures to txt files...')
    for node in nodes:
        filename = prefix + '_' + node.__str__() + '.txt'
        print('\t%s' % filename)
        np.savetxt(filename, nodal_temps[node][:, 0:-1:s], fmt='%8.1f')
    print('...process complete...')


if __name__ == '__main__':

    # If only 'debug' is supplied on command line then run locally, else run main().
    if sys.argv.__len__() == 2 and sys.argv[1] == 'debug':
        os.chdir('pva_temps')
        plo2txt(nodes='txtnode.lis', plos='pva1A_plo.lis', prefix='T1A', skip=True)
        os.chdir('../')
    else:
        main()
