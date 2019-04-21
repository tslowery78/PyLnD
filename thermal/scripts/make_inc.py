#!/ots/sw/osstoolkit/15.4/sles12-x86_64/bin/python3.6

import argparse
import json
from PyLnD.thermal.ptcs_map import make_inc

# Get the inc conversion json and oper list
parser = argparse.ArgumentParser()
parser.add_argument("element", help="element to convert")
parser.add_argument("json", help="inc conversion json")
parser.add_argument("operlis", help="oper list")
parser.add_argument("plo_tar_zip", help="tarzip with all PLO")
parser.add_argument("bytype", help="byalpha or byoper")
parser.add_argument('-g', action='store_true')
args = parser.parse_args()

# Define the inputs
element = args.element
json_name = args.json
operlis = args.operlis
plo_tar_zip = args.plo_tar_zip
bytype = args.bytype
debug = args.g
if debug:
    print('Debug mode is active; all inputs are expected to be in the run path.')

# Read the inc info json
with open(json_name) as json_file:
    inc_info = json.load(json_file)

# Pull out the map from the inc info json
maps = inc_info[element.upper()]['maps']
desc = inc_info[element.upper()]['desc']
types = inc_info[element.upper()]['types']

# For each map convert the relevant inc files
for i, i_map in enumerate(maps):
    if debug:
        i_map = i_map.split(sep='/')[-1]
    if desc[i] == '-':
        inc_root_name = types[i].lower() + '_' + element
    else:
        inc_root_name = types[i].lower() + '_' + element + '_' + desc[i].lower()
    make_inc(i_map, plo_tar_zip, operlis, inc_root_name, bytype)
