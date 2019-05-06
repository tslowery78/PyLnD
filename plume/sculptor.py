def sculptor(**kwargs):
    """Function to make a plume surface model and map."""
    from PyLnD.loads.f06_results import GRIDLOCA
    from PyLnD.loads.f06_results import USET

    # Import keyword arguments.
    [pbs, dat, gridloca, ese_grid_ranges, ese_phi_grids, plume_exlis, usetf06,
     plume_map_out, psm] = import_keywords(kwargs)

    # Make the plume and loads models from the pbs and dat files. (0.537)
    [loads_model, plume_model, plume_group_order] = make_models(pbs, dat)

    # Create the gridloca object and list of gridloca grids. (0.129)
    gridloca = GRIDLOCA(gridloca)
    grid_list = list(gridloca.grids.keys())

    # Relocate the grids in each plume model to match their location in the gridloca. (3.95)
    plume_model = relocate_plume_grids(plume_model, gridloca, grid_list)

    # Write out the pilager surface model. (0.009)
    make_psm(psm, plume_model, plume_group_order)

    # Read in the ESE group ranges and ESE phi grids and assign to ESE groups. (0.048)
    ese_groups = load_ese_groups(ese_grid_ranges, ese_phi_grids)

    # Create a uset table object. (0.456)
    print('... determining which grids are in the aset from the uset table:\n\t%s\n' % usetf06)
    uset = USET(usetf06)

    # For each plume model collect the associated loads grids. (4.88)
    #  - Collect grids from multiple loads model of same surfgroup.
    #  - Only collect if the grids are in Aset or are ese phi grids.
    #  - If the loads_model has an esephi name, warn the user.
    [plume_model, non_aset] = connect_models(plume_model, loads_model, uset, ese_groups)

    # For each plume_model grid find the nearest loads_model grid and distance. (22.58)
    plume_map = make_map(plume_model, gridloca, plume_map_out, plume_exlis, 8.0)

    # Write out the plume_grids.dat file. (0.029)
    plume_grids_out(plume_model)

    # Write out the loads_grids.dat file.
    loads_grids_out(loads_model)

    # Complete
    print('\n... process complete ...\n')
    print('\nSummary:')
    print('loads models: %s' % list(loads_model.keys()).__len__())
    print('plume grids: %s' % plume_map.__len__())
    print('surfmods: %s' % plume_group_order.__len__())
    print('gridloca grids: %s' % gridloca.grids.__len__())
    print('all 6dof aset grids: %s' % uset.aset_6dof.__len__())


def import_keywords(kwargs):
    """Function to import the keyword arguments."""

    if 'pbs' in kwargs.keys():
        pbs = kwargs['pbs']
    else:
        raise Exception('!!! pbs file must be specified. !!!')
    if 'dat' in kwargs.keys():
        dat = kwargs['dat']
    else:
        raise Exception('!!! dat file must be specified. !!!')
    if 'gridloca' in kwargs.keys():
        gridloca = kwargs['gridloca']
    else:
        raise Exception('!!! gridloca file must be specified. !!!')
    if 'ese_grid_ranges' in kwargs.keys():
        ese_grid_ranges = kwargs['ese_grid_ranges']
    else:
        raise Exception('!!! ese_grid_ranges file must be specified. !!!')
    if 'ese_phi_grids' in kwargs.keys():
        ese_phi_grids = kwargs['ese_phi_grids']
    else:
        raise Exception('!!! ese_phi_grids file must be specified. !!!')
    if 'plume_exlis' in kwargs.keys():
        plume_exlis = kwargs['plume_exlis']
    else:
        raise Exception('!!! ese_phi_grids file must be specified. !!!')
    if 'usetf06' in kwargs.keys():
        usetf06 = kwargs['usetf06']
    else:
        raise Exception('!!! usetf06 file must be specified. !!!')
    if 'plume_map' in kwargs.keys():
        plume_map_out = kwargs['plume_map']
    else:
        raise Exception('!!! plume_map file must be specified. !!!')
    if 'psm' in kwargs.keys():
        psm = kwargs['psm']
    else:
        raise Exception('!!! psm file must be specified. !!!')

    return pbs, dat, gridloca, ese_grid_ranges, ese_phi_grids, plume_exlis, usetf06, plume_map_out, psm


def plume_grids_out(plume_model):
    """Function to write out the plume_grids.dat file"""
    from sys import platform

    print('... writing out the plume_grids.dat file ...\n')
    # Look for debug platform.
    if platform == 'win32' or platform == 'darwin':
        plume_grids = 'sculptor/plume_grids.dat'
    else:
        plume_grids = 'plume_grids.dat'

    # Assemble complete plume grids list of tuples for output.
    plume_grid_list = []
    for k, v in plume_model.items():
        for g in list(v.plume_grids.keys()):
            k_v_tuple = (g, k)
            plume_grid_list.append(k_v_tuple)
    plume_grid_list = sorted(plume_grid_list, key=lambda x: x[0])

    # Write out the plume group grid ranges in sequential order.
    low = plume_grid_list[0][0]
    high = plume_grid_list[0][0]
    group = plume_grid_list[0][1]
    with open(plume_grids, 'w') as f:
        for i, p in enumerate(plume_grid_list):
            if p[1] == group:
                high = p[0]
            else:
                range_start = "{0:<8d}".format(low)
                range_stop = "{0:<8d}".format(high)
                s_group = "{0:<16s}".format(group)
                out_string = s_group[0:16] + range_start + ' ' + range_stop + '\n'
                f.write(out_string)
                low = p[0]
                high = p[0]
                group = p[1]


def loads_grids_out(loads_model):
    """Function to write out the loads_grids.dat file"""
    from sys import platform

    print('... writing out the loads_grids.dat file ...\n')
    # Look for debug platform.
    if platform == 'win32' or platform == 'darwin':
        loads_grids = 'sculptor/loads_grids.dat'
    else:
        loads_grids = 'loads_grids.dat'

    # Assemble complete loads grids list of tuples for output.
    loads_grid_list = []
    for k, v in loads_model.items():
        for g in list(v.loads_grids.keys()):
            k_v_tuple = (g, k)
            loads_grid_list.append(k_v_tuple)
    loads_grid_list = sorted(loads_grid_list, key=lambda x: x[0])

    # Write out the loads group grid ranges in sequential order.
    low = loads_grid_list[0][0]
    high = loads_grid_list[0][0]
    group = loads_grid_list[0][1]
    with open(loads_grids, 'w') as f:
        for i, p in enumerate(loads_grid_list):
            if p[1] == group:
                high = p[0]
            else:
                range_start = "{0:<8d}".format(low)
                range_stop = "{0:<8d}".format(high)
                s_group = "{0:<16s}".format(group)
                out_string = s_group[0:16] + range_start + ' ' + range_stop + '\n'
                f.write(out_string)
                low = p[0]
                high = p[0]
                group = p[1]


def make_models(pbs, dat):
    """Function to extract plume and loads model from pbs and dat files."""
    from PyLnD.loads.pbs import PBS
    from PyLnD.loads.dat_classes import DAT103
    from PyLnD.loads.blk import BLK
    from plume.plume_dat import PLUME_DAT
    from sys import platform

    # Create pbs and dat objects.
    print('... reading loads and plume models from system model pbs and dat files: \n\tpbs: %s\n\tdat: %s\n'
          % (pbs, dat))
    pbs = PBS(pbs)
    dat = DAT103(dat)

    # Remove the pch files included in the dat file.
    dat.included_blk = [x for x in dat.included_blk if ".pch" not in x]

    # Create the loads and the plume models.
    loads_model = {}
    plume_model = {}
    plume_group_order = []
    for d in dat.included_blk:

        # Check if the included file is the pbs job.
        if d not in pbs.blkfiles.keys():
            raise Exception('!!! %s is not in the pbs file !!!' % d)

        # Make an object for each loads model
        if d not in loads_model.keys():
            print('\tloads model: %s' % d)
            blkfile = pbs.blkfiles[d]

            # Look for debug platform.
            if platform == "win32" or platform == "darwin":
                blkfile = 'sculptor/blkfiles/' + blkfile.split('/')[-1]

            # Create blk object.
            print('\tblk: ' + blkfile)
            blk = BLK(blkfile)

            # Check for exceptions.
            if not blk.surfgroup:
                raise Exception('!!! %s does not have a plume group !!!\n\t%s' % (d, blkfile))

            # Set loads model attributes.
            print('\tsurfgroup: ' + blk.surfgroup)
            loads_model[d] = {'grids': list(blk.grids.keys())}
            loads_model[d]['surfgroup'] = blk.surfgroup
            if blk.surfgroup not in plume_group_order and blk.surfgroup.lower() != 'unknown':
                plume_group_order.append(blk.surfgroup)
            loads_model[d]['esephi_name'] = blk.esephi_name
            print('\tesephi group: %s' % blk.esephi_name)

            # Make plume model object from loads model surface model.
            if blk.surfgroup not in plume_model.keys():
                plume_model[blk.surfgroup] = PLUME_DAT(blk.surfgroup)
            plume_model[blk.surfgroup].loads_models.append(d)
            if blk.surfmod and blk.surfgroup.lower() != 'unknown':
                print('\tsurfmod: %s' % blk.surfmod)
                if not blk.surfgroup:
                    raise Exception('!!! loads model %s has specified a surf_mod: %s but no surfgroup' %
                                    (d, blk.surfmod))
                plume_model[blk.surfgroup].load_dat(blk.surfmod)
            elif blk.surfmod and blk.surfgroup.lower() == 'unknown':
                raise Exception('!!! %s has a surface model but is using "unknown" as a surfgroup !!!' % d)
        print('\n')
    return loads_model, plume_model, plume_group_order


def relocate_plume_grids(plume_model, gridloca, grid_list):
    """Function relocate the plume grids in the plume_model with the gridloca."""

    print('... relocating grids in the plume surface models based on the gridloca:\n\t%s\n' % gridloca.name)
    for group in plume_model.keys():
        for i, line in enumerate(plume_model[group].psm):
            if line[0:4].lower() == 'grid':
                grid = int(line[8:16])
                if grid in grid_list:
                    plume_model[group].plume_grids[grid] = gridloca.grids[grid]
                    x_pos = "{0:>8.2f}".format(gridloca.grids[grid][0])
                    y_pos = "{0:>8.2f}".format(gridloca.grids[grid][1])
                    z_pos = "{0:>8.2f}".format(gridloca.grids[grid][2])
                    grid = "{0:<8d}".format(grid)
                    plume_model[group].psm[i] = 'GRID    ' + grid + '       0' + x_pos + y_pos + z_pos
    return plume_model


def load_ese_groups(ese_grid_ranges, ese_phi_grids):
    """Function to read in the ESE group ranges."""

    print('... reading the ESE PHI group ranges and grids:\n\tese group ranges: %s'
          '\n\tese phi grids: %s\n' % (ese_grid_ranges, ese_phi_grids))
    ese_groups = {}
    with open(ese_grid_ranges) as f:
        for line in f:
            start = int(line[0:8])
            stop = int(line[8:16])
            group = line[16:40].strip()
            flag = int(line[40:48])
            if group not in ese_groups.keys():
                ese_groups[group] = {'range': [start, stop, flag]}

    # Read the ESE phi grids and assign them to the ese_groups
    # Check if the group is empty
    with open(ese_phi_grids) as f:
        for line in f:
            grid = int(line)
            for group in ese_groups.keys():
                start = ese_groups[group]['range'][0]
                stop = ese_groups[group]['range'][1]
                if start < grid < stop:
                    if 'grids' not in ese_groups[group].keys():
                        ese_groups[group]['grids'] = []
                    ese_groups[group]['grids'].append(grid)
    return ese_groups


def connect_models(plume_model, loads_model, uset, ese_groups):
    """Function to connect the plume model and loads model."""
    from sys import platform

    print('... collecting the loads model grids in aset or ese grids for each plume model ...\n')
    non_aset = {}
    for surfgroup, psm in sorted(plume_model.items()):
        for ldm in sorted(psm.loads_models):
            if ldm not in non_aset.keys():
                non_aset[ldm] = {'grids': [], 'surfgroup': surfgroup}
            # Add the esephi grids if required, fatal if missing.
            if loads_model[ldm]['esephi_name']:
                if surfgroup not in ese_groups.keys():
                    print('!!! %s loads model specifies a ese phi but none'
                                    ' is provided in the ESE group range file.' % ldm)
                else:
                    psm.loads_grids.extend(ese_groups[surfgroup]['grids'])
            for ug in loads_model[ldm]['grids']:
                if ug in uset.aset_6dof:
                    psm.loads_grids.append(ug)
                else:
                    non_aset[ldm]['grids'].append(ug)

        # Fatal if no grids found!
        if not psm.loads_grids:
            raise Exception('!!! plume group %s has no loads grids to map to !!!'
                            '\n\tCheck the non_aset table output.' % psm)

    # Look for debug platform.
    if platform == 'win32' or platform == 'darwin':
        non_aset_file = 'sculptor/non_aset_grids.dat'
    else:
        non_aset_file = 'non_aset_grids.dat'

    # Write out the non-aset grids.
    print('\n... writing out the non-aset grids file:\n\t%s\n' % non_aset_file)
    with open(non_aset_file, 'w') as f:
        for na_ldm, na in non_aset.items():
            f.write('loads model: %s\n' % na_ldm)
            f.write('surfgroup: %s\n' % na['surfgroup'])
            f.write('grids: %s\n\n' % na['grids'])

    return plume_model, non_aset


def make_map(plume_model, gridloca, plume_map_out, plume_exlis, eps):
    """Function to make the map between plume and loads grids."""
    import numpy as np
    from scipy import spatial

    print('... creating the plume to loads model map:\n\t%s\n' % plume_map_out)
    # Read in the plume exclusion list.
    plume_ex = []
    with open(plume_exlis) as f:
        for line in f:
            plume_ex.append(int(line[8:16]))

    plume_map = []
    for pm_k, pm in sorted(plume_model.items()):
        # Make an array out of the loads grids locations.
        lg_locations = np.empty((0, 3))
        for lg in pm.loads_grids:
            new_location = np.asarray(gridloca.grids[lg])
            new_location = np.array([new_location])
            lg_locations = np.append(lg_locations, new_location, axis=0)

        # For each plume grid, not in the exlcusion list, find the closest loads grid.
        for pg, pg_location in sorted(pm.plume_grids.items()):
            if pg not in plume_ex:
                distance, index = spatial.KDTree(lg_locations).query(pg_location)
                lg_mapped = pm.loads_grids[index]
                p2l_diff = pg_location - lg_locations[index]
                if distance > eps:
                    flag = '%%'
                else:
                    flag = ''
                plume_map.append([pm_k, pg, lg_mapped, p2l_diff, distance, flag])

    # Write out the plume to loads model map.
    with open(plume_map_out, 'w') as f:
        # format(1x, a16, 1x, a8, 1x, a8, 4(1x, f10.4), 2x, a2)
        for line in plume_map:
            group = "{0:<16s}".format(line[0])
            plume_grid = "{0:<8d}".format(line[1])
            loads_grid = "{0:<8d}".format(line[2])
            x_pos = "{0:>10.4f}".format(line[3][0])
            y_pos = "{0:>10.4f}".format(line[3][1])
            z_pos = "{0:>10.4f}".format(line[3][2])
            distance = "{0:>10.4f}".format(line[4])
            flag = "{0:>2s}".format(line[5])
            f.write(' ' + group + ' ' + plume_grid + ' ' + loads_grid + ' ' + x_pos + ' ' + y_pos + ' ' + z_pos +
                    ' ' + distance + '  ' + flag + '\n')

    return plume_map


def make_psm(psm, plume_model, plume_group_order):
    """Function to write out the plume surface model."""

    print('... writing out the complete plume surface model:\n\t%s\n' % psm)
    with open(psm, 'w') as f:
        for surfgroup in plume_group_order:
            for line in plume_model[surfgroup].psm:
                f.write(line)
