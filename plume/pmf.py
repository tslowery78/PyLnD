import numpy as np
from scipy.interpolate import interp1d
from PyLnD.loads.pfile import auto_ts


class PMF:
    """Class of object that represents a plume modal force time history."""

    def __init__(self, **kwargs):
        """Method to initialize the PMF class."""

        # Get the kwargs
        if 'jfh' in kwargs.keys():
            self.jfh_file = kwargs['jfh']
        else:
            raise Exception('!!! You must specify a jfh file !!!')
        if 'pmf' in kwargs.keys():
            self.mf_file = kwargs['pmf']
        else:
            raise Exception('!!! You must specify a pmf file. !!!')
        if 'auto' in kwargs.keys():
            self.auto = True
        else:
            self.auto = False
        if 'tstep' in kwargs.keys():
            self.dt = kwargs['tstep']
        else:
            self.dt = 0.01
        if 'tol' in kwargs.keys():
            self.tol = kwargs['tol']
        else:
            self.tol = 0.1   # default to 0.1 of lbs change in load minimum.
        if 'ring' in kwargs.keys():
            self.ring = kwargs['ring']
        else:
            self.ring = 2.0  # default to 2 sec of ring up/down around pick-back-up times.

        # Initialize the attributes.
        self.pw = []
        self.on_time = []
        self.pmf = []
        self.pmf_raw = []
        self.n_rec = 0
        self.n_modes = 0
        self.time = []
        self.time_raw = []

        # Read the JFH and PMF
        self.read_jfh()
        self.read_mf()

        # Create the pmf time history.
        self.time_hist()

    def read_jfh(self):
        """Method to load the jfh for pmf timing.

            Ex:  PMF.read_jfh()
        """

        # Open the jfh and read the pulse width and the on-times.
        with open(self.jfh_file) as f:
            for line in f:
                l_split = line.split()
                pw = float(l_split[1])
                on_time = float(l_split[2])
                self.pw.append(pw)
                self.on_time.append(on_time)

    def read_mf(self):
        """Method to read the modal force file.

            Ex:  PMF.read_mf()
        """

        # Open the pmf binary file and read.
        with open(self.mf_file) as f:
            [br1] = np.fromfile(f, dtype=np.int32, count=1)
            [n_rec, n_modes] = np.fromfile(f, dtype=np.int32, count=2)
            self.n_rec = n_rec
            self.n_modes = n_modes
            # Allocate the modal force array
            self.pmf = np.zeros([n_modes, n_rec])
            [br2] = np.fromfile(f, dtype=np.int32, count=1)
            for i in range(0, n_rec):
                [br3] = np.fromfile(f, dtype=np.int32, count=1)
                [n_modes] = np.fromfile(f, dtype=np.int32, count=1)
                self.pmf[:, i] = np.fromfile(f, dtype=np.float32, count=n_modes)
                [br4] = np.fromfile(f, dtype=np.int32, count=1)

    def time_hist(self):
        """Method to create a pmf time history.

            Ex:  PMF.time_hist()
        """

        # Setup expanded matrices ahead of time.
        new_time = np.zeros([4 * self.n_rec])
        new_n_rec = 4 * self.n_rec
        new_pmf = np.zeros([self.n_modes, new_n_rec])
        zero_column = np.zeros([1, self.n_modes])
        nan_column = np.empty([1, self.n_modes])
        nan_column = np.nan

        # Loop over each record and insert zero or nan column.
        step_down = 0.001
        last_off = 0.0
        next_on = 0.0
        for o, on_time in enumerate(self.on_time):
            i = 4 * o
            if o == self.on_time.__len__() - 1:
                next_on = 0.0
            else:
                next_on = self.on_time[o + 1]
            lhs = i
            lhs_time = on_time - step_down
            on_pt = i + 1
            off_pt = i + 2
            off_time = on_time + self.pw[o]
            rhs = i + 3
            rhs_time = off_time + step_down
            new_time[lhs] = lhs_time
            new_time[on_pt] = on_time
            new_time[off_pt] = off_time
            new_time[rhs] = rhs_time

            # Logic to incorporate adjacent pulses.
            if lhs_time < last_off:
                new_pmf[:, lhs] = nan_column
            else:
                new_pmf[:, lhs] = zero_column
            new_pmf[:, on_pt] = self.pmf[:, o]
            new_pmf[:, off_pt] = self.pmf[:, o]
            if rhs_time > next_on:
                new_pmf[:, rhs] = nan_column
                last_off = off_time
            else:
                new_pmf[:, rhs] = zero_column
                last_off = rhs_time

        # Remove the nan columns from the time history.
        self.time_raw = new_time[~np.all(np.isnan(new_pmf), axis=0)]
        self.pmf_raw = new_pmf[:, ~np.all(np.isnan(new_pmf), axis=0)]

        # Interpolate each dof
        min_time = np.min(self.time_raw)
        max_time = np.max(self.time_raw)
        nmodes = new_pmf[:, 0].__len__()
        full_time = np.arange(min_time, max_time, self.dt)
        # Add in the raw times to capture the square wave pulses.
        cat_time = np.unique(np.sort(np.concatenate((self.time_raw, full_time)), axis=0))
        new_time = np.zeros([cat_time.__len__() + 1, 1])
        interp_pmf = np.zeros([nmodes, cat_time.__len__() + 1])
        # Add additional time step to ensure new_vec ends at zero load.
        new_time[0:-1, 0] = cat_time
        new_time[-1, 0] = cat_time[-1] + self.dt
        for d in range(0, nmodes):
            interp_f = interp1d(self.time_raw, self.pmf_raw[d, :])
            interp_pmf[d, 0:-1] = interp_f(cat_time)
        self.time = new_time
        self.pmf = interp_pmf

        # For auto time step, determine the index of the time steps to be kept.
        if self.auto:
            p_sum = np.sum(np.absolute(self.pmf), axis=0)
            keep_list = auto_ts(self.time, p_sum, self.tol, self.ring)
            pmf = np.zeros([self.n_modes, keep_list.__len__()])
            for m in range(0, self.n_modes):
                pmf[m, :] = self.pmf[m, keep_list]
            self.time = self.time[keep_list]
            self.pmf = pmf
