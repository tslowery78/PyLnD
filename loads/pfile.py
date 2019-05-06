import numpy as np
from scipy.interpolate import interp1d
import re


class PFILE:
    """Forcing function class for screening code."""

    def __init__(self, name, **kwargs):
        """Initializing the PFILE object."""
        if 'filetype' not in kwargs.keys():
            raise Exception("!!! filetype must be specified !!!")
        else:
            filetype = kwargs['filetype']

        self.name = name
        self.pf_lines = []
        self.case = {}
        if filetype == 'pfile':
            self.load_pfile()
        elif filetype == 'matfile':
            self.read_matfile()

    def save2mat(self, outfile):
        """Method to save the pfile to a Matlab mat file.

            Ex:  PFILE.save2mat(key='pfile', olist=self.case, ofile=outfile)
        """
        from PyLnD.matlab.mat_utilities import save2mat

        save2mat(key='pfile', olist=self.case, ofile=outfile)

    def plot_p(self, **kwargs):
        """Method to plot the forcing function time domain.

            Ex:  Plot case 1 and 100 for two different DOF.
                pfile.plot_p(items=[(1, 100012, 1), (100, 110162, 1)], desc='testing sp0001')
        """
        import matplotlib.pyplot as plt

        # Get the kwargs.
        items = kwargs['items']
        if type(items) is not list:
            items = [items]
        if 'desc' in kwargs.keys():
            desc = kwargs['desc']
        else:
            desc = ''

        # Loop and plot each requested dof.
        fig = plt.figure()
        ax = plt.subplot(111)
        for item in items:
            if item.__len__() != 3:
                raise Exception('!!! You must supply (case, grid, dof) to plot !!!')
            c = item[0]
            grid = item[1]
            d = item[2]
            label = '({0}, {1}) case: {2}'.format(grid, d, c)
            # Plot the requested time history.
            if grid in self.case[c].keys():
                time = self.case[c][grid][:, 0]
                ax.plot(time, self.case[c][grid][:, d], label=label)
            else:
                plt.close(fig)
                raise Exception('!!! Grid %s is not in Case %s !!!' % (grid, c))
        ax.legend()
        plt.title('FF Time History: %s' % self.name)
        plt.xlabel('Time (s)')
        plt.show()
        fig.canvas.set_window_title('{0} {1}'.format(self.name, desc))

    def read_matfile(self):
        """Method to read a forcing function from a Matlab mat file.

            Ex:  PFILE.read_matfile()
        """
        from matlab.mat_utilities import readmat

        # Load the mat variables into
        f_dicts = readmat(self.name)

        if 'pfile' not in f_dicts.keys():
            raise Exception('!!! PFILE not one of the types in the {0}'.format(self.name))
        else:
            self.case = f_dicts['pfile']

        # Add the list of grids in case this is user created matfile.
        for case in self.case.keys():
            for k in self.case[case].keys():
                if k != 'grids' and k != 'loc':
                    if 'grids' not in self.case[case].keys():
                        self.case[case]['grids'] = []
                    else:
                        self.case[case]['grids'].append(k)

        # Check that each forcing function has 7 columns, t, x, y, z, mx, my, mz
        for case in self.case.keys():
            for g in self.case[case]['grids']:
                shape = self.case[case][g].shape
                if shape[1] != 7:
                    raise Exception('!!! You must specified 7 columns in your ff: [t, x, y, z, mx, my, mz] {0}'
                                    .format(self.name))

    def sync(self, **kwargs):
        """Method to interpolate and sync each applied load time to each other per case.

        Ex:  Sync and set the run to have a timestep of 0.01 sec.
            pfile.sync(case=[1,100], tstep=0.01)

        Ex:  Sync and set the run to have an auto time step, defaults to 0.01 sec.
            pfile.sync(case=76, auto='yes')

        Ex:  Sync and set the run to have an auto time step with the times were force exists = 0.02 sec
            pfile.sync(case=76, auto='yes', tstep=0.02)

        """

        # Find the keyword arguments.
        auto = False
        if 'tstep' in kwargs.keys():
            dt = kwargs['tstep']
        else:
            dt = 0.01   # Default to a 100 Hz signal.
        if 'tol' in kwargs.keys():
            tol = kwargs['tol']
        else:
            tol = 0.01   # default to 0.01 of lbs change in load minimum.
        if 'ring' in kwargs.keys():
            ring = kwargs['ring']
        else:
            ring = 2.0  # default to 2 sec of ring up/down around pick-back-up times.
        if 'case' in kwargs.keys():
            case_list = kwargs['case']
            if case_list == 'all':
                case_list = list(self.case.keys())
            elif type(case_list) is not list:
                case_list = [case_list]
        else:
            raise Exception('!!! You must supply a case !!!')
        if 'auto' in kwargs.keys():
            auto = True
        else:
            auto = False

        # Loop over each case in the case_list and sync.
        for c in case_list:
            # Determine the max and min times for all grids in this case.
            self.case[c]['dt'] = dt
            min_time = 1e6
            max_time = -1e6
            g = 0
            for g in self.case[c]['grids']:
                # Check if the case has been parsed.
                if type(self.case[c][g]) is list:
                    raise Exception("!!! This case {0} must be parsed first !!!".format(c))
                min_t = np.min(self.case[c][g][:, 0], axis=0)
                if min_t < min_time:
                    min_time = min_t
                max_t = np.max(self.case[c][g][:, 0], axis=0)
                if max_t > max_time:
                    max_time = max_t

            # Add extra rows to the data to extend each history to match max/min times and interpolate.
            for g in self.case[c]['grids']:
                l = self.case[c][g].__len__()
                if self.case[c][g][0, 0] > min_time:
                    new_time = [self.case[c][g][0, 0] - dt]
                    if new_time > min_time:
                        new_time.append(min_time)
                        self.case[c][g] = np.insert(self.case[c][g], [l, l], 0, axis=0)
                        self.case[c][g][0:1, 0] = new_time
                    else:
                        self.case[c][g] = np.insert(self.case[c][g], l, 0, axis=0)
                        self.case[c][g][0, 0] = new_time
                if self.case[c][g][-1, 0] < max_time:
                    ext_time = [self.case[c][g][-1, 0] + dt]
                    if ext_time < max_time:
                        ext_time.append(max_time)
                        self.case[c][g] = np.insert(self.case[c][g], [l, l], 0, axis=0)
                        self.case[c][g][l:, 0] = ext_time
                    else:
                        self.case[c][g] = np.insert(self.case[c][g], l, 0, axis=0)
                        self.case[c][g][l, 0] = ext_time

                # Interpolate each dof
                full_time = np.arange(min_time, max_time, dt)
                new_vec = np.zeros([full_time.__len__() + 1, 7])
                new_vec[0:-1, 0] = full_time
                new_vec[-1, 0] = full_time[-1] + dt     # Add additional time step to ensure new_vec ends at zero load.
                for d in range(1, 7):
                    interp_f = interp1d(self.case[c][g][:, 0], self.case[c][g][:, d])
                    new_vec[0:-1, d] = interp_f(full_time)
                self.case[c][g] = new_vec

            # Sync up the duplicate grid blocks into one final vector for that grid.
            to_remove = []
            for g in self.case[c]['grids']:
                if type(g) is str:
                    g_split = g.split('_')
                    d_grid = int(g_split[0])
                    self.case[c][d_grid][:, 1:] = self.case[c][d_grid][:, 1:] + self.case[c][g][:, 1:]
                    to_remove.append(g)
            for g in to_remove:
                self.case[c].pop(g, None)
                self.case[c]['grids'].remove(g)

            # For auto time step, determine the index of the time steps to be kept.
            if auto:
                p_sum = []
                # Sum the forces in all directions at each time step and accumulate for each grid
                for g in self.case[c]['grids']:
                    if type(p_sum) is list:
                        p_sum = np.zeros_like(self.case[c][g][:, 0])
                    p_sum = p_sum + np.sum(np.absolute(self.case[c][g][:, 1:]), axis=1)
                keep_list = auto_ts(self.case[c][g][:, 0], p_sum, tol, ring)
                for g in self.case[c]['grids']:
                    self.case[c][g] = self.case[c][g][keep_list, :]

    def load_pfile(self):
        """Method to load the contents of PFILE and index for later.

            Ex:  PFILE.load_pfile()
        """

        # Read the file contents.
        with open(self.name) as f:
            self.pf_lines = f.readlines()

        # Go line by line, construct ff dict.
        i = 1
        for j, line in enumerate(self.pf_lines):
            if line[2:7].lower() == 'case=':
                try:
                    case_num = int(line[7:11])
                except:
                    raise Exception('Could not convert "{0}" in file {1} line {2}\n{3} '
                                    .format(line[7:11], self.name, j + 1, line))
                i = 1
                if case_num not in self.case.keys():
                    self.case[case_num] = {}
                    if 'loc' not in self.case[case_num]:
                        self.case[case_num]['loc'] = j
                        self.case[case_num]['grids'] = []
                        self.case[case_num]['dt'] = 0

            if line[2:6].lower() == 'grid':
                grid = int(line[7:15])
                if grid in self.case[case_num]['grids']:
                    grid = grid.__str__() + '_' + i.__str__()
                    self.case[case_num]['grids'].append(grid)
                    i += 1
                else:
                    self.case[case_num]['grids'].append(grid)
                if grid not in self.case[case_num].keys():
                    self.case[case_num][grid] = []

    def parse_pfile(self, **kwargs):
        """Method to parse a case in the pfile string into real data.

            Ex:  Parse the text data into numbers.
                scr.pfile.parse_pfile(case=[1,100])
        """

        # Get the keyword arguments.
        if 'case' in kwargs.keys():
            case_list = kwargs['case']
            if case_list == 'all':
                case_list = list(self.case.keys())
            elif type(case_list) is not list:
                case_list = [case_list]
        else:
            raise Exception('!!! You must supply a case !!!')

        # Loop over the collection of a cases to parse.
        for case_num in case_list:
            # Parse the section of the pfile for this case.
            ng = self.case[case_num]['grids'].__len__()
            g = 0
            l = self.case[case_num]['loc']
            while g < ng:
                line = self.pf_lines[l]
                if line[2:6].lower() == 'grid':
                    data = np.empty((0, 2))
                    grid = int(line[7:15])
                    fx = float(line[19:26])
                    fy = float(line[36:43])
                    fz = float(line[53:60])
                    l += 1
                    line = self.pf_lines[l]
                    mx = float(line[19:26])
                    my = float(line[36:43])
                    mz = float(line[53:60])
                    # Loop over the grid entry for this case.
                    dollar = False
                    # while line[0] != '$':
                    while not dollar:
                        l += 1
                        if l == self.pf_lines.__len__():
                            dollar = True
                            continue
                        line = self.pf_lines[l]
                        if line[0] == '$':
                            dollar = True
                            l -= 1
                            continue
                        line = line.rstrip()
                        line_chunk = [line[i:i + 8] for i in range(0, len(line), 8)]  # chunk up in 8-char segments
                        line_chunk = [i for i in line_chunk if "        " not in i]  # Remove empty first field.
                        line_chunk = [x.strip(' ') for x in line_chunk]  # Remove all spaces
                        line_chunk = [i.replace('-', 'e-') for i in line_chunk]  # Add the exponent at the end
                        line_chunk = [re.sub('^e', '', i) for i in line_chunk]
                        try:
                            line_data = list(map(float, line_chunk))  # Convert the strings to floats
                        except:
                            raise Exception('Could not convert part of case {0} line {1} to a float:\n\t\t{2}\n{3}'
                                            .format(case_num, l + 1, self.name, line))
                        new_times = np.asarray(line_data[0::2])  # Pull just the time columns
                        new_loads = np.asarray(line_data[1::2])  # Pull just the value columns
                        new_data = np.array([new_times, new_loads]).transpose()
                        data = np.append(data, new_data, axis=0)
                        pass
                    # Create a full vector using the coefficients.
                    p_vec = np.zeros([data.shape[0], 7])
                    p_vec[:, 0] = data[:, 0]  # time
                    p_vec[:, 1] = fx * data[:, 1]  # fx
                    p_vec[:, 2] = fy * data[:, 1]  # fy
                    p_vec[:, 3] = fz * data[:, 1]  # fz
                    p_vec[:, 4] = mx * data[:, 1]  # mx
                    p_vec[:, 5] = my * data[:, 1]  # my
                    p_vec[:, 6] = mz * data[:, 1]  # mz
                    self.case[case_num][self.case[case_num]['grids'][g]] = p_vec
                    g += 1
                l += 1


def auto_ts(time, vec, tol, ring):
    """Function to minimize time steps.
        inputs: time
                vec
                tol (difference in vec for auto cut outs)
                ring (amount before and after to keep in seconds)
        outputs: f_index (index of data points to remove)
    """

    # Assuming dt is uniform for all time steps.
    dt = time[1] - time[0]

    # Determine the ring up/down number of points.
    nk = int(ring/dt)

    # Setup an index of the original vector.
    index = np.arange(0, time.size, 1)

    # Determine the first non-zero element and delete all but the
    #  first point and the point before the first non-zero point.
    i_non_zero = np.nonzero(vec)[0][0]
    time = np.delete(time, np.s_[1:i_non_zero-1:1], 0)
    vec = np.delete(vec, np.s_[1:i_non_zero - 1:1], 0)
    index = np.delete(index, np.s_[1:i_non_zero - 1:1], 0)

    # Keep only indices that have a change in vec greater than tol and
    #  keep the indices nk indices in both directions around each change in vec.
    dv = np.absolute(vec[0:-1] - vec[1:])
    dv = np.append(dv, 0)
    k_index = index[dv > tol, ]
    k_index = k_index[:, np.newaxis]
    to_keep = np.tile(np.arange(-nk, nk, 1), (k_index.size, 1))
    f_index = k_index + to_keep
    f_index = np.unique(f_index)
    f_index = f_index[(f_index >= index[1]) & (f_index <= index[-1])]
    f_index = np.insert(f_index, 0, 0)

    return f_index


def modal_p(pfile, phi):
    """Method to find the modal load vector for a case.
        inputs: pfile <PFILE object (only one case)>
                phi <PHI object>
        outputs: p_modal <modal force vector>
    """

    # Define the forcing function, retaining only non-zero load vectors.
    applied_grids = pfile['grids']
    applied_dofs = []
    time = pfile[applied_grids[0]][:, 0]
    for grid in applied_grids:
        for i in range(0, 6):
            if np.abs(pfile[grid][:, i + 1].sum()) > 0.0:
                applied_dofs.append((grid, i + 1))
    ndof = applied_dofs.__len__()
    load = np.zeros([time.size, ndof])
    for i, d in enumerate(applied_dofs):
        load[:, i] = pfile[d[0]][:, d[1]]
    p = load.transpose()

    # Find the applied load dofs rows in the PHI matrix.
    phi_applied = np.zeros([ndof, phi.num_modes])
    for i, dof in enumerate(applied_dofs):
        i_dof = phi.dofs.index(dof)
        phi_applied[i, :] = phi.phi[i_dof, :]

    # Determine the modal force vector for each time step. P = PHI_T * p
    p_modal = phi_applied.transpose() @ p

    return p_modal
