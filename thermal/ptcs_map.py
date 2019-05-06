import numpy as np
import math


class PTCSMap:
    """Map from SINDA nodes to FEM beams or plates."""

    def __init__(self, name):
        """Initialize all the map attributes."""
        self.name = name
        self.map = {}
        self.elements = []
        self.read_map()

    def read_map(self):
        """Function to read the contents of a PTCS map."""
        # 191  FORMAT( I8, I2, 4(2X,A6,I8,F6.3))
        with open(self.name) as f:
            for line in f:
                # if line[0] != '$':
                #     elem = int(line[0:8])
                #     self.elements.append(elem)
                #     self.map[elem] = {}
                #     num_mapped = int(line[8:10])
                #     self.map[elem]['sub_models'] = []
                #     self.map[elem]['nodes'] = []
                #     self.map[elem]['weights'] = []
                #     for i in range(0, num_mapped):
                #         bias = 22 * i
                #         sub_model = line[13 + bias - 1: 18 + bias].strip()
                #         node = int(line[19 + bias - 1: 26 + bias])
                #         weight = float(line[27 + bias - 1: 32 + bias])
                #         self.map[elem]['sub_models'].append(sub_model)
                #         self.map[elem]["nodes"].append(node)
                #         self.map[elem]['weights'].append(weight)
                if line[0] != '$':
                    line_split = line.split(sep=' ')
                    line_split = [item.rstrip() for item in line_split if item != '']
                    elem = int(line_split[0])
                    self.elements.append(elem)
                    self.map[elem] = {}
                    num_mapped = int(line_split[1])
                    self.map[elem]['sub_models'] = []
                    self.map[elem]['nodes'] = []
                    self.map[elem]['weights'] = []
                    for i in range(0, num_mapped):
                        sub_model = line_split[i + (i + 1)*2]
                        node = int(line_split[i + (i + 1)*2 + 1])
                        weight = float(line_split[i + (i + 1)*2 + 2])
                        self.map[elem]['sub_models'].append(sub_model)
                        self.map[elem]["nodes"].append(node)
                        self.map[elem]['weights'].append(weight)


def make_inc(ptcs_map_file, plo_tar_zip, oper_list, inc_root_name, bytype):
    """Method to create the inc files for a plo set and oper list"""
    from PyLnD.thermal.plo import PLOSet

    # Determine which component is being analyzed
    inc_type = inc_root_name.split(sep='_')[0]
    component = inc_root_name.split(sep='_')[1]

    # Create the map object
    print('PTCS map:\t\t\t{0}'.format(ptcs_map_file))
    ptcs_map = PTCSMap(ptcs_map_file)

    # Create the PLOSet object
    plo_set = PLOSet(tarzip=plo_tar_zip, bytype=bytype, operlist=oper_list)

    # Read the opers in from the oper list
    print('OPER list\t\t\t{0}'.format(oper_list))
    with open(oper_list) as f:
        opers = f.read().splitlines()
    opers = [int(item) for item in opers]

    # Create the inc files from the plo sets and ptcs map
    for i, oper in enumerate(opers):

        # For every entry in the ptcs map, calculate the fem temperature
        number_elements = len(ptcs_map.elements)
        number_time_steps = plo_set.plos[0].num_time_steps
        inc = np.zeros([number_elements, number_time_steps])
        last_weight_sum = -1.0
        for e, element in enumerate(ptcs_map.elements):
            fem_weighted_temperatures = np.zeros([number_time_steps])
            weight_sum = 0
            node = 0
            plo_index = -1
            for j, node in enumerate(ptcs_map.map[element]['nodes']):
                sub_model = ptcs_map.map[element]['sub_models'][j]
                weight = ptcs_map.map[element]['weights'][j]
                weight_sum += weight

                # Some of the components use the opposite side map, bias back to that side
                if component == 's5':
                    sub_model = sub_model.replace('P5', 'S5')

                try:
                    plo_index = plo_set.sub_models.index(sub_model)
                except ValueError:
                    print('!!! WARNING {0} for fem {1} is referenced in the map but is not a PLO file !!!'
                          .format(sub_model, element))
                    continue
                plo = plo_set.plos[plo_index]
                nodal_temperatures = plo.plo[plo.nodes == node, :].reshape([number_time_steps])
                fem_weighted_temperatures += weight * nodal_temperatures
            if plo_index >= 0:
                # Properly handle the 0.5 and 1.0 weight factor issue, check if all the weight sums are the same
                if last_weight_sum > 0.0:
                    if not math.isclose(last_weight_sum, weight_sum, rel_tol=2e-3):
                        raise Exception("This map entry's weight sum is different than the others: {0}".format(node))
                else:
                    last_weight_sum = weight_sum
                if math.isclose(weight_sum, 2.0, rel_tol=2e-3):
                    if e == 0 and i == 0:
                        print('weight scaling:\t\t2.0')
                    inc[e, :] = fem_weighted_temperatures / 2
                elif math.isclose(weight_sum, 1.0, rel_tol=2e-3):
                    if e == 0 and i == 0:
                        print('weight scaling:\t\t\t1.0')
                    inc[e, :] = fem_weighted_temperatures
                else:
                    raise Exception('You must have a weight scale of 1.0 or 2.0:\n\t{0}: FEM node map {1}'.format(
                        ptcs_map_file, element))

        # Open the inc file and print
        inc_name = inc_root_name + '_' + str(opers[i]) + '.inc'
        print('\t{0}'.format(inc_name))
        with open(inc_name, 'w') as f:
            for k in range(number_time_steps):
                sub_case = 101 + k
                for e, element in enumerate(ptcs_map.elements):
                    line = ''
                    if inc_type == 'beams':
                        nastran_card = 'TEMPRB'
                        line = '{0}, {1}, {2}, {3:9.4f}, {4:9.4f}\n'.format(nastran_card, sub_case, element, inc[e, k],
                                                                            inc[e, k])
                    elif inc_type == 'plates':
                        nastran_card = 'TEMPP1'
                        line = '{0}, {1}, {2}, {3:9.4f}\n'.format(nastran_card, sub_case, element, inc[e, k])
                    elif inc_type == 'nodes':
                        nastran_card = 'TEMP'
                        line = '{0}, {1}, {2}, {3:9.4f}\n'.format(nastran_card, sub_case, element, inc[e, k])
                    f.write(line)


if __name__ == '__main__':
    # beams_map = PTCSMap("P5_BARS_NOPRGF.map")
    # make_inc('P5_BARS_NOPRGF.map', 'plosets.lis', 'RPDAM19_NOVV_MNVR_WS4_OPERs.lis', 'beams_p5')
    # make_inc('P5_BARS_NOPRGF.map', 'plosets.lis', 'RPDAM19_NOVV_MNVR_WS4_OPERs.lis', 'beams_s5')
    make_inc('P5_BARS_NOPRGF.map', 'plosets.lis', 'RPDAM19_NOVV_MNVR_WS4_OPERs.lis', 'beams_s5')
