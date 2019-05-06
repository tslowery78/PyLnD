class GRIDLOCA:
    """Class of grid location results from NASTRAN."""

    def __init__(self, name):
        """Method to initialize GRIDLOCA class."""
        self.name = name
        self.grids = {}
        self.load_gridloca()

    def load_gridloca(self):
        """Method to read the GRIDLOCA f06 file for grid locations."""

        # Read in results.
        with open(self.name) as f:
            for line in f:
                if line[18:23] == '  G  ':
                    grid = int(line[0:14])
                    x_pos = float(line[26:39])
                    y_pos = float(line[41:54])
                    z_pos = float(line[56:69])
                    if grid not in self.grids.keys():
                        self.grids[grid] = [x_pos, y_pos, z_pos]


class USET:
    """Class of USET table output from NASTRAN."""

    def __init__(self, name):
        """Method to initialize the USET class."""
        self.name = name
        self.aset = []
        self.aset_6dof = []
        self.gset = []
        self.oset = []
        self.load_uset()

    def load_uset(self):
        """Method to load the USET f06."""

        # Read the USET table.
        with open(self.name) as f:
            i = 0
            for line in f:
                if line.__len__() > 29:
                 if line[16:18] == '- ' and line[38:40] == '- ':
                        # Get ASET DOF
                        if line[60:66] != '      ':
                            if line[30:38] != '        ':
                                grid = int(line[30:38])
                                i = 1
                            dof = int(line[40:42])
                            self.aset.append((grid, dof))
                            i += 1
                            if i == 6:
                                self.aset_6dof.append(grid)
                        # Get GSET DOF
                        if line[78:84] != '      ':
                            if line[30:38] != '        ':
                                grid = int(line[30:38])
                                i = 1
                            dof = int(line[40:42])
                            self.gset.append((grid, dof))
                            i += 1
                        # Get OSET DOF
                        if line[90:96] != '      ':
                            if line[30:38] != '        ':
                                grid = int(line[30:38])
                                i = 1
                            dof = int(line[40:42])
                            self.oset.append((grid, dof))
                            i += 1
