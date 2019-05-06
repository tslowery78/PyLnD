class PLUME_DAT:
    """Class of PILAGER surface model dat file."""

    def __init__(self, name):
        """Method to initialize the PLUME DAT class."""
        self.name = name
        self.psm = []
        self.plume_grids = {}
        self.loads_grids = []
        self.loads_models = []

    def load_dat(self, datfile):
        """Method to load the surface model dat file."""

        # Read the dat file and extract important bits.
        with open(datfile) as f:
            for line in f:
                self.psm.append(line)
                if line[0:4].lower() == 'grid':
                    grid = int(line[8:16])
                    x_pos = float(line[24:32])
                    y_pos = float(line[32:40])
                    z_pos = float(line[40:48])
                    if grid not in self.plume_grids.keys():
                        self.plume_grids[grid] = [x_pos, y_pos, z_pos]
