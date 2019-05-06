from PyLnD.loads.rf_functions import rf_mdof
from PyLnD.loads.pfile import modal_p
from PyLnD.loads.phi import PHI
from PyLnD.loads.hwlist import HWLIST
from PyLnD.loads.ltm import LTM
from PyLnD.loads.eig import EIG
from PyLnD.loads.pfile import PFILE
from pylab import *


class SCR:
    """Screening Class to do Modal Transient Analysis."""

    def __init__(self, name):
        """Initialize the SCR Object."""
        self.name = name
        self.phi = []
        self.hwlist = []
        self.ltm = []
        self.eig = []
        self.pfile = []
        self.zeta = []
        self.u = {}
        self.eta = {}
        self.time = {}

    def load_phi(self, **kwargs):
        """Method to load the Normal Modes Matrix (PHI) into the analysis.

        Procedure to load the f12 and corresponding f06.
          scr.load_phi(msf12='ms_xp93s1gl.f12', msf06='ms_xp93s1gl.f06')
        """
        msf12 = kwargs['msf12']
        msf06 = kwargs['msf06']

        self.phi = PHI(msf12, msf06)
        self.zeta = 0.01 * np.ones([self.phi.num_modes])

    def load_hwlist(self, **kwargs):
        """Method to load the Hardware List (HWLIST) into the analysis.

        Ex:  scr.load_hwlist(hwlist='xp_hwlist.xls')
        """
        hwlist = kwargs['hwlist']

        self.hwlist = HWLIST(hwlist)

    def load_ltm(self, **kwargs):
        """Method to load the LTM into the analysis.

        Ex:  scr.load_ltm(ltm='xp93zz_scr.pch)"""
        ltm = kwargs['ltm']

        self.ltm = LTM(ltm)
        self.ltm.label_ltm(self.hwlist)

    def load_eig(self, **kwargs):
        """Method to load the eigenvalue file into the analysis.

        Ex:  scr.load_eig(eig='xp93zz.eig')"""
        eig = kwargs['eig']

        self.eig = EIG(eig)

    def load_pfile(self, **kwargs):
        """Method to load the forcing function (PFILE) into the analysis.

        * Auto time step skips time steps that do not contribute above some threshold.

        Ex:  scr.load_pfile(pfile='ff_xp93s1sp0001.dat', filetype=['pfile' or 'matfile'])

        Ex:  Parse the text data into numbers.
            scr.pfile.parse_pfile(case=[1,100])

        Ex:  Sync and set the run to have a timestep of 0.01 sec.
            scr.pfile.sync(case=[1,100], tstep=0.01)

        Ex:  Sync and set the run to have an auto time step, defaults to 0.01 sec.
            scr.pfile.sync(case=76, auto='yes')

        Ex:  Sync and set the run to have an auto time step with the times were force exists = 0.02 sec
            scr.pfile.sync(case=76, auto='yes', tstep=0.02)

        """
        pfile = kwargs['pfile']
        filetype = kwargs['filetype']

        # Loads the pfile and finds the indices, still need to sync and parse.
        self.pfile = PFILE(pfile, filetype=filetype)
        # self.pfile.sync(tstep='auto')

    def load_zeta(self, **kwargs):
        """Method to load the damping file.

            Ex:  scr.load_zeta(damp='xp93s1/DAMPINGFILE')
        """
        dampfile = kwargs['damp']

        with open(dampfile) as f:
            for line in f:
                if line[0] != '$' and line[0] != 'i':
                    row = line.split()
                    row = list(map(float, row))
                    self.zeta[int(row[0] - 1)] = 0.01 * row[1]

    def save2mat(self, outfile):
        """Method to save the scr object to a Matlab mat file.

        Ex:  scr.save2mat('xp93zz/sc_xp93zzsp0001.mat')
        """
        from matlab.mat_utilities import save2mat
        from matlab.mat_utilities import tuple2list as t2l

        doflist = {'acron_dofs': t2l(self.ltm.acron_dofs)}
        outlist = [self.eta, self.u, self.time, doflist]
        keylist = ['eta', 'u', 'time', 'ltm']
        save2mat(key=keylist, olist=outlist, ofile=outfile)

    def plot_u(self, **kwargs):
        """Method to plot the response in the time domain.

            Ex:  Plot this dof for case 1 and 2, and label the window "u test"
            scr.plot_u(items=[(1, 'N1PN3', 'TOR'), (2, 'N1PN3', 'TOR')], desc='u test')
        """

        # Get the kwargs.
        items = kwargs['items']
        if type(items) is not list:
            items = [items]
        if 'desc' in kwargs.keys():
            desc = kwargs['desc']
        else:
            desc = ''

        # Loop and plot each requested dof.
        fig = figure()
        ax = subplot(111)
        for item in items:
            if item.__len__() != 3:
                raise Exception('!!! You must supply (case, acron, dof) to plot !!!')
            c = item[0]
            if c not in self.u.keys():
                raise Exception('!!! Case {0} is has not been run or does not exist !!!'.format(c))
            dof = (item[1], item[2])

            # Find the dof tuple in the acron_dof list or the dof list from the ltm object.
            if dof in self.ltm.acron_dofs:
                i_dof = self.ltm.acron_dofs.index(dof)
            elif dof in self.ltm.dofs:
                i_dof = self.ltm.dofs.index(dof)
            else:
                raise Exception("!!! DOF " + dof.__str__() + " not in LTM " + self.ltm.name)

            # Plot the requested time history.
            label = '({0}, {1}) case: {2}'.format(dof[0], dof[1], c)
            ax.plot(self.time[c], self.u[c][i_dof, :], label=label)
        ax.legend()
        title('Response of FF: %s' % (self.pfile.name))
        xlabel('Time (s)')
        fig.canvas.set_window_title('{0} {1}'.format(self.name, desc))
        show()

    def plot_eta(self, **kwargs):
        """Method to plot the modal displacements.

        Ex:  Plot mode 7 for case 1 and case 100, and label the window "eta sp0001".
            scr.plot_eta(items=[(1, 7), (100, 7)], desc='eta sp0001')
        """

        # Get the kwargs.
        items = kwargs['items']
        if type(items) is not list:
            items = [items]
        if 'desc' in kwargs.keys():
            desc = kwargs['desc']
        else:
            desc = ''

        fig = plt.figure()
        ax = plt.subplot(111)
        for item in items:
            c = item[0]
            mode = item[1]
            if mode > self.phi.num_modes:
                raise Exception("!!! Only %s modes in analysis !!!" % self.phi.num_modes.__str__())

            # Plot the requested modal displacement.
            label = 'Mode {0} case: {1}'.format(mode, c)
            ax.plot(self.time[c], self.eta[c][mode - 1, :], label=label)
        ax.legend()
        plt.title('Modal Response of FF: %s' % self.pfile.name)
        plt.xlabel('Time (s)')
        fig.canvas.set_window_title('{0} {1}'.format(self.name, desc))
        plt.show()

    def amx(self, **kwargs):
        """Method to find the max/mins for one or all output DOF.\n
            Ex:  Find the max/mins and times for this DOF in case 1.
                scr.amx(item=(1, 'N2LAB', 'TOR'))
        """

        # Determine the keyword arguments.
        if 'item' in kwargs.keys():
            item = kwargs['item']
            if not type(item) is tuple:
                raise Exception('Requested dof {0} is not a tuple (case, "acron", "dof").'.format(dof))
            dof = (item[1], item[2])
            case = item[0]
        else:
            raise Exception('You must request a dof:  scr.amx(item=(case, "acron", "dof")).')

        # Determine the location of the requested dof.
        loc = [x for x, y in enumerate(self.ltm.acron_dofs) if y == dof][0]

        # Determine the max/min and the time at which they occurred.
        dof_res = self.u[case][loc, :]
        max_val = np.max(dof_res)
        min_val = np.min(dof_res)
        max_loc = np.argmax(dof_res)
        min_loc = np.argmin(dof_res)
        max_time = self.time[case][max_loc]
        min_time = self.time[case][min_loc]

        # Print to the screen.
        print('Case {0}- \t{1}\tMax: {2:.4f} (@ {3:.4f} sec)\tMin: {4:.4f} (@ {5:.4f} sec)\n'.format(
            case, dof, max_val, max_time, min_val, min_time
        ))

    def fft(self, **kwargs):
        """Method to perform fft on a signal.

            Ex:  Plot fft of several responses.
                scr.fft(u_out=[(1, 'SSSIEA', 'FX'), (1, 'SSSIEA', 'FY')])

            Ex:  Plot fft of several applied forces.
                scr.fft(f_in=[(1, 100012, 1), (1, 100012, 2), (1, 100012, 3)])
        """
        from PyLnD.loads.freq_domain import FFT

        u_out = []
        f_in = []
        # Obtain the keyword arguments.
        if 'u_out' in kwargs.keys():
            u_out = kwargs['u_out']
            if type(u_out) is not list:
                u_out = [u_out]
        if 'f_in' in kwargs.keys():
            f_in = kwargs['f_in']
            if type(f_in) is not list:
                f_in = [f_in]
        if 'desc' in kwargs.keys():
            desc = kwargs['desc']
        else:
            desc = ''

        # Loop, perform fft, and plot each requested response.
        if u_out:
            for resp in u_out:
                if resp.__len__() != 3:
                    raise Exception('!!! You must supply (case, acron, dof) to plot !!!')
                c = resp[0]
                if c not in self.u.keys():
                    raise Exception('!!! Case {0} is has not been run or does not exist !!!'.format(c))
                dof = (resp[1], resp[2])

                # Find the dof tuple in the acron_dof list or the dof list from the ltm object.
                if dof in self.ltm.acron_dofs:
                    i_dof = self.ltm.acron_dofs.index(dof)
                elif dof in self.ltm.dofs:
                    i_dof = self.ltm.dofs.index(dof)
                else:
                    raise Exception("!!! DOF " + dof.__str__() + " not in LTM " + self.ltm.name)

                # Create FFT object.
                u_fft = FFT(resp, x=self.u[c][i_dof, :], time=self.time[c])

                # Plot the requested response fft.
                fig = plt.figure(1)
                u_fft.plot_fft()

        for load in f_in:
            if load.__len__() != 3:
                raise Exception('!!! You must supply (case, acron, dof) to plot !!!')
            c = load[0]
            if c not in self.u.keys():
                raise Exception('!!! Case {0} is has not been run or does not exist !!!'.format(c))
            grid_id = load[1]
            dir = load[2]

            # Create FFT object.
            p_fft = FFT(load, x=self.pfile.case[c][grid_id][:, dir], time=self.pfile.case[c][grid_id][:, 0])

            # Plot the requested response fft.
            p_fft.plot_fft()

    def rss(self, case):
        """Method to RSS responses as dictated by the HWLIST.

            Ex:  Perform the rss on case 1.
                scr.rss(1)
        """

        # Loop over each HWLIST RSS items, determine if available in the LTM, perform RSS on u.
        for item in self.hwlist.hw_rss:
            acron = item[0]
            eid = item[1]
            dof = item[2]
            rss_list = []
            rss_idx = []
            rss_dofs = []
            if acron in self.hwlist.hw.keys():
                if eid in self.hwlist.hw[acron].keys():
                    if dof in self.hwlist.hw[acron][eid].keys():
                        rss_dofs.append((acron, dof))
                        for d in self.hwlist.hw[acron][eid][dof]['dofs']:
                            eid_d = (eid, d)
                            rss_list.append(eid_d)
                            if eid_d in self.ltm.dofs:
                                rss_idx.append(self.ltm.dofs.index(eid_d))
                            else:
                                raise Exception('Missing {0} in {1} and {2} in ltm.'.format(eid_d, acron, dof))
                        rss_sum = np.zeros_like(self.u[case][0, :])
                        for idx in rss_idx:
                            rss_sum = rss_sum + np.square(self.u[case][idx, :])
                        rss = np.sqrt(rss_sum)
                        # Add the RSS to the u and ltm.acron_dof.
                        self.ltm.acron_dofs.append((acron, dof))
                        self.u[case] = np.vstack([self.u[case], rss])

    def run(self, **kwargs):
        """Method to perform numerical integration of EOM via Recurrence Formulas.

            Ex:  Run case 1 and 2.
                scr.run(case=[1, 2])

            Ex:  Run all cases.
                scr.run(case='all')
        """

        # Get the kwargs.
        cases = kwargs['case']
        if cases == 'all':
            cases = scr.pfile.case.keys()
        elif type(cases) is not list:
            cases = [cases]
        if 'rbm' in kwargs.keys():
            if kwargs['rbm'].lower() == 'yes':
                rbm = 1
            else:
                rbm = 0
        else:
            rbm = 0

        # Run all the requested cases.
        for c in cases:
            # Create the current case dictionary key.
            if c not in self.time.keys():
                self.time[c] = []
            if c not in self.u.keys():
                self.u[c] = []
            if c not in self.eta.keys():
                self.eta[c] = []

            # Determine the modal force vector.
            p_modal = modal_p(self.pfile.case[c], self.phi)

            # Determine the time parameters in the forcing function.
            grid = self.pfile.case[c]['grids'][0]
            self.time[c] = self.pfile.case[c][grid][:, 0]
            dt = self.pfile.case[c]['dt']

            # Add 100 seconds at the end of the forcing function for ring down.
            add_time = [(20, 0.01), (80, 0.5)]
            for at in add_time:
                new_time = np.arange(self.time[c][-1] + dt, self.time[c][-1] + at[0], at[1])
                self.time[c] = np.append(self.time[c], new_time)
                new_p_modal = np.zeros([self.phi.num_modes, new_time.size])
                p_modal = np.append(p_modal, new_p_modal, axis=1)

            # Integrate the modal EOM using Reccurence Formulas:
            #   etadd + 2 * zeta omn * etad + omn**2 * eta = P
            eta0 = np.zeros_like(p_modal)
            etad0 = np.zeros_like(p_modal)
            [self.eta[c], etad] = rf_mdof(self.time[c], p_modal, self.eig.eigenvalues,
                                          np.multiply(2 * np.pi, self.eig.frequency), self.zeta,
                                          eta0, etad0)

            # Remove rigid body modes unless requested not to.
            if rbm == 0:
                self.eta[c][0:6, :] = 0.0

            # Recover the desired responses with superposition of modes using the LTM
            self.u[c] = self.ltm.dtm @ self.eta[c]

            # Perform the required RSS set out in the HWLIST.
            self.rss(c)
