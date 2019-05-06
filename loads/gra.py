from pylab import *


class GRA:
    """This is a screening code graphics time history object."""

    def __init__(self, name):
        """Initializing the GRA object."""
        self.name = name
        self.data = {}
        self.read_gra()

    def read_gra(self):
        """Function to read the GRA time history.

            Ex:  GRA.read_gra()
        """
        import re
        import numpy as np

        # Open the GRA file and read line by line making numpy array.
        with open(self.name) as f:
            for line in f:
                line = line.rstrip()
                if line[0] == '$':
                    elem = int(line[16:27].strip())
                    if elem not in self.data.keys():
                        self.data[elem] = {}
                    dof = int(line[32:35].strip())
                    if dof not in self.data[elem].keys():
                        self.data[elem][dof] = np.empty((0, 2))
                elif line[0] == ' ':
                    line_chunk = [line[i:i + 8] for i in range(0, len(line), 8)] # chunk up in 8-char segments
                    line_chunk = [i for i in line_chunk if "ENDT" not in i] # Remove ENDT
                    line_chunk = [i for i in line_chunk if "        " not in i]  # Remove empty first field.
                    line_chunk = [i.replace('-', 'e-') for i in line_chunk] # Add the exponent at the end
                    line_chunk = [re.sub('^e', '', i) for i in line_chunk]
                    line_data = list(map(float, line_chunk))    # Convert the strings to floats
                    new_times = np.asarray(line_data[0::2])
                    new_loads = np.asarray(line_data[1::2])
                    new_data = np.column_stack((new_times, new_loads))
                    self.data[elem][dof] = np.append(self.data[elem][dof], new_data, axis=0)

    def plot(self, elem, dof):
        """Function to plot the time histories.

            Ex:  GRA.plot(1000, 1)
        """

        # Find the time and values requested.
        elem = self.makeint(elem)
        dof = self.makeint(dof)
        if elem not in self.data.keys():
            raise Exception(elem.__str__() + " is not in this GRA object "
                            + self.name)
        if dof not in self.data[elem].keys():
            raise Exception(dof.__str__() + " is not a DOF in this GRA object "
                            + self.name + " element " + elem.__str__())
        time = self.data[elem][dof][:, 0]
        val = self.data[elem][dof][:, 1]
        plot(time, val)
        show()

    def makeint(self, val):
        """Function to make a string an integer if you can.

            Ex:  GRA.makeint('100')
        """
        try:
            val = int(val)
        except ValueError:
            pass
        return val

    def save2mat(self, outfile):
        """Method to save the gra file to a Matlab mat file.

            Ex:  GRA.save2mat('outfile.mat')
        """
        from PyLnD.matlab.mat_utilities import save2mat

        save2mat(key='gra', olist=self.data, ofile=outfile)
