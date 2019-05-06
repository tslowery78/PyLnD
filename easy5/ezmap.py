class EZMAP:
    """Class representing an Easy5 schematic mapped out in desired order."""

    def __init__(self, list_file):
        """Method to initialize object."""

        # Initialize the parameters
        self.list_file = list_file
        self.paths_list = []
        self.paths = {}
        self.load()

    def load(self):
        """Method to load the ezmap list file."""

        # Make the submodel dict
        with open(self.list_file) as f:
            lines = f.read().splitlines()
        path_index = [i for i, item in enumerate(lines) if 'path:' in item]
        submodel_name = ''
        components = ''
        self.paths_list = []
        self.paths = {}
        for i, p in enumerate(path_index):
            try:
                p_lines = lines[p:path_index[i + 1]]
            except IndexError:
                p_lines = lines[p:]
            path_name = p_lines[0][6:]
            self.paths[path_name] = {}
            self.paths_list.append(path_name)
            for sub_group in p_lines[1:]:
                if sub_group:
                    if ':' in sub_group:
                        sub_group_split = sub_group.split(sep=':')
                        submodel_name = sub_group_split[0]
                        components = sub_group_split[1].split()
                    elif sub_group:
                        submodel_name = sub_group
                        components = sub_group
                    self.paths[path_name][submodel_name] = components
                    if 'submodels' not in self.paths[path_name].keys():
                        self.paths[path_name]['submodels'] = []
                    self.paths[path_name]['submodels'].append(submodel_name)


if __name__ == '__main__':
    ezmap = EZMAP('rhs_map.lis')
    pass
