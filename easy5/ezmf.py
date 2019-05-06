import numpy as np


class EZMF:
    """Class of object representing an Easy5 .ezmf file"""

    def __init__(self, name):
        """Method to initialize the object"""

        # Assign parameters
        self.name = name
        self.components = {}
        self.load()

    def load(self):
        """Read the file and pick out the important stuff"""

        # Open read the ezmf file
        with open(self.name) as f:
            lines = f.read().splitlines()

        # Find all CH elements and extract their parameters
        ch_index = [i for i, line in enumerate(lines) if line[0:2] == 'CH' and len(line) < 5]
        if ch_index:
            ch_ids = [lines[i] for i in ch_index]
            ch_desc = [lines[i + 1] for i in ch_index]
            # Find liquid volume
            vol_index = [i for i, line in enumerate(lines) if line == 'Liquid volume']
            ch_volumes = extract_parameter('Liquid volume', vol_index, lines, 3, number=True)
            # Put into object dict
            ch = {'type': 'ch',
                  'ids': np.asarray(ch_ids),
                  'desc': np.asarray(ch_desc),
                  'vol': np.asarray(ch_volumes)}
            self.components['ch'] = ch

        # Find all PI element and extract their parameters
        pi_index = [i for i, line in enumerate(lines) if line[0:2] == 'PI' and len(line) < 5]
        if pi_index:
            # Remove errant PIL line
            pi_real_zeros = [lines[i + 1] for i in pi_index]
            pi_fake_index = [i for i, line in enumerate(pi_real_zeros) if line == '']
            r = 0
            for remove in pi_fake_index:
                del pi_index[remove + r]
                r -= 1
            pi_ids = [lines[i] for i in pi_index]
            pi_desc = [lines[i + 1] for i in pi_index]
            pi_sr = [lines[i + 8][1:] for i in pi_index]
            pi_dh = extract_parameter('Hydraulic diameter', pi_index, lines, 3, number=True)
            pi_len = extract_parameter(
                'Length of pipe {if bends included, LEN = total length of all straight sections}', pi_index, lines, 3,
                number=True)
            pi_rfc = extract_parameter('Absolute roughness', pi_index, lines, 3, number=True)
            pi_od = extract_parameter('Outer diameter for heat transfer area', pi_index, lines, 4, number=True)
            pi_dens = extract_parameter('Wall material density (use global default if 0.99999)', pi_index, lines, 4,
                                        number=True)
            pi_spht = extract_parameter('Specific heat of wall material (use global default if = 0.99999)',
                                        pi_index, lines, 4, number=True)
            pi_xln = extract_parameter('Extra length (for pressure drop)', pi_index, lines, 3, number=True)
            pi_dzh = extract_parameter('Height of exit above inlet', pi_index, lines, 3, number=True)
            pi_vol = np.pi * (np.asarray(pi_dh) / 2)**2 * pi_len
            # Put into object dict
            pi = {'type': 'pi',
                  'ids': np.asarray(pi_ids),
                  'desc': np.asarray(pi_desc),
                  'sr': np.asarray(pi_sr),
                  'dh': np.asarray(pi_dh),
                  'len': np.asarray(pi_len),
                  'rfc': np.asarray(pi_rfc),
                  'od': np.asarray(pi_od),
                  'dens': np.asarray(pi_dens),
                  'spht': np.asarray(pi_spht),
                  'xln': np.asarray(pi_xln),
                  'dzh': np.asarray(pi_dzh),
                  'vol': pi_vol}
            self.components['pi'] = pi

        # Find all the OR elements and extract their parameters
        or_index = [i for i, line in enumerate(lines) if line[0:2] == 'OR' and len(line) < 5]
        if or_index:
            or_ids = [lines[i] for i in or_index]
            or_desc = [lines[i + 1] for i in or_index]
            or_dh = extract_parameter('Orifice hydraulic diameter', or_index, lines, 4, number=True)
            or_are = extract_parameter('Orifice flow area', or_index, lines, 4, number=True)
            or_cd = extract_parameter('Constant discharge coefficient', or_index, lines, 4, number=True)
            # Put into object dict
            orifice = {'type': 'or',
                       'ids': np.asarray(or_ids),
                       'desc': np.asarray(or_desc),
                       'dh': np.asarray(or_dh),
                       'are': np.asarray(or_are),
                       'cd': np.asarray(or_cd)}
            self.components['or'] = orifice

        # Find all the VC elements and extract their parameters
        vc_index = [i for i, line in enumerate(lines) if line[0:2] == 'VC' and len(line) < 5]
        if vc_index:
            vc_ids = [lines[i] for i in vc_index]
            vc_desc = [lines[i + 1] for i in vc_index]
            vc_pck = extract_parameter('Cracking pressure drop', vc_index, lines, 3, number=True)
            vc_pfo = extract_parameter('Pressure difference at which valve is fully open', vc_index, lines, 4, number=True)
            vc_dh = extract_parameter('Hydraulic diameter when fully open', vc_index, lines, 3, number=True)
            vc_vol = extract_parameter('Effective average volume', vc_index, lines, 3, number=True)
            vc_cd = extract_parameter('Discharge coefficient', vc_index, lines, 4, number=True)
            vc_tfl = extract_parameter('Fluid temperature in volume', vc_index, lines, 3, number=True)
            # Put into object dict
            vc = {'type': 'vc',
                  'ids': np.asarray(vc_ids),
                  'desc': np.asarray(vc_desc),
                  'pck': np.asarray(vc_pck),
                  'pfo': np.asarray(vc_pfo),
                  'dh': np.asarray(vc_dh),
                  'vol': np.asarray(vc_vol),
                  'cd': np.asarray(vc_cd),
                  'tfl': np.asarray(vc_tfl)}
            self.components['vc'] = vc

        # Find all the VC elements and extract their parameters
        vm_index = [i for i, line in enumerate(lines) if line[0:2] == 'VM' and len(line) < 5]
        if vm_index:
            vm_ids = [lines[i] for i in vm_index]
            vm_desc = [lines[i + 1] for i in vm_index]
            vm_tc = extract_parameter('Time constant for valve dynamics', vm_index, lines, 4, number=True)
            vm_cd = extract_parameter('Discharge coefficent', vm_index, lines, 3, number=True)
            vm_vol = extract_parameter('Volume of fluid in upstream section', vm_index, lines, 3, number=True)
            vm_tfl = extract_parameter('Fluid temperature in volume', vm_index, lines, 3, number=True)
            vm_afs = extract_parameter('Scaled orifice flow area', vm_index, lines, 4, number=True)
            vm = {'type': 'vm',
                  'ids': np.asarray(vm_ids),
                  'desc': np.asarray(vm_desc),
                  'tc': np.asarray(vm_tc),
                  'cd': np.asarray(vm_cd),
                  'vol': np.asarray(vm_vol),
                  'tfl': np.asarray(vm_tfl),
                  'afs': np.asarray(vm_afs)}
            self.components['vm'] = vm

        # Find all the PB elements and extract their parameters
        pb_index = [i for i, line in enumerate(lines) if line[0:2] == 'PB' and len(line) < 5]
        if pb_index:
            pb_ids = [lines[i] for i in pb_index]
            pb_desc = [lines[i + 1] for i in pb_index]
            pb_rfc = extract_parameter('Pipe absolute roughness', pb_index, lines, 3, number=True)
            pb_od = extract_parameter('Outer diameter for heat transfer area', pb_index, lines, 4, number=True)
            pb_dh = extract_parameter('Hydraulic diameter', pb_index, lines, 3, number=True)
            pb_len = extract_parameter('Length of pipe', pb_index, lines, 3, number=True)
            pb_dzh = extract_parameter('Height of exit above inlet', pb_index, lines, 4, number=True)
            pb_tf = extract_parameter('Fluid temperature', pb_index, lines, 3, number=True)
            pb_vol = []
            for i, dh in enumerate(pb_dh):
                try:
                    pb_vol.append(np.pi * (dh / 2)**2 * pb_len[i])
                except TypeError:
                    pb_vol.append('not available')
            pb = {'type': 'pb',
                  'ids': np.asarray(pb_ids),
                  'desc': np.asarray(pb_desc),
                  'rfc': np.asarray(pb_rfc),
                  'od': np.asarray(pb_od),
                  'dh': np.asarray(pb_dh),
                  'len': np.asarray(pb_len),
                  'dzh': np.asarray(pb_dzh),
                  'tf': np.asarray(pb_tf),
                  'vol': np.asarray(pb_vol)}
            self.components['pb'] = pb


def extract_parameter(string, index, lines, n, **kwargs):
    """Method to do all extraction"""

    # Get kwargs
    float_expected = False
    if 'number' in kwargs.keys():
        float_expected = True

    item_list = []
    # Loop the full index and get the item index
    for i, ii in enumerate(index):
        try:
            item_index = extract_index(string, lines[ii:index[i + 1]])
        except IndexError:
            item_index = extract_index(string, lines[ii:ii+300])

        # Try to convert to float or leave as string
        try:
            item_list.append(float(lines[ii + item_index[0] + n]))
        except ValueError:
            if not float_expected:
                item_list.append(lines[ii + item_index[0] + n])
            else:
                item_list.append('default')
    return item_list


def extract_index(string, lines):
    """Method to extract string from sub list and get its index"""

    index = [i for i, line in enumerate(lines) if line == string]
    return index


if __name__ == '__main__':
    ez = EZMF('rhs_cooling_loop.41.ezmf')
    pass
