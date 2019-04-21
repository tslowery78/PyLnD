def contacts_point_plane(i_marker_locations: dict, j_geometry: str, cmd_file: str, stiffness: float,
                         damping: float, exponent: float, dmax: float, **kwargs):
    """Function to create an ADAMS cmd file that will create a series of point-plane contacts.
        input:
                i_marker_locations- dict; key(marker location string) value(markers)
                j_geometry- string; plane name
                cmd_file- string; cmd file name
    """

    # Get the optional arguments
    friction = False
    if 'mu_static' in kwargs.keys():
        friction = True
        mu_static = kwargs['mu_static']
        mu_dynamic = kwargs['mu_dynamic']
        svelo = kwargs['svelo']
        fvelo = kwargs['fvelo']

    # Write out the cmd file
    with open(cmd_file, 'w') as f:
        for marker_location, markers in i_marker_locations.items():
            # Make comma-separated string
            markers_str = ','.join(markers)
            f.write('contact create &\n')
            f.write('    contact_name =.IVA_Hatch.CONTACT_{0}_seal &\n'.format(marker_location))
            f.write('    i_marker_name = {0} &\n'.format(markers_str))
            f.write('    j_geometry_name = {0} &\n'.format(j_geometry))
            f.write('    stiffness = {0} &\n'.format(stiffness))
            f.write('    damping = {0} &\n'.format(damping))
            f.write('    exponent = {0} &\n'.format(exponent))
            if not friction:
                f.write('    dmax = {0}\n\n'.format(dmax))
            else:
                f.write('    dmax = {0} &\n'.format(dmax))
                f.write('    coulomb_friction = on  &\n')
                f.write('    mu_static = {0} &\n'.format(mu_static))
                f.write('    mu_dynamic = {0} &\n'.format(mu_dynamic))
                f.write('    stiction_transition_velocity = {0} &\n'.format(svelo))
                f.write('    friction_transition_velocity = {0}\n\n'.format(fvelo))
    print('created {0}'.format(cmd_file))
