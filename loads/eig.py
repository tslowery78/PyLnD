class EIG:
    """Eigenvalues from the EIGFILE."""

    def __init__(self, name):
        """Initializing the EIG class object."""
        self.name = name
        self.eigenvalues = []
        self.frequency = []
        self.read_eig()

    def read_eig(self):
        """Method to read through the EIGFILE and find the set of eigenvalues.

            Ex:  eig.read_eig()
        """
        # Read through each line of the EIGFILE and extract the eigenvalues.
        with open(self.name) as f:
            for line in f:
                if line[87:99] == '1.000000E+00':
                    data = line.split()
                    self.eigenvalues.append(float(data[2]))
                    self.frequency.append(float(data[4]))
