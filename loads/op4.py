import numpy as np


class OP4:
    """Class of object to represent the matrices in an OP4 file.

        Ex:  OP4(op4=filename, type='ascii')
    """

    def __init__(self, **kwargs):
        """Method to initialize the OP4 object."""

        # Get the keyword arguments.
        if 'op4' in kwargs.keys():
            self.op4_file = kwargs['op4']
        else:
            raise Exception('The op4 is required!')
        if 'type' in kwargs.keys():
            self.in_type = kwargs['type']
        else:
            raise Exception('The type is required!')

        self.op4 = {}
        self.load()

    def load(self):
        """Method to load the OP4 file data."""

        if self.in_type.lower() == 'ascii':

            # Read all the lines in the file.
            with open(self.op4_file) as f:
                lines = f.read().splitlines()

            # Determine the number of matrices in the ot4
            i_headers = [i for i, val in enumerate(lines) if ',' in val]

            # Read in each matrix.
            for i in i_headers:

                # Get the matrix properties.
                n_cols = int(lines[i][0:8])
                n_rows = int(lines[i][8:16])
                form = int(lines[i][16:24])
                m_type = int(lines[i][24:32])
                m_name = lines[i][32:40]
                m_name = ' '.join(m_name.split())
                nrec_per_line = int(lines[i][43])
                rec_size = int(lines[i][45:47])
                if m_name not in self.op4.keys():
                    self.op4[m_name] = {'n_rows': n_rows, 'n_cols': n_cols, 'form': form, 'type': m_type,
                    'data': np.zeros([n_rows, n_cols])}

                # Read each column section
                p = i
                for c in range(0, n_cols):
                    i_col = int(lines[p + 1][0:8])
                    i_num = int(lines[p + 1][8:16])
                    n_rec = int(lines[p + 1][16:24])
                    n_lines = int(n_rec/nrec_per_line)
                    n_l_modulus = n_rec % nrec_per_line
                    if n_l_modulus > 0:
                        n_lines += 1
                    s = i_num - 1
                    for j in range(2, n_lines + 2):
                        o = p + j
                        line_chunk = [lines[o][m:m + rec_size] for m in range(0, len(lines[o]), rec_size)]
                        line_data = list(map(float, line_chunk))
                        s_end = len(line_data)
                        self.op4[m_name]['data'][s:s+s_end, i_col - 1] = line_data
                        s += s_end
                    p += n_lines + 1

    def save2mat(self, matfile):
        """Method to save the matrices to a file.

            Ex: op4.save2mat(matfile)
        """

        from PyLnD.matlab.mat_utilities import save2mat

        v_dict = list(self.op4.keys())
        save2mat(key=v_dict, olist=self.op4[v_dict[0]], ofile=matfile)
