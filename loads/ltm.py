class LTM:
    """Loads Transformation Matrix class."""

    def __init__(self, name):
        """Initializing the LTM class."""
        self.name = name
        self.atm = {}
        self.dtm = {}
        self.num_ltms = 0
        self.num_modes = 0
        self.dofs = []
        self.acron_dofs = []
        self.types = []
        self.read_ltmfile()

    def read_ltmfile(self):
        """Method to read the LTMFILE for screening.

            Ex:  LTM.read_ltmfile()
        """
        import numpy as np
        import os

        # Use the file size to determine the number of LTMs in the LTMFILE.
        file_size = os.path.getsize(self.name)

        # Open the LTMFILE to determine the number of LTMs and number of modes.
        with open(self.name) as f:
            [bytes_in_record] = np.fromfile(f, dtype=np.int32, count=1)
            num_ltms = int(file_size/(bytes_in_record + 8))
            self.num_ltms = num_ltms
            matrix_name = np.fromfile(f, dtype=np.int8, count=80)
            [num_modes] = np.fromfile(f, dtype=np.int32, count=1)
            self.num_modes = num_modes
        self.atm = np.zeros([num_ltms, num_modes])
        self.dtm = np.zeros([num_ltms, num_modes])

        # Open the LTMFILE and read the contents into ATM and DTM.
        with open(self.name) as f:
            # Loop over the num_ltms and read each one.
            for i in range(self.num_ltms):
                # Bytes in record
                [bytes_in_record] = np.fromfile(f, dtype=np.int32, count=1)

                # Define LTM type for this entry.
                matrix_name = np.fromfile(f, dtype=np.int8, count=80)
                matrix_name = ''.join([chr(item) for item in matrix_name]).strip()
                elem_type = matrix_name[0:15]
                self.types.append(elem_type)

                # Define element and dof tuple for the LTM entry.
                element = int(matrix_name[16:24])
                dof = int(matrix_name[30:32])
                self.dofs.append((element, dof))

                # Read the LTM entry.
                [num_modes] = np.fromfile(f, dtype=np.int32, count=1)
                # if (element, dof) not in self.atm.keys():
                #     self.atm[(element, dof)] = np.zeros([num_modes, 1])
                # if (element, dof) not in self.dtm.keys():
                #     self.dtm[(element, dof)] = np.zeros([num_modes, 1])
                raw_otm = np.fromfile(f, dtype=np.float32, count=num_modes*2)
                # self.atm[(element, dof)] = raw_otm[0::2]
                # self.dtm[(element, dof)] = raw_otm[1::2]
                self.atm[i, :] = raw_otm[0::2]
                self.dtm[i, :] = raw_otm[1::2]

                # Bytes in record, should be the same as the first.
                [end_bytes] = np.fromfile(f, dtype=np.int32, count=1)

    def label_ltm(self, hwlist):
        """Method to label the LTM DOF with the HWLIST information.

            Ex:  LTM.label_ltm('hwlist.xls')
        """

        # Label each eid_dof combo if it exists in the LTM.
        for dof in self.dofs:
            if dof in hwlist.eid_dofids:
                i = hwlist.eid_dofids.index(dof)
                acron_dof = hwlist.acron_dofs[i]
                if acron_dof[1][0:3].upper() == 'RSS':
                    acron_dof = (acron_dof[0], acron_dof[1] + '_' + str(dof[1]))
                self.acron_dofs.append(acron_dof)
            else:
                self.acron_dofs.append(None)

    def find_dof(self, target, **kwargs):
        """Method to find the acronyms or element that match a pattern.

            Ex:  Look up all the LTMs containing a keyword in their acronym.
                LTM.find_dof('N2LAB', type='acron')

            Ex:  Look up all the LTMs containing a element id.
                LTM.find_dof(100100, type='eid')

            Ex:  Default is to look for both types.
                LTM.find_dof(100100)
        """

        # Determine the keyword arguments.
        t_type = []
        if 'type' in kwargs.keys():
            t_type = kwargs['type']

        # Search both types.
        if not t_type:
            res = []
            try:
                if type(target) is str:
                    res = [item for item in self.acron_dofs if target in item[0]]
                if not res:
                    eid = int(target)
                    res = [item for item in self.dofs if eid == item[0]]
            except:
                raise Exception('!!! {0} was not found in LTM {1} !!!'.format(target, self.name))
            print(res)
        else:
            # Search by type.
            if t_type == 'acron':
                target = str(target)
                res = [item for item in self.acron_dofs if target in item[0]]
            elif t_type == 'eid':
                eid = int(target)
                res = [item for item in self.dofs if eid == item[0]]
            else:
                raise Exception('!!! ltm.find_dof(target, acron=... or eid=...')
            print(res)
