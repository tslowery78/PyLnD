class DAT103:
    """Class of NASTRAN 103 run deck."""

    def __init__(self, name):
        """Initializing the NASTRAN 103 run deck."""
        self.name = name
        self.included_blk = []
        self.load_dat()

    def load_dat(self):
        """Method to load the dat file information into the class."""

        with open(self.name) as f:
            for line in f:
                # Extract the included blkdata names.
                if line[0:7].lower() == 'include':
                    l_split = line.split()
                    included = l_split[1]
                    self.included_blk.append(included)
