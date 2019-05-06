class BLK:
    """Class of NASTRAN bulk data."""

    def __init__(self, name):
        """Method to initialize the BLK class."""
        self.name = name
        self.grids = {}
        self.surfmod = []
        self.surfgroup = []
        self.esephi_name = None
        self.load_blk()

    def load_blk(self):
        """Method to read the blk data file."""
        import os.path

        # Read and extract needed bulk data entries.
        with open(self.name) as f:
            for line in f:
                # GRIDs
                if line[0:4].lower() == 'grid':
                    line = line.replace('\t', ',')
                    if ',' in line:
                        l_split = line.split(',')
                        if l_split[0].lower() == 'grid':
                            grid = l_split[1]
                            grid = grid[0:8]
                        else:
                            grid = line[8:16]
                    else:
                        grid = line[8:16]
                    grid = int(grid)
                    if grid not in self.grids.keys():
                        self.grids[grid] = []
                # SURFMOD
                if line[0:9] == "$ SURFMOD":
                    l_split = line.split(':')
                    surfmod = l_split[-1].rstrip()
                    if surfmod != '':
                        surfmod = l_split[-1].rstrip() + '.dat'
                        surfmod = surfmod.replace('.dat.dat', '.dat')
                        blkname = self.name.split('/')[-1]
                        blkloc = self.name.replace(blkname, '') + '../plume/'
                        surfmod = blkloc + surfmod
                        # Check if file exists.
                        if not os.path.exists(surfmod):
                            raise  Exception('!!! Plume model %s does not exist !!!' % surfmod)
                    self.surfmod = surfmod
                # SURFGROUP
                if line[0:11] == "$ SURFGROUP":
                    surfgroup = line.split(':')[-1].rstrip()
                    self.surfgroup = surfgroup
                # ESEPHI NAME
                if line[0:13] == "$ ESEPHI NAME":
                    esephi_name = line.split(':')[-1].rstrip()
                    self.esephi_name = esephi_name
