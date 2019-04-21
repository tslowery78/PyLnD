import numpy as np
from scipy.interpolate import interp1d


class FFT():
    """Class of FFT of time domain."""

    def __init__(self, name, **kwargs):
        """Initializing FFT class."""
        self.name = name

        # Get input parameters.
        if 'time' in kwargs.keys():
            self.time = kwargs['time']
        else:
            raise Exception('!!! Must specify time vector !!!')
        if 'x' in kwargs.keys():
            self.x = kwargs['x']
        else:
            raise Exception('!!! Must specify signal array !!!')
        if 'xlim' in kwargs.keys():
            self.xlim = kwargs['xlim']
            if type(self.xlim) is not list:
                raise Exception("!!! Expecting xlim=[0, 10], a list !!!")
        else:
            self.xlim = []
        if 'df' in kwargs.keys():
            self.df = kwargs['df']
            if self.df == 'raw':
                self.df = 0
        else:
            self.df = 0.001      # Frequency resolution (Hz) target, not exact.
        if 'Fs' in kwargs.keys():
            self.Fs = kwargs['Fs']
        else:
            self.Fs = 100

        # Initialize the remaining.
        self.freq = 0
        self.X = 0
        self.F_Ny = self.Fs / 2
        self.N = 0
        self.T = 0
        self.t_min = 0
        self.t_max = 0

        # Perform the fft.
        self.fft()

    def fft(self):
        """Method to calculate the FFT of a signal.

            Ex:  fft.fft()
        """

        # Determine fft parameters.
        t = self.time
        x = self.x

        # Interpolate at the requested sampling frequency.
        dt = 1 / self.Fs                    # Time step (sec)
        t_interp = np.arange(t[0], t[-1], dt)
        x_interp = np.zeros(t_interp.shape[-1])
        interp_x = interp1d(t, x)
        x = interp_x(t_interp)
        t = t_interp

        # Truncate the time series if requested.
        if self.xlim:
            index = (t <= self.xlim[1]) & (t >= self.xlim[0])
            t = t[index]
            p = p[index]
        N_orig = t.shape[-1]
        T_orig = t[-1]
        self.t_max = t[-1]
        self.t_min = t[0]

        # Repeat the signal as many times needed to achieve desired df.
        if self.df > 0:
            T_req = 1 / self.df
            n_repeat = int(T_req / T_orig)
            x = np.tile(x, n_repeat)
            N = x.shape[-1]
            t = np.arange(N) * dt + t[0]
            T = t[-1]
        else:
            N = N_orig
            T = T_orig

        # Construct a frequency series based on the number of points.
        f = self.Fs * np.fft.fftfreq(N)

        # Calculate the fft and scale.
        X = 2 * np.fft.fft(x) / N

        # Set object attributes.
        self.freq = f
        self.time = t
        self.x = x
        self.X = X
        self.df = f[1] - f[0]
        self.N = N
        self.T = T

    def plot_fft(self, **kwargs):
        """Method to plot the FFT and time history.

            Ex:  fft.plot_fft(flim=[0, 10], tlim=[0, 100])
        """
        import matplotlib.pyplot as plt

        # Get the input parameters
        if 'flim' in kwargs.keys():
            flim = kwargs['flim']
            if type(flim) is not list:
                raise Exception("!!! Expecting flim=[0, 10], a list !!!")
        else:
            flim = [0, 10]
        if 'tlim' in kwargs.keys():
            tlim = kwargs['tlim']
            if type(tlim) is not list:
                raise Exception("!!! Expecting tlim=[0, 10], a list !!!")
        else:
            tlim = [self.t_min, self.t_max]

        # Plot the fft and time history on two panel figure.
        plt.figure(1)
        plt.subplot(211)
        plt.plot(self.freq, np.abs(self.X))
        if flim:
            plt.xlim(flim[0], flim[1])
        plt.subplot(212)
        plt.plot(self.time, self.x)
        if tlim:
            plt.xlim(tlim[0], tlim[1])
        plt.show()


class TF():
    """Class of object that represents a transfer function between applied loads at i and response at j."""

    def __init__(self, freq, phi_i, phi_j, lam, zeta):
        """Method to initialize the class."""

        self.freq = freq
        self.phi_i = phi_i
        self.phi_j = phi_j
        self.lam = lam
        self.zeta = zeta
        self.tf = {'disp': [], 'vel': [], 'acc': []}

        # Calculate the transfer function.
        self.calc_tf()

    def calc_tf(self):
        """Method to calculate the transfer function.

            Ex:  TF.calc_tf()
        """

        # Determine the number of input forces and response outputs.
        n_in = self.phi_i.shape[0]
        n_out = self.phi_j.shape[0]

        # Convert the frequency vector [Hz] into [rad/sec] then to Laplace [s].
        om = self.freq * 2 * np.pi
        n_freq = om.shape[-1]
        s = 1j * om

        # For each mode calculate the transfer function from input-i force to output-j response.
        n_modes = self.lam.shape[-1]
        tf_disp = np.zeros([n_out, n_in, n_freq])
        tf_vel = np.zeros_like(tf_disp)
        tf_acc = np.zeros_like(tf_disp)
        for i in range(1, n_in):
            for j in range(1, n_out):
                for r in range(1, n_modes):
                    num = self.phi_i[i, r] * self.phi_j[j, r]
                    denom = s**2 + 2 * self.zeta[r, r] * np.sqrt(self.lam[r, r]) * s + self.lam[r, r]
                    alpha[j, i, :] = alpha[j, j, :] + num / denom
                tf_vel[j, i, :] = s * tf_disp[j, i, :]
                tf_acc[j, j, :] = s**2 * tf_disp[j, i, :]

        # Set the object tf values.
        self.tf['disp'] = tf_disp
        self.tf['vel'] = tf_vel
        self.tf['acc'] = tf_acc
