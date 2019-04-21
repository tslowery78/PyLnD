import numpy as np
from pprint import pprint


class PLO:
    """PLO is a plate-line-object file that has SINDA node temperatures.

        Create the object:
            Ex. plo = PLO(filename)

        Plot a list of nodes:
            Ex. plo.plot(nodes=[1, 2])

        Plot all nodes:
            Ex. plo.plot(nodes='all')"""

    def __init__(self, name, **kwargs):
        """Method to initialize the PLO object."""

        # Get the kwargs
        self.plo_list = []
        if 'list' in kwargs.keys():
            self.plo_list = kwargs['list']
        self.name = name
        self.num_nodes = 0
        self.num_time_steps = 0
        self.nodes = []
        self.T_ref = []
        self.plo = []
        self.read_plo()

    def read_plo(self):
        """Method to read the PLO file."""

        # Read the PLO file
        if self.plo_list:
            res = np.fromstring('\n'.join(self.plo_list), sep=' ')
        else:
            res = np.fromfile(self.name, sep=' ')

        # Set the PLO parameters
        self.num_nodes = int(res[0])
        self.nodes = (res[1:self.num_nodes + 1]).astype(int)
        self.num_time_steps = int(res.size / (self.num_nodes + 1)) - 1
        self.plo = np.zeros([self.num_nodes, self.num_time_steps])

        # Loop over each time step and extract the temperatures
        for i in range(1, self.num_time_steps + 1):
            m = i * (self.num_nodes + 1)
            n = (i + 1) * (self.num_nodes + 1)
            col = res[m:n]
            self.plo[:, i - 1] = col[1:]

    def plot(self, **kwargs):
        """Method to plot selected temperatures."""
        import matplotlib.pyplot as plt

        # Get the kwargs
        if 'nodes' in kwargs.keys():
            nodes = kwargs['nodes']
            if nodes == 'all':
                nodes = self.nodes
            elif type(nodes) is not list:
                nodes = [nodes]
        else:
            print(self.__doc__)
            raise Exception('You must supply a node or list of nodes to plot.')

        # Plot the list of nodes
        fig = plt.figure()
        axes = fig.add_axes([0.1, 0.1, 0.8, 0.8])
        axes.set_xlabel('Time Step')
        axes.set_ylabel('degF')
        plt.grid()
        for requested_node in nodes:
            test = self.plo[self.nodes == requested_node, :]
            axes.plot(test.transpose(), label=str(requested_node))
        plt.title(self.name)
        plt.legend()
        plt.show()


class PLOSet:
    """Class of object representing a group of PLO per OPER/alpha containing the required PTCS sub-models"""

    def __init__(self, **kwargs):
        """Method to initialize"""

        # Get the kwargs
        if 'tarzip' in kwargs.keys():
            self.tarzip = kwargs['tarzip']
        if 'bytype' in kwargs.keys():
            self.bytype = kwargs['bytype']
        else:
            raise \
                Exception('Missing "bytype" option: PLOSet(tarzip=tarzip, bytype=bytype, operlist=operlist)')
        operlist = None
        if 'operlist' in kwargs.keys():
            operlist = kwargs['operlist']
            with open(operlist) as f:
                self.opers = f.read().splitlines()
                self.num_opers = len(self.opers)
        self.ptype = None
        if 'plosub' in kwargs.keys():
            self.ptype = kwargs['plosub']

        # Print the inputs
        print('\nPLOSet Inputs:')
        print('\tploset tarzip file: {0}'.format(self.tarzip))
        print('\tbytype: {0}'.format(self.bytype))
        if operlist:
            print('\toperlist: {0}'.format(operlist))
            print('\tnumber of opers: {0}'.format(self.num_opers))
        if self.ptype:
            print('\tploset element type: {0}'.format(self.ptype))

        # Initialize attributes
        self.time_steps = None
        self.num_time_steps = 0
        if self.bytype == 'byalpha':
            self.time_steps = range(0, 360, 30)
            self.num_time_steps = len(self.time_steps)
            print('\tnumber of time steps: {0}'.format(self.num_time_steps))
        self.num_nodes = {}
        self.nodes = {}
        self.plo_set = {}
        self.parse_tarzip()

    def parse_tarzip(self):
        """Method to parse the tarzip file full of PLO files"""
        import tarfile

        # Extract the plo's from the tarzip
        tar = tarfile.open(self.tarzip, 'r:gz')
        plos = {}
        print('\nreading the following plo files:')
        for member in tar.getmembers():
            t = None
            if '.PLO' in member.name:
                if self.ptype:
                    if self.ptype in member.name:
                        t = tar.extractfile(member)
                else:
                    t = tar.extractfile(member)
                if t:
                    print('\t{0}'.format(member.name))
                    plo_text = t.read()
                    plo_text = plo_text.decode('utf-8')
                    plo_text = plo_text.rstrip().split('\n')
                    plos[member.name] = PLO(member.name, list=plo_text)
        tar.close()

        # Find the set of submodel id's in the plos
        submodel_set = set([item.split(sep='_')[0] for item in list(plos.keys())])

        # Insert the temperature data into large array
        for submodel in submodel_set:
            print(submodel)
            if self.bytype == 'byalpha':
                [self.num_nodes[submodel], self.num_opers] = plos[list(plos.keys())[0]].plo.shape
                self.plo_set[submodel] = np.zeros([self.num_nodes[submodel], self.num_opers, self.num_time_steps])
                for i, alpha in enumerate(range(0, 360, 30)):
                    for j, plo in plos.items():
                        if '_' + str(alpha) + '.inc' in plo.name:
                            self.plo_set[:, :, i] = plo.plo[:, :]
            elif self.bytype == 'byoper':
                for i, oper in enumerate(self.opers):
                    print(i, oper)
                    for j, plo in plos.items():
                        if oper + '.plo' in plo.name.lower() and submodel + '_' in plo.name:
                            if i == 0:
                                self.nodes[submodel] = plo.nodes
                                [self.num_nodes[submodel], self.num_time_steps] = plo.plo.shape
                                self.time_steps = np.arange(1, self.num_time_steps + 1)
                                self.plo_set[submodel] = np.zeros(
                                    [self.num_nodes[submodel], self.num_opers, self.num_time_steps])
                            self.plo_set[submodel][:, i, :] = plo.plo[:, :]
                            break

        # Print a results summary
        print('\nIntake:')
        print('\tnumber of elements: {0}'.format(self.num_nodes))
        print('\tnumber of opers: {0}'.format(self.num_opers))
        print('\tnumber of time steps: {0}'.format(self.num_time_steps))
        print('\nInfo:')
        print('\tmax temperature: {0:8.5f}'.format(self.plo_set.max()))
        print('\tmin temperature: {0:8.5f}'.format(self.plo_set.min()))
        print('\tincset ({0} x {1} x {2})'.format(self.num_nodes, self.num_opers, self.num_time_steps))
        print('\nPretty Print:')
        pprint(vars(self))
