#!/ots/sw/osstoolkit/15.4/sles12-x86_64/bin/python3.6

import argparse
from PyLnD.thermal.inc import INCSet
from PyLnD.thermal.plo import PLOSet
import numpy as np
import pandas as pd

# Get the command line inputs
parser = argparse.ArgumentParser()
parser.add_argument("ploset_bytype", help='Is ploset byalpha or byoper?')
parser.add_argument("incset_bytype", help='Is incset byalpha or byoper?')
parser.add_argument("ploset", help="tarzip plo.tar.gz file with all AMS PLOs")
parser.add_argument("incset", help='tarzip inc.tar.gz file with all S3 incs')
parser.add_argument("operlist", help='oper list for the incset')
parser.add_argument('ams_nodes', help='List of cas nodes in the ams PLO')
parser.add_argument('s3_elements', help='List of pcas elements in the S3 inc')

# Set the arguments
args = parser.parse_args()
ploset_bytype = args.ploset_bytype
incset_bytype = args.incset_bytype
ploset_name = args.ploset
incset_name = args.incset
operlist = args.operlist
ams_listfile = args.ams_nodes
s3_listfile = args.s3_elements

# Get the AMS nodes and S3 elements
with open(ams_listfile) as f:
    ams_nodes = f.read().splitlines()
    ams_nodes = np.asarray([int(item) for item in ams_nodes])
with open(s3_listfile) as f:
    s3_elements = f.read().splitlines()
    s3_elements = np.asarray([int(item) for item in s3_elements])

# Create the S3 PLOSet and ESP-3 INCSet
ams_ploset = PLOSet(tarzip=ploset_name, bytype=ploset_bytype, operlist=operlist, plosub='SAMS')
s3_incset = INCSet(tarzip=incset_name, bytype=incset_bytype, operlist=operlist, etype='beams')

# Find the temperatures at each node for each side
ams_temps = ams_ploset.plo_set[ams_ploset.nodes == ams_nodes, :, 0::2]
ams_temps = ams_temps[:, :, 0:-1]
s3_temps = np.zeros([len(s3_elements), s3_incset.num_opers, s3_incset.num_time_steps])
for i, element in enumerate(s3_elements):
    s3_temps[i, :, :] = s3_incset.inc_set[s3_incset.elements == element, :, :]

# Find the average s3 temperatures
s3_temps_average = np.average(s3_temps, axis=0)

# Find the delta T between S3 - AMS
delta_T = s3_temps_average - ams_temps

# Save to csv
print('\nwriting s3_pas_to_ams_pcas_dT.csv')
df = pd.DataFrame(delta_T[0, :, :])
df.to_csv('s3_pas_to_ams_pcas_dT.csv', index=False, header=False)
