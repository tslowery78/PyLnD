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
parser.add_argument("ploset", help="tarzip plo.tar.gz file with all S3 PLOs")
parser.add_argument("incset", help='tarzip inc.tar.gz file with all ESP-3 incs')
parser.add_argument("operlist", help='oper list for the incset')
parser.add_argument('esp3_nodes', help='List of pcas nodes in the esp3 fem')
parser.add_argument('s3_nodes', help='List of cas nodes in the s3 PLO')

# Set the arguments
args = parser.parse_args()
ploset_bytype = args.ploset_bytype
incset_bytype = args.incset_bytype
ploset_name = args.ploset
incset_name = args.incset
operlist = args.operlist
esp3_listfile = args.esp3_nodes
s3_listfile = args.s3_nodes

# Get the ESP-3 and S3 nodes
with open(esp3_listfile) as f:
    esp3_nodes = f.read().splitlines()
    esp3_nodes = np.asarray([int(item) for item in esp3_nodes])
with open(s3_listfile) as f:
    s3_nodes = f.read().splitlines()
    s3_nodes = np.asarray([int(item) for item in s3_nodes])

# Create the S3 PLOSet and ESP-3 INCSet
s3_ploset = PLOSet(tarzip=ploset_name, bytype=ploset_bytype, operlist=operlist, plosub='PAS3')
esp3_incset = INCSet(tarzip=incset_name, bytype=incset_bytype, operlist=operlist, nalphas='all')

# Find the temperatures at each node for each side
s3_temps = s3_ploset.plo_set[s3_ploset.nodes == s3_nodes, :, :]
esp3_temps = np.zeros([len(esp3_nodes), esp3_incset.num_opers, esp3_incset.num_time_steps])
for i, node in enumerate(esp3_nodes):
    esp3_temps[i, :, :] = esp3_incset.inc_set[esp3_incset.elements == node, :, :]

# Find the max, mins
s3_min_temp = s3_temps.min(axis=2)
s3_max_temp = s3_temps.max(axis=2)
esp3_min_temps = esp3_temps.min(axis=2)
esp3_max_temps = esp3_temps.max(axis=2)

# Find the delta T
max_min_deltaT = s3_min_temp - esp3_min_temps.max(axis=0)
min_min_deltaT = s3_min_temp - esp3_min_temps.min(axis=0)
max_max_deltaT = s3_max_temp - esp3_max_temps.max(axis=0)
min_max_deltaT = s3_max_temp - esp3_max_temps.min(axis=0)
allqs = np.array([max_min_deltaT.squeeze(), min_min_deltaT.squeeze(), max_max_deltaT.squeeze(), min_max_deltaT.squeeze()])
min_index = np.argmin(np.abs(allqs), axis=0)
max_index = np.argmax(np.abs(allqs), axis=0)
min_deltaT = allqs[min_index, range(allqs.shape[1])]
max_deltaT = allqs[max_index, range(allqs.shape[1])]

# Create output dataframe
dataset = pd.DataFrame({'OPERs': s3_ploset.opers,
                        'PAS3 915000 min Temp': s3_min_temp.squeeze(),
                        'PAS3 915000 max Temp': s3_max_temp.squeeze(),
                        'ESP-3 PCAS 9386 min Temp': esp3_min_temps[0, :],
                        'ESP-3 PCAS 9386 max Temp': esp3_max_temps[0, :],
                        'ESP-3 PCAS 9387 min Temp': esp3_min_temps[1, :],
                        'ESP-3 PCAS 9387 max Temp': esp3_max_temps[1, :],
                        'ESP-3 PCAS 9388 min Temp': esp3_min_temps[2, :],
                        'ESP-3 PCAS 9388 max Temp': esp3_max_temps[2, :],
                        'ESP-3 PCAS 9393 min Temp': esp3_min_temps[3, :],
                        'ESP-3 PCAS 9393 max Temp': esp3_max_temps[3, :],
                        'ESP-3 PCAS 9394 min Temp': esp3_min_temps[4, :],
                        'ESP-3 PCAS 9394 max Temp': esp3_max_temps[4, :],
                        'ESP-3 PCAS 9395 min Temp': esp3_min_temps[5, :],
                        'ESP-3 PCAS 9395 max Temp': esp3_max_temps[5, :],
                        'CAS - PCAS max-min dT': max_min_deltaT.squeeze(),
                        'CAS - PCAS min-min dT': min_min_deltaT.squeeze(),
                        'CAS - PCAS max-max dT': max_max_deltaT.squeeze(),
                        'CAS - PCAS min-max dT': min_max_deltaT.squeeze(),
                        'min ESP-3 dT': min_deltaT,
                        'max ESP-3 dT': max_deltaT
                        })

dataset = dataset[['OPERs', 'PAS3 915000 min Temp', 'PAS3 915000 max Temp', 'ESP-3 PCAS 9386 min Temp',
                       'ESP-3 PCAS 9386 max Temp', 'ESP-3 PCAS 9387 min Temp', 'ESP-3 PCAS 9387 max Temp',
                       'ESP-3 PCAS 9388 min Temp', 'ESP-3 PCAS 9388 max Temp', 'ESP-3 PCAS 9393 min Temp',
                       'ESP-3 PCAS 9393 max Temp', 'ESP-3 PCAS 9394 min Temp', 'ESP-3 PCAS 9394 max Temp',
                       'ESP-3 PCAS 9395 min Temp', 'ESP-3 PCAS 9395 max Temp', 'CAS - PCAS max-min dT',
                       'CAS - PCAS min-min dT', 'CAS - PCAS max-max dT', 'CAS - PCAS min-max dT',
                       'min ESP-3 dT', 'max ESP-3 dT']]

# Write to a csv file
print('\nwriting s3_pas_to_esp3_pcas_dT.csv')
dataset.to_csv('s3_pas_to_esp3_pcas_dT.csv')
