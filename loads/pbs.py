class PBS():
    """Class containing pertinent info on a PBS run file."""

    def __init__(self, name):
        self.name = name
        self.blkfiles = {}
        self.load_pbs()

    def load_pbs(self):
        """Method to extract info a from pbs file."""

        with open(self.name) as f:
            for line in f:
                # Get the blk path and acronym names.
                if line[0:2] == 'cp':
                    if '.blk' in line:
                        l_split = line.split()
                        blkfile = l_split[-2]
                        acron = l_split[-1]
                        if acron not in self.blkfiles.keys():
                            self.blkfiles[acron] = blkfile
