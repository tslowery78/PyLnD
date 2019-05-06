import numpy as np
import tarfile
from pprint import pprint


class INC:
    """INC is a NASTRAN input deck for temperatures at element/nodes."""

    def __init__(self, name, **kwargs):
        """Initializing the INC object."""

        # Get the kwargs
        self.inc_list = []
        if 'list' in kwargs.keys():
            self.inc_list = kwargs['list']
        self.name = name
        self.n_sc = 0
        self.n_elems = 0
        self.elements = []
        self.inc = []
        self.read_inc()

    def read_inc(self):
        """Method to read an inc file."""

        # Read in the inc.
        if self.inc_list:
            lines = self.inc_list
        else:
            with open(self.name) as f:
                lines = f.read().splitlines()
        remove = [i for i, v in enumerate(lines) if v[0] == '$']
        self.n_sc = int(lines[-1].split(sep=',')[1]) - 100
        self.n_elems = int((len(lines) - len(remove)) / self.n_sc)
        self.inc = np.zeros([self.n_elems, self.n_sc])
        np_lines = np.asarray(lines)
        np_lines = np.delete(np_lines, remove)
        # Put the data in the inc array.
        self.elements = np.zeros([self.n_elems], dtype=int)
        e = 0
        for line in np_lines:
            l_split = line.split(sep=',')
            case = int(l_split[1]) - 100
            if case == 1:
                # self.elements.append(int(l_split[2]))
                self.elements[e] = int(l_split[2])
            temp = float(l_split[3])
            self.inc[e, case - 1] = temp
            e += 1
            if e > self.n_elems - 1:
                e = 0

    def plot(self, **kwargs):
        """Plot selected fem temperatures."""
        import matplotlib.pyplot as plt

        # Get the kwargs
        if 'elements' in kwargs.keys():
            elements = kwargs['elements']
            if elements == 'all':
                elements = self.elements
            else:
                if type(elements) is not list:
                    elements = [elements]
        else:
            print(self.__doc__)
            raise Exception('You must supply an element or list of elements to plot.')

        # Plot the list of elements
        fig = plt.figure()
        axes = fig.add_axes([0.1, 0.1, 0.8, 0.8])
        axes.set_xlabel('Time Step')
        axes.set_ylabel('degF')
        plt.grid()
        for requested_element in elements:
            axes.plot(np.transpose(self.inc[requested_element == self.elements, :]), label=str(requested_element))
        if len(elements) <= 10:
            plt.legend()
        plt.show()


class INCSet:
    """Class of object to represent a set of INC objects.
        Ex:
        myset = INCSet(tarzip='inc.tar.gz', bytype='byoper', operlist='RPDAM19_stdyst_vv_ws4_OPERs.lis', etype='beams')
    """

    def __init__(self, **kwargs):
        """Method to initialize."""

        # Get the kwargs
        if 'tarzip' in kwargs.keys():
            self.tarzip = kwargs['tarzip']
        if 'bytype' in kwargs.keys():
            self.bytype = kwargs['bytype']
        else:
            raise \
                Exception('Missing "bytype" option: INCSet(tarzip=tarzip, bytype=bytype, operlist=operlist)')
        operlist = None
        if 'operlist' in kwargs.keys():
            operlist = kwargs['operlist']
            with open(operlist) as f:
                self.opers = f.read().splitlines()
                self.num_opers = len(self.opers)
        self.etype = None
        if 'etype' in kwargs.keys():
            self.etype = kwargs['etype']
        nalphas = 12
        if 'nalphas' in kwargs.keys():
            nalphas = kwargs['nalphas']

        # Print the inputs
        print('\nINCSet Inputs:')
        print('\tincset tarzip file: {0}'.format(self.tarzip))
        print('\tbytype: {0}'.format(self.bytype))
        if operlist:
            print('\toperlist: {0}'.format(operlist))
            print('\tnumber of opers: {0}'.format(self.num_opers))
        if self.etype:
            print('\tincset element type: {0}'.format(self.etype))

        # Initialize attributes
        self.time_steps = None
        self.num_time_steps = 0
        if self.bytype == 'byalpha':
            if nalphas != 'all':
                self.time_steps = range(0, 360, 30)
                self.num_time_steps = len(self.time_steps)
                print('\tnumber of time steps: {0}'.format(self.num_time_steps))
            elif nalphas == 'all':
                self.time_steps = range(0, 375, 15)
                self.num_time_steps = len(self.time_steps)
                print('\tnumber of time steps: {0}'.format(self.num_time_steps))
            else:
                raise Exception('nalphas must be 12 or "all"')
        self.num_elements = 0
        self.elements = []
        self.inc_set = []
        self.parse_tarzip()

    def parse_tarzip(self):
        """Method to parse the tarzip file full of INC files"""

        # Extract the inc's from the tarzip
        tar = tarfile.open(self.tarzip, 'r:gz')
        incs = {}
        print('\nreading the following inc files:')
        for member in tar.getmembers():
            t = None
            if '.inc' in member.name:
                if self.etype:
                    if self.etype in member.name:
                        t = tar.extractfile(member)
                else:
                    t = tar.extractfile(member)
                if t:
                    print('\t{0}'.format(member.name))
                    inc_text = t.read()
                    inc_text = inc_text.decode('utf-8')
                    inc_text = inc_text.rstrip().split('\n')
                    incs[member.name] = INC(member.name, list=inc_text)
        tar.close()

        # Insert the temperature data into large array
        self.elements = incs[list(incs.keys())[0]].elements
        if self.bytype == 'byalpha':
            [self.num_elements, self.num_opers] = incs[list(incs.keys())[0]].inc.shape
            self.inc_set = np.zeros([self.num_elements, self.num_opers, self.num_time_steps])
            for i, alpha in enumerate(self.time_steps):
                for j, inc in incs.items():
                    if self.etype:
                        if '_' + str(alpha) + '.inc' in inc.name and self.etype in inc.name:
                            self.inc_set[:, :, i] = inc.inc[:, :]
                    else:
                        if '_' + str(alpha) + '.inc' in inc.name:
                            self.inc_set[:, :, i] = inc.inc[:, :]
        elif self.bytype == 'byoper':
            [self.num_elements, self.num_time_steps] = incs[list(incs.keys())[0]].inc.shape
            self.time_steps = np.arange(1, self.num_time_steps + 1)
            self.inc_set = np.zeros([self.num_elements, self.num_opers, self.num_time_steps])
            for i, oper in enumerate(self.opers):
                for j, inc in incs.items():
                    if oper + '.inc' in inc.name and self.etype in inc.name:
                        self.inc_set[:, i, :] = inc.inc[:, :]

        # Print a results summary
        print('\nIntake:')
        print('\tnumber of elements: {0}'.format(self.num_elements))
        print('\tnumber of opers: {0}'.format(self.num_opers))
        print('\tnumber of time steps: {0}'.format(self.num_time_steps))
        print('\nInfo:')
        print('\tmax temperature: {0:8.5f}'.format(self.inc_set.max()))
        print('\tmin temperature: {0:8.5f}'.format(self.inc_set.min()))
        print('\tincset ({0} x {1} x {2})'.format(self.num_elements, self.num_opers, self.num_time_steps))
        print('\nPretty Print:')
        pprint(vars(self))

    def plot(self, **kwargs):
        """Method to plot selected temperatures."""
        import matplotlib.pyplot as plt

        # Get the kwargs
        if 'elements' in kwargs.keys():
            elements = kwargs['elements']
            if type(elements) is not list:
                elements = [elements]
        else:
            print(self.__doc__)
            raise Exception('You must supply an element or list of elements to plot.')
        if 'opers' in kwargs.keys():
            opers = kwargs['opers']
            all_opers = False
            if opers == 'all':
                all_opers = True
            else:
                if type(opers) is not list:
                    opers = [opers]
        else:
            print(self.__doc__)
            raise Exception('You must supply an open or list of opers to plot.')

        # Plot the list of elements
        fig = plt.figure()
        axes = fig.add_axes([0.1, 0.1, 0.8, 0.8])
        axes.set_xlabel('Time Step')
        axes.set_ylabel('degF')
        plt.grid()
        for requested_element in elements:
            size = self.inc_set[requested_element].shape
            if all_opers:
                opers = range(0, size[1])
            for oper in opers:
                axes.plot(self.inc_set[requested_element][:, oper], label=str(requested_element) + ' ' + str(oper + 1))
        plt.legend()
        plt.show()


class SGM:
    """Class of object to represent the sgm file, csv of inc."""

    def __init__(self, name):
        """Method to initialize."""
        self.name = name
        self.sgm = {}
        self.psarj = []
        self.ssarj = []
        self.read_sgm()
        self.eqv_15deg()

    def read_sgm(self):
        """Method to read in the sgm file and parse."""

        # Read the csv file line by line using the first column of each row as the entity of interest
        #  be it TIME, PSARJ, SSARJ, or element number.
        with open(self.name) as f:
            for i, line in enumerate(f):
                line_split = line.split(sep=',')
                if i > 2:
                    line_split[0] = int(line_split[0])
                label = line_split[0]
                res = list(map(float, line_split[1:]))
                if label not in self.sgm.keys():
                    self.sgm[label] = np.asarray(res)

    def eqv_15deg(self):
        """Method to round to nearest 15deg increment for sarj angles."""

        # Setup 15deg angles array.
        alpha_15s = np.arange(0.0, 375.0, 15.0)

        # Find the minimum absolute difference for each PSARJ and SSARJ.
        for alpha in self.sgm['PSARJ']:
            diffs = np.abs(alpha_15s - alpha)
            idx = diffs.argmin()
            self.psarj.append(alpha_15s[idx])
        for alpha in self.sgm['SSARJ']:
            diffs = np.abs(alpha_15s - alpha)
            idx = diffs.argmin()
            self.ssarj.append(alpha_15s[idx])


if __name__ == '__main__':
    # with open('inc.lis', 'r') as f:
    #     inc_list = f.read().splitlines()
    # myset = INCSet(inc_list, 'byalpha')
    # myset.plot(elements=1, opers='all')
    # myinc = INC('plates_s6ls_841083152.inc')
    # myinc.plot(elements='all')
    myset = INCSet(tarzip='inc.tar.gz', bytype='byoper', operlist='RPDAM19_stdyst_vv_ws4_OPERs.lis', etype='beams')

    pass
