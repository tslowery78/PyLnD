import numpy as np
import re

class read_op4_ascii:
    """Read ascii op4 files"""

    def __init__(self, name):
        self.name = name
        self.data = {}
        self.read_op4()
        self.save2mat()

    def read_op4(self):

        with open(self.name) as f:
            while True:
                line = f.readline()
                if not line:
                    break
                logical = 0
                line_temp = line
                line_temp = re.sub('\n', '', line_temp)
                line_temp = re.sub(r'\s+', ',', line_temp)
                line_temp = re.sub(',', '', line_temp)
                line_temp = line_temp.replace('.', '')

                if line_temp.isalnum() and not line_temp.isnumeric() and not logical:
                    case = line[31:40]
                    case = re.sub(r'\s+', '', case)
                    logical = 1
                    s_log = 1

                if line_temp.isnumeric() and not logical:
                    line = f.readline()
                    line_temp = line
                    line_temp = re.sub('\n', '', line_temp)
                    line_temp = re.sub(r'\s+', ',', line_temp)
                    line_temp = re.sub(',', '', line_temp)
                    line_temp = line_temp.replace('.', '')

                line_temp = line_temp.replace('+', '')
                line_temp = line_temp.replace('-', '')

                if line_temp.isalnum() and not logical:
                    c1 = float(line[0:16])
                    try:
                        c2 = float(line[16:32])
                        c3 = float(line[32:48])
                        c4 = float(line[48:64])
                        c5 = float(line[64:80])

                        logical = 1
                        new_row = np.array([[c1, c2, c3, c4, c5]])

                        if s_log:
                            self.data[case] = new_row
                            s_log = 0
                        else:
                            self.data[case] = np.append(self.data[case], new_row, axis=0)
                    except:
                        logical = 1


    def save2mat(self):
        from scipy.io import savemat
        outfile = self.name
        outfile = outfile[:-4]
        mdict = {}

        for case in self.data.keys():
            mdict['op4_' + case.__str__()] = self.data[case]

        # Save to .mat file
        savemat(outfile, mdict=mdict)


if __name__ == '__main__':
    op4 = read_op4_ascii('testing/s4red_90.ot4')