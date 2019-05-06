from PyLnD.thermal.inc import INC
import numpy as np


class TTH():
    """Class which represents the temperature time history of selected elements across a series of inc."""

    def __init__(self, **kwargs):
        """Method to initialize this TTH object."""

        # Initialize class variables.
        self.loc = ''
        self.incfiles = []
        self.elems = []
        self.num_inc = 0
        self.num_elems = 0
        self.elem_tth = []
        self.avg_tth = []
        self.n_sc = 0

        # Obtain the keyword arguments.
        if 'incfiles' in kwargs.keys():
            self.incfiles = kwargs['incfiles']
            self.num_inc = np.size(self.incfiles)
        else:
            raise Exception('List of incfiles needed: TTH(incfiles=[], elems=[])')
        if 'elems' in kwargs.keys():    # Convert strings to integers
            self.elems = kwargs['elems']
            self.elems = list(map(int, self.elems))
            self.num_elems = np.size(self.elems)
        else:
            raise Exception('List of elems needed: TTH(incfiles=[], elems=[])')
        if 'loc' in kwargs.keys():
            self.loc = kwargs['loc']

        # Extract the time histories.
        self.extract()

    def extract(self):
        """Method to extract the temperature time history of the elements."""

        # Determine the size of the problem.
        inc = INC(self.loc + self.incfiles[0])
        self.n_sc = inc.n_sc

        # Initialize the size of the selected elements temperature time histories.
        self.elem_tth = np.empty([self.num_inc, self.num_elems, self.n_sc])

        # Loop on each inc file and extract the time histories of the selected elements.
        for i, incfile in enumerate(self.incfiles):
            if i > 0:
                inc = INC(self.loc + incfile)
                if self.n_sc != inc.n_sc:
                    raise Exception('The number of subcases in {0} is the not the same as the rest'.format(incfile))
            for j, elem in enumerate(self.elems):
                idx = elem == inc.elements
                self.elem_tth[i, j, :] = inc.inc[idx, :]

        # Find the mean temperatures of the selected elements.
        self.avg_tth = np.mean(self.elem_tth, axis=1)




