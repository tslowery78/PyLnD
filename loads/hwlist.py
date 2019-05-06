class HWLIST:
    """Hardware List Class"""

    def __init__(self, name):
        """Initializing the HWLIST class."""
        self.name = name
        self.hw = {}
        self.acron_dofs = []
        self.eid_dofids = []
        self.num_dof = 0
        self.hw_rss = []
        self.read_hwlist()

    def read_hwlist(self):
        """Method to read in the HWLIST attributes.

            Ex:  HWLIST.read_hwlist()
        """

        # Read the HWLIST line by line looking for interface dof.
        # BN,A8,1x,I8,1X,A5,3x,2(I3))
        # bn,A8,1X,I8,1X,A5,3x,2(I3),2x,f10.2
        # aaaaaaaxiiiiiiiixaaaaaxxxiiiiiixxffffffffff
        with open(self.name, 'r') as f:
            for line in f:
                if line.__len__() > 20 and line[0] != '$':
                    acron = line[0:8].strip()
                    if acron not in self.hw.keys():
                        self.hw[acron] = {}
                    elem_id = int(line[9:17].strip())
                    if elem_id not in self.hw[acron]:
                        self.hw[acron][elem_id] = {}
                    dof = line[18:23].strip()
                    if dof not in self.hw[acron][elem_id]:
                        self.hw[acron][elem_id][dof] = {'dofs': [], 'load_limit': []}
                    if ',' in line[26:32]:
                        dofids = line[26:32].split(sep=',')
                    else:
                        dofids = line[26:32].split()
                    dofids = list(map(int, dofids))
                    if len(dofids) > 1:
                        self.hw_rss.append((acron, elem_id, dof))
                    for d in dofids:
                        self.eid_dofids.append((elem_id, d))
                        self.acron_dofs.append((acron, dof))
                    self.hw[acron][elem_id][dof]['dofs'] = dofids
                    load_limit = line[34:44]
                    try:
                        load_limit = float(load_limit)
                    except:
                        load_limit = 'na'
                    self.hw[acron][elem_id][dof]['load_limit'] = load_limit
        self.num_dof = self.acron_dofs.__len__()
