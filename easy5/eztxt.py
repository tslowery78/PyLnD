import math


class EZTXT:
    """Class of object representing a Easy5 model documentation txt file."""

    def __init__(self, name):
        """Method to initialize object"""

        # initialize
        self.name = name
        self.component = {}
        self.load()

    def load(self):
        """Method to load and parse an Easy5 txt doc"""

        # Read the entire file
        with open(file=self.name) as f:
            lines = f.read().splitlines()

        # Determine the index components in the model
        component_index = [i for i, line in enumerate(lines) if ' Component:' in line]
        for i, index in enumerate(component_index):
            line = lines[index]
            line_split = line.split(sep=':')
            component_line = line_split[1].split(sep='-')
            component = component_line[0].strip()
            self.component[component] = {}
            component_desc = component_line[1][1:]
            self.component[component]['desc'] = component_desc
            try:
                subset = lines[index:component_index[i + 1]]
            except IndexError:
                subset = lines[index:]

            # Grab the desired parameters
            submodel_id = None
            submodel_desc = None

            # Get the submodel id and description
            smod_index = [item for item, line in enumerate(subset) if 'Contained in Submodel:' in line]
            if smod_index:
                s_line = subset[smod_index[0]]
                s_line_split = s_line.split(sep=':')
                submodel_id = s_line_split[1].split(sep='-')[0].strip()
                submodel_desc = s_line_split[1]
                k = s_line_split[1].index('-')
                submodel_desc = submodel_desc[k + 2:]
            self.component[component]['submodel_id'] = submodel_id
            self.component[component]['submodel_desc'] = submodel_desc

            # Get the params
            self.get_param('VOL_{0}'.format(component), subset, component, 'vol')
            if 'vol' in self.component[component].keys():
                self.component[component]['port_config'] = 'Storage'
            self.get_param('DH_{0}'.format(component), subset, component, 'dh')
            self.get_param('DiameterInlet_{0}'.format(component), subset, component, 'dh')
            self.get_param('LEN_{0}'.format(component), subset, component, 'len')
            self.get_param('Length_{0}'.format(component), subset, component, 'len')
            self.get_param('OD_{0}'.format(component), subset, component, 'od')
            self.get_param('XLN_{0}'.format(component), subset, component, 'xln')
            self.get_param('DZH_{0}'.format(component), subset, component, 'dzh')
            self.get_param('DENS_{0}'.format(component), subset, component, 'dens')
            self.get_param('SPHT_{0}'.format(component), subset, component, 'spht')

            # Get the port config
            index = [item for item, line in enumerate(subset) if 'Connectivity =' in line]
            if not index:
                index = [item for item, line in enumerate(subset) if 'Port Configuration =' in line]
            if index:
                port_config = subset[index[0]].split(sep='=')[-1][1:]
                self.component[component]['port_config'] = port_config
            if 'WP' == component[0:2].upper():
                self.component[component]['port_config'] = 'Storage/Resistive/Storage'
            if 'port_config' in self.component[component].keys():
                # Set the pipe volume if it is storage/resistive
                if 'storage' in self.component[component]['port_config'].lower():
                    if 'len' in self.component[component].keys() and 'dh' in self.component[component].keys():
                        try:
                            self.component[component]['vol'] = self.component[component]['len'] * math.pi \
                                                               * (self.component[component]['dh'] / 2)**2
                        except TypeError:
                            self.component[component]['vol'] = 'na'

    def get_param(self, target, subset, component, desc):
        """Method to get the parameter from a subset."""

        index = [item for item, line in enumerate(subset) if target in line]
        if index:
            try:
                value = float(subset[index[0]].split()[1])
            except ValueError:
                value = subset[index[0]].split()[1]
            self.component[component][desc] = value


if __name__ == '__main__':
    eztxt = EZTXT('rhs_cooling_loop.txt')
    pass
