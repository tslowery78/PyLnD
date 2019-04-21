class BAS:
    """BASFILE class to define the parameters of a screening run."""

    def __init__(self, name):
        self.name = name
        self.berthing = 'na'
        self.desc = 'na'
        self.cycle_id = 'na'
        self.model_id = 'na'
        self.ff_id = 'na'
        self.sc_id = 'na'
        self.start_case = 'na'
        self.integration_type = 'na'
        self.auto_time = 'na'
        self.time_increment = 'na'
        self.modal_damp_pct = 'na'
        self.modes_start = 'na'
        self.modes_end = 'na'
        self.num_cases = 'na'
        self.uncertainty = 'na'
        self.limit_load_multiplier = 'na'
        self.read_bas()

    def read_bas(self):
        """Method to read the BASFILE parameters."""
        # Open and read all the lines in the BASFILE.
        with open(self.name) as f:
            lines = f.readlines()
        # For each line determine the screening run parameters.
        for i, line in enumerate(lines):
            if line[18:26] == 'BERTHING':   # Found the berthing analysis flag.
                if line[32:33] == '0':
                    self.berthing = 'yes'
            if line[18:29] == 'DESCRIPTION':    # Found the run description.
                self.desc = lines[i + 1].rstrip()
            if line[11:16] == 'CYCLE':  # Found the cycle id.
                self.cycle_id = lines[i + 1].rstrip()
            if line[5:10] == 'EVENT':   # Found the event id, break into model id and ff id.
                event_id = lines[i + 1].rstrip()
                self.model_id = event_id[0:2]
                self.ff_id = event_id[2:]
            if line[5:11] == 'CONFIG':  # Found the sc id.
                self.sc_id = lines[i + 1].rstrip()
            if line[5:10] == 'START':   # Found the starting case number.
                self.start_case = lines[i + 1].rstrip()
            if line[5:10] == 'INTEG':   # Found the integration routine selection.
                selection = int(lines[i + 2])
                if selection == 1:
                    self.integration_type = 'Newmark-Beta'
                elif selection == 2:
                    self.integration_type = 'Recurrence Formulas'
            if line[5:9] == 'TIME':   # Find the time constraints.
                times = lines[i + 1].split()
                if times[0].upper() == 'AUTO':
                    self.auto_time = 'yes'
                    self.time_increment = float(times[1])
                else:
                    self.auto_time = 'no'
            if line[11:18] == 'DAMPING':   # Found the modal damping %
                self.modal_damp_pct = float(lines[i + 1])
            if line[5:10] == 'RANGE':   # Found the range of modes to include.
                mode_range = lines[i + 1].split()
                self.modes_start = int(mode_range[0])
                self.modes_end = int(mode_range[1])
            if line[5:11] == 'NUMBER':  # Found the number of analysis cases.
                self.num_cases = int(lines[i + 1])
            if line[5:8] == 'UNC':  # Found the uncertainty of the analysis.
                self.uncertainty = float(lines[i + 1])
            if line[5:10] == 'LIMIT':   # Found the limit load multiplication factor.
                self.limit_load_multiplier = float(lines[i + 1])
