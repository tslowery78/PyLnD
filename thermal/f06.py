import numpy as np


class F06:
    """Class of object that represents a NASTRAN f06 file.
        Ex: f06 = F06(file='file.f06', outreqs=['cbar_forces', 'cbeam_forces', 'celas2_forces'])
    """

    def __init__(self, **kwargs):
        """Method to initialize a F06 object."""

        # Get the keyword arguments
        if 'file' in kwargs.keys():
            self.file = kwargs['file']
        else:
            raise Exception('You must supply an f06 file: file=file.f06')
        outreqs = []
        if 'outreqs' in kwargs.keys():
            outreqs = kwargs['outreqs']
            if type(outreqs) is not list:
                outreqs = [outreqs]

        # Initialize variables
        self.lines = []
        self.num_subcases = 0
        self.first_case = 0
        self.page_index = []
        self.bar_forces = {}
        self.bar_elements = []
        self.beam_forces = {}
        self.beam_elements = []
        self.beam_grids = {}
        self.celas2_forces = {}
        self.celas2_elements = []
        self.dof_names = {'ma1': (0, 'in-lbs'), 'ma2': (1, 'in-lbs'), 'mb1': (2, 'in-lbs'), 'mb2': (3, 'in-lbs'),
                          'sh1': (4, 'lbs'), 'sh2': (5, 'lbs'), 'ax': (6, 'lbs'), 'tor': (7, 'in-lbs'),
                          'for': (0, 'lbs')}
        self.inc = None

        # Parse the f06 file.
        self.parse_f06()

        # Get the requested outputs.
        for outreq in outreqs:
            if outreq == 'cbar_forces':
                self.get_cbar_forces()
            elif outreq == 'cbeam_forces':
                self.get_cbeam_forces()
            elif outreq == 'celas2_forces':
                self.get_celas2_forces()
            else:
                raise Exception('Unrecognized outreq: {0}'.format(outreq))

    def parse_f06(self):
        """Method to read the f06 as a list of strings."""

        # Open and read f06
        with open(self.file) as f:
            lines = f.read().splitlines()
        self.lines = lines

        # Determine the number of subcases.
        search_string = 'SUBCASE'
        sc_index = [i for i, x in enumerate(lines) if search_string in x and x[0] == '0']
        first_case = int(lines[sc_index[0]][117:120])
        last_case = int(lines[sc_index[-1]][117:120])
        n_sc = last_case - first_case + 1
        self.num_subcases = n_sc
        self.first_case = first_case

        # Determine the page index.
        search_string = 'PAGE'
        page_index = [i for i, x in enumerate(lines) if search_string == x[118:122]]
        self.page_index = page_index

    def get_cbar_forces(self):
        """Method to get the cbar forces from the f06."""

        lines = self.lines
        first_case = self.first_case
        page_index = self.page_index
        n_sc = self.num_subcases
        # Check for and read the bar forces table.
        search_string = 'F O R C E S   I N   B A R   E L E M E N T S         ( C B A R )'
        header_index = [i for i, x in enumerate(lines) if search_string in x]
        if header_index:
            for i, t in enumerate(header_index):
                # Get the current subcase.
                sc = int(lines[t - 2][117:120]) - first_case
                # Get the current page.
                page = int(lines[t - 4][122:128]) + 1
                # Loop over the rows in this page and grab the cbar forces.
                for e in range(t + 3, page_index[page - 1]):
                    element = int(lines[e][5:13])
                    if element not in self.bar_forces.keys():
                        self.bar_forces[element] = np.zeros([n_sc, 8])
                        self.bar_elements.append(element)
                    self.bar_forces[element][sc, 0] = float(lines[e][17:30])    # MA1
                    self.bar_forces[element][sc, 1] = float(lines[e][31:44])    # MA2
                    self.bar_forces[element][sc, 2] = float(lines[e][46:59])    # MB1
                    self.bar_forces[element][sc, 3] = float(lines[e][60:73])    # MB1
                    self.bar_forces[element][sc, 4] = float(lines[e][75:88])    # SH1
                    self.bar_forces[element][sc, 5] = float(lines[e][89:102])   # SH2
                    self.bar_forces[element][sc, 6] = float(lines[e][104:117])  # AX
                    self.bar_forces[element][sc, 7] = float(lines[e][119:132])  # TOR

    def get_cbeam_forces(self):
        """Method to get the cbeam forces from the f06."""

        lines = self.lines
        first_case = self.first_case
        page_index = self.page_index
        n_sc = self.num_subcases
        # Check for and read the beam forces table.
        search_string = 'F O R C E S   I N   B E A M   E L E M E N T S        ( C B E A M )'
        header_index = [i for i, x in enumerate(lines) if search_string in x]
        element = 0
        if header_index:
            for i, t in enumerate(header_index):
                # Get the current subcase.
                sc = int(lines[t - 2][117:120]) - first_case
                # Get the current page.
                page = int(lines[t - 4][122:128]) + 1
                # Loop over the rows in this page and grab the cbeam forces.
                side = 0
                for e in range(t + 3, page_index[page - 1]):
                    if lines[e][0] == '0':
                        side = 0
                        element = int(lines[e][2:11])
                        if element not in self.beam_forces.keys():
                            self.beam_forces[element] = np.zeros([n_sc, 8])
                            self.beam_elements.append(element)
                            self.beam_grids[element] = []
                    else:
                        side += 1
                        if side == 1:
                            if sc == 0:
                                self.beam_grids[element].append(int(lines[e][11:19]))    # A
                            self.beam_forces[element][sc, 0] = float(lines[e][30:43])    # MA1
                            self.beam_forces[element][sc, 1] = float(lines[e][44:57])    # MA2
                            self.beam_forces[element][sc, 4] = float(lines[e][59:72])    # SH1
                            self.beam_forces[element][sc, 5] = float(lines[e][73:86])    # SH2
                            self.beam_forces[element][sc, 6] = float(lines[e][88:101])   # AX
                            self.beam_forces[element][sc, 7] = float(lines[e][103:116])  # TOR
                        elif side == 2:
                            if sc == 0:
                                self.beam_grids[element].append(int(lines[e][11:19]))    # B
                            self.beam_forces[element][sc, 2] = float(lines[e][30:43])    # MB1
                            self.beam_forces[element][sc, 3] = float(lines[e][44:57])    # MB1

    def get_celas2_forces(self):
        """Method to get the celas2 forces from the f06."""

        lines = self.lines
        first_case = self.first_case
        page_index = self.page_index
        n_sc = self.num_subcases
        # Check for and read the celas2 forces table.
        search_string = 'F O R C E S   I N   S C A L A R   S P R I N G S        ( C E L A S 2 )'
        header_index = [i for i, x in enumerate(lines) if search_string in x]
        if header_index:
            for i, t in enumerate(header_index):
                # Get the current subcase.
                sc = int(lines[t - 2][117:120]) - first_case
                # Get the current page.
                page = int(lines[t - 4][122:128]) + 1
                # Loop over the rows in this page and grab the celas2 forces.
                for e in range(t + 3, page_index[page - 1]):
                    line_length = len(lines[e])
                    columns = [0, 31, 64, 97]
                    strips = [5, 38, 71, 104]
                    for j, column in enumerate(columns):
                        s = strips[j]
                        if line_length > column:
                            element = int(lines[e][s:s+8])
                            if element not in self.celas2_forces.keys():
                                self.celas2_forces[element] = np.zeros([n_sc])
                                self.celas2_elements.append(element)
                            self.celas2_forces[element][sc] = float(lines[e][s+13:s+26])

    def plot(self, **kwargs):
        """Method to use matrix_plot to plot the loads.
            Ex: f06.plot('cbar 1 ax')
            Ex: f06.plot('cbar 1 ax', title='my title')
            Ex: f06.plot(y=['cbar 662607 ax', 'cbar 661114 ax'], title='my title')
        """

        from PyLnD.utilities.matrix_plot import matrix_plot

        # Get the kwargs
        if 'y' in kwargs.keys():
            y = kwargs['y']
            if type(y) is not list:
                y = [y]
        else:
            raise Exception("You must supply at least a y: f06.plot(y='cbar 1 ax'")
        y2 = None
        if 'y2' in kwargs.keys():
            y2 = kwargs['y2']
            if type(y2) is not list:
                y2 = [y2]
        if 'title' in kwargs.keys():
            title = kwargs['title']
        else:
            title = self.file

        # Setup plot items
        xlabel = 'time steps'

        # Parse the y request
        [y, ylabel, ylegend] = self.y_parse(y)

        # Parse the y2 request
        if y2 is not None:
            [y2, y2label, y2legend] = self.y_parse(y2)
            matrix_plot(y=y, ylabel=ylabel, xlabel=xlabel, ylegend=ylegend, title=title, y2=y2, y2label=y2label,
                        y2legend=y2legend)
        else:
            # Plot the data
            matrix_plot(y=y, ylabel=ylabel, xlabel=xlabel, ylegend=ylegend, title=title)

    def y_parse(self, vin):
        """Method to parse the y request"""

        # Determine what is to be plotted
        v_str_list = vin
        difference = False
        if '-' in v_str_list[0]:
            difference = True
        # Check for any m
        v = None
        vlabel = []
        vlegend = []
        for i, item in enumerate(v_str_list):
            item_split = item.split()
            if len(item_split) < 2:
                raise Exception("You must supply 3 parameters: f06.plot(y2='cbar 1 ax'): {0}".format(item))
            item_type = item_split[0]
            try:
                item_dof = item_split[2]
                plot_column = self.dof_names[item_dof][0]
                if difference:
                    item_dof2 = item_split[-1]
                    plot_column2 = self.dof_names[item_dof2][0]
            except IndexError:
                item_dof = 'degF'
                plot_column = 0
            if item_type.lower() == 'cbar':
                element = int(item_split[1])
                if element not in self.bar_elements:
                    raise Exception('cbar {0} is not in {1}'.format(element, self.file))
                new_v = self.bar_forces[element][:, plot_column]
                if i == 0:
                    v = np.zeros([len(new_v), len(v_str_list)])
                v[:, i] = new_v
                vlabel.append(self.dof_names[item_dof.lower()][1])
                vlegend.append('CBAR {0} {1}'.format(element, item_dof.upper()))
            elif item_type.lower() == 'cbeam':
                element = int(item_split[1])
                if element not in self.beam_elements:
                    raise Exception('cbeam {0} is not in {1}'.format(element, self.file))
                new_v = self.beam_forces[element][:, plot_column]
                if i == 0:
                    v = np.zeros([len(new_v), len(v_str_list)])
                v[:, i] = new_v
                vlabel.append(self.dof_names[item_dof.lower()][1])
                vlegend.append('CBEAM {0} {1}'.format(element, item_dof.upper()))
            elif item_type.lower() == 'celas2':
                element = int(item_split[1])
                if element not in self.celas2_elements:
                    raise Exception('celas2 {0} is not in {1}'.format(element, self.file))
                new_v = self.celas2_forces[element]
                if difference:
                    element2 = int(item_split[5])
                    new_v2 = self.celas2_forces[element2]
                    new_v = new_v - new_v2
                    vlegend.append(vin[0])
                else:
                    vlegend.append('CELAS2 {0} {1}'.format(element, item_dof.upper()))
                if i == 0:
                    v = np.zeros([len(new_v), len(v_str_list)])
                v[:, i] = new_v
                vlabel.append(self.dof_names[item_dof.lower()][1])
            elif item_type.lower() == 'temp':
                element = int(item_split[1])
                if element not in self.inc.elements:
                    raise Exception('temp {0} is not in {1}'.format(element, self.inc.name))
                new_v = np.transpose(self.inc.inc[self.inc.elements == element, :])
                if i == 0:
                    v = np.zeros([len(new_v), len(v_str_list)])
                v[:, i] = new_v[:, 0]
                vlabel.append('degF')
                vlegend.append('TEMP {0}'.format(element))
            else:
                raise Exception('You must supply a element type for each entry: {0}'.format(item))
        # Combine ylabels if different
        vlabel = ' or '.join(set(vlabel))

        return v, vlabel, vlegend

    def load_temps(self, incfile):
        """Method to load an inc object"""

        from PyLnD.thermal.inc import INC
        self.inc = INC(incfile)


if __name__ == '__main__':
    # f06 = F06(file='s0run_841020902.f06', outreqs=['cbar_forces', 'cbeam_forces'])
    # f06.plot(y='cbar 662607 ax', title='bogus stuff')
    # f06.plot(y=['cbar 662607 ax', 'cbar 661114 tor'], title='bogus stuff')
    # f06.plot(y='cbar 662607 ax', y2='cbar 661114 tor', title='bogus stuff')
    # f06.load_temps('beams_s0_841020902.inc')
    # f06.plot(y='cbar 662607 ax', y2='temp 662607', title='bogus stuff')
    # f06.plot(y=['cbar 662607 ax', 'cbar 661114 mb2', 'cbar 662607 ma2'], y2=['temp 662607', 'temp 661114'],
    # title='bogus stuff')
    # cbeam
    # f06 = F06(file='p1run_841020902.f06', outreqs=['cbar_forces', 'cbeam_forces'])
    # f06.load_temps('beams_p1_841020902.inc')
    # f06.plot(y=['cbeam 616000 tor', 'cbeam 616000 ma1', 'cbar 615150 tor'], y2=['temp 616000'], title='bogus stuff')
    # celas2
    # f06 = F06(file='s3run_841002252.f06', outreqs=['cbar_forces', 'cbeam_forces', 'celas2_forces'])
    # f06.load_temps('beams_s3_841002252.inc')
    # f06.plot(y=['celas2 625507 for', 'celas2 625519 for'], y2=['temp 623566', 'temp 625531'],
    #          title='S3 TBA 7 mnvr novv')
    # trundle debug and diff implementation
    # f06 = F06(file='s3run_84200.f06', outreqs=['cbar_forces', 'cbeam_forces', 'celas2_forces'])
    # f06.load_temps('beams_s3_84200.inc')
    # f06.plot(y=['celas2 625507 for - celas2 625519 for'], y2=['temp 623566', 'temp 625531'],
    #          title='S3 TBA 7 stdyst novv')
    # celas2 test
    f06 = F06(file='s3run_84200.f06', outreqs=['cbar_forces', 'cbeam_forces', 'celas2_forces'])
    f06.load_temps('beams_s3_84200.inc')
    f06.plot(y=['celas2 625507 for', 'celas2 625519 for'], y2=['temp 623566', 'temp 625531'],
             title='S3 TBA 7 stdyst novv')
    pass