#!/ots/sw/osstoolkit/15.1/sles11-x86_64/bin/python3.5
import numpy as np
import argparse


class LOG:
    """Class of object that represents the data in a PILAGER log_file."""

    def __init__(self, log_file):
        """Method to initialize the LOG object."""
        self.log_file = log_file
        self.njf = 0
        self.group_names = []
        self.n_groups = 0
        self.n_press = []
        self.s_press = []
        self.veh_pos = []
        self.read_log()

    def read_log(self):
        """Method to read in the log_file and look for attributes."""

        # Read the lines in the log_file
        with open(self.log_file) as f:
            lines = f.readlines()

        # Determine the number of jet firing combinations in the log_file.
        jet_combos = [s for s in lines if "Jet firing combination" in s]
        self.njf = jet_combos.__len__()

        # Determine the position of the vehicle during each firing.
        self.veh_pos = np.zeros([self.njf, 3])
        self.veh_pos[:, 0] = np.asarray([float(s.split()[2]) for s in lines if "x =" in s])
        self.veh_pos[:, 1] = np.asarray([float(s.split()[2]) for s in lines if "y =" in s])
        self.veh_pos[:, 2] = np.asarray([float(s.split()[2]) for s in lines if "z =" in s])

        # Determine the list of unique groups in the log_file.
        peak_ns_group_press = [s for s in lines if "Peak normal and shear pressure for Group" in s]
        log_groups = [s[42:59] for s in peak_ns_group_press]
        log_groups = set(log_groups)
        self.n_groups = log_groups.__len__()

        # Make an array of normal and shear pressure for each group for each firing combo.
        self.n_press = np.zeros([self.njf, self.n_groups])
        self.s_press = np.zeros([self.njf, self.n_groups])
        for i, group in enumerate(log_groups):
            g_press = [s[74:] for s in peak_ns_group_press if group in s]
            g_press = np.asarray([np.asfarray(np.array(s.split()), float) for s in g_press])
            self.n_press[:, i] = g_press[:, 0]
            self.s_press[:, i] = g_press[:, 1]
            g_name = group.rstrip()
            self.group_names.append(g_name)


class AFILE:
    """Class of object that represents a PILAGER A-file."""

    def __init__(self, a_file):
        """Method to initialize the AFILE object."""
        self.a_file = a_file
        self.a_lines = []
        self.read_Afile()

    def read_Afile(self):
        """Method to read A-file attributes."""

        # Open and read the lines of the A-file.
        with open(self.a_file) as f:
            self.a_lines = f.read().splitlines()


class JFH(AFILE):
    """Class of object that represents a PILAGER JFH file."""
    pass


def filter_Amiss(**kwargs):
    """Function to remove the jet firings that miss the ISS from the A files."""

    # Determine the command/function arguments.
    if not bool(kwargs):
        parser = argparse.ArgumentParser()
        parser.add_argument('func', help='name of function: filter_Amiss')
        parser.add_argument('list', help='[A-file, log_file, new_A] to be filtered.')
        parser.add_argument('--limit', help='Limit to exclude pressure.')
        args = parser.parse_args()
        f_list = args.list
        if args.limit is None:
            limit = 0.001
        else:
            limit = float(args.limit)
    else:
        f_list = kwargs['list']
        if 'lmt' in kwargs.keys():
            limit = kwargs['lmt']
        else:
            limit = 0.001

    # Create the LOG and AFILE objects and filter.
    # Open the supplied list and read the A, log_files, and new A file list.
    with open(f_list) as f:
        lines = f.readlines()
    convert_list = [s.split() for s in lines]

    for entry in convert_list:
        a_file = entry[0]
        jfh_file = a_file + '.jfh'
        log_file = entry[1]
        out_file = entry[2]
        print('\tCreating new A-file: %s' % out_file)
        a_obj = AFILE(a_file)
        jfh_obj = JFH(jfh_file)
        log_obj = LOG(log_file)

        # Determine the jet firing pressures that are below the supplied limit.
        n_p_maxes = np.amax(log_obj.n_press, axis=1)
        n_s_maxes = np.amax(log_obj.s_press, axis=1)
        p_maxes = np.amax(np.column_stack((n_p_maxes, n_s_maxes)), axis=1)
        jet_index = np.arange(0, log_obj.njf)
        # miss_index = jet_index[p_maxes < limit]
        hit_index = p_maxes > limit

        # Determine if the jet firings are inside the ISS box.
        x_index = (-1700 < log_obj.veh_pos[:, 0]) & (log_obj.veh_pos[:, 0] < 650)
        y_index = (-1100 < log_obj.veh_pos[:, 1]) & (log_obj.veh_pos[:, 1] < 1100)
        z_index = (-800 < log_obj.veh_pos[:, 2]) & (log_obj.veh_pos[:, 2] < 800)
        r_index = x_index.astype(int) + y_index.astype(int) + z_index.astype(int)
        must_keep_index = r_index == 3
        delete_index = (hit_index.astype(int) + must_keep_index.astype(int)) == 0
        delete_index = jet_index[delete_index]

        # Remove the lines of the A-file that miss the ISS entirely or are in the ISS box.
        new_a_lines = np.asarray(a_obj.a_lines[1:])
        new_a_lines = np.delete(new_a_lines, delete_index)

        # Remove the lines of the JFH file as well.
        new_jfh_lines = np.asarray(jfh_obj.a_lines)
        new_jfh_lines = np.delete(new_jfh_lines, delete_index)

        # Renumber the A and jfh lines.
        for i, line in enumerate(new_jfh_lines):
            renumber = '{:>8}'.format(i + 1)
            new_line = renumber + line[8:]
            new_jfh_lines[i] = new_line
            a_line = new_a_lines[i]
            new_a_line = renumber + a_line[8:]
            new_a_lines[i] = new_a_line
        new_a_lines = np.insert(new_a_lines, 0, a_obj.a_lines[0], axis=0)

        # Write the new a_lines to filtered out file and jfh file.
        np.savetxt(out_file, new_a_lines, fmt='%s', delimiter='')
        np.savetxt(out_file + '.jfh', new_jfh_lines, fmt='%s', delimiter='')
