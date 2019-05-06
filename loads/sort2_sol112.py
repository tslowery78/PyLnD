import numpy as np


class SORT2_112:
    """NASTRAN Sort 112 time history in sort2 format."""

    def __init__(self, name):
        """Initializing SORT2_112 object."""
        self.name = name
        self.data = {}
        self.read_sort2()

    def read_sort2(self):
        """Function to convert a sort2 sol 112 transient pch file to a MATLAB mat."""

        # Read and parse the file data into dict structure.
        with open(self.name) as f:
            while True:
                line = f.readline()
                if not line:
                    break
                if line[0:13] == "$SUBCASE ID =":
                    pid = None
                    p_count = 0
                    etype = None
                    subcase = int(line[13:40])
                    if subcase not in self.data.keys():
                        self.data[subcase] = {}
                if line[0:15] == "$ELEMENT TYPE =":
                    type_str = line[15:40].lower()
                    etype = ''
                    if 'beam' in type_str:
                        etype = "cbeam"
                    if 'bar' in type_str:
                        etype = "cbar"
                    if etype == '':
                        raise Exception('!!! Cannot find any type in {0}'.format(type_str))
                    if etype not in self.data[subcase].keys():
                        self.data[subcase][etype] = {}
                if line[0:11] == '$POINT ID =':
                    pid = int(line[12:25])
                    p_count = p_count + 1
                if line[0:13] == "$ELEMENT ID =" and pid is None:
                    eid = int(line[15:25])
                    if eid not in self.data[subcase][etype].keys():
                        if etype == 'cbeam':
                            self.data[subcase][etype][eid] = {}
                        elif etype == 'cbar':
                            self.data[subcase][etype][eid] = np.empty((0, 9))
                if line[0] == " ":
                    if etype == 'cbeam':
                        for i in range(0, 11):
                            if i > 0:
                                line = f.readline()
                            gid = int(line[22:33])
                            if gid == 0:
                                line = f.readline()
                                line = f.readline()
                                continue
                            if gid not in self.data[subcase][etype][eid].keys():
                                self.data[subcase][etype][eid][gid] = \
                                    np.empty((0, 7))
                            if line[0:6] != "-CONT-":
                                time = float(line[6:18])
                            m1 = float(line[59:72])
                            line = f.readline()
                            m2 = float(line[23:36])
                            s1 = float(line[41:54])
                            s2 = float(line[59:72])
                            line = f.readline()
                            ax = float(line[23:36])
                            tor = float(line[41:54])
                            new_row = np.array([[time, m1, m2, s1, s2, ax, tor]])
                            self.data[subcase][etype][eid][gid] = np.append(
                                self.data[subcase][etype][eid][gid],
                                new_row, axis=0)
                    elif etype == 'cbar':
                        if line[0:6] != "-CONT-":
                            time = float(line[6:18])
                        ma1 = float(line[23:36])
                        ma2 = float(line[41:54])
                        mb1 = float(line[59:72])
                        line = f.readline()
                        mb2 = float(line[23:36])
                        s1 = float(line[41:54])
                        s2 = float(line[59:72])
                        line = f.readline()
                        ax = float(line[23:36])
                        tor = float(line[41:54])
                        new_row = np.array([[time, ma1, ma2, mb1, mb2, s1, s2, ax, tor]])
                        self.data[subcase][etype][eid] = np.append(
                            self.data[subcase][etype][eid],
                            new_row, axis=0)
                    elif pid is not None:
                        if line[0:6] != '-CONT-':
                            time = float(line[4:16])
                        ma1 = float(line[23:36])
                        ma2 = float(line[41:54])
                        ma3 = float(line[59:72])
                        line = f.readline()
                        mb2 = float(line[26:36])
                        s1 = float(line[41:54])
                        s2 = float(line[59:72])
                        new_row = np.array([[time, ma1, ma2, ma3, mb2, s1, s2]])
                        if p_count == 1:
                            self.data[subcase][pid] = new_row
                            p_count = 0
                        else:
                            self.data[subcase][pid] = np.append(self.data[subcase][pid],new_row, axis=0)
                    self.pid = pid

    def save2mat(self, outfile):
        """Method to save the dictionary into a mat file."""
        from scipy.io import savemat

        # Loop over each element and create the matlab dictionary.
        mdict = {}
        if self.pid is None:
            for case in self.data.keys():
                for etype in self.data[case].keys():
                    for eid in self.data[case][etype].keys():
                        if etype == 'cbeam':
                            for gid in self.data[case][etype][eid].keys():
                                mdict['c' + case.__str__() + '_' + eid.__str__()
                                    + '_' + gid.__str__()] = self.data[case][etype][eid][gid]
                        elif etype == 'cbar':
                            mdict['c' + case.__str__() + '_' + eid.__str__()] = self.data[case][etype][eid]

        else:
            for case in self.data.keys():
                for pid in self.data[case].keys():
                    mdict['c' + case.__str__() + '_' + pid.__str__()] = self.data[case][pid]

        # Save to a mat file.
        savemat(outfile, mdict=mdict)
