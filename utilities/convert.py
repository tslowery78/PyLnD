def convert(request, **kwargs):
    """Converts any set of units to all other known systems.

        request:  two strings containing 'value units'; ex. '50 in'
            mass flow request:  '290 gpm @ 54 lbm/ft3'
        response:  a dict containing all known units of the requested type

        options:
            verbose:  controls the response print out; ex. verbose=False - suppresses printout
        """

    # Parse the request statement
    split_request = request.split()
    value = float(split_request[0])
    units = split_request[1]
    dens_resp = ''
    if '@' in request:
        density = float(split_request[3])
        density_units = split_request[4]
        dens_resp = convert(str(density) + ' ' + density_units, verbose=False)

    # Set the options
    verbose = True
    if kwargs:
        if 'verbose' in kwargs.keys():
            verbose = kwargs['verbose']

    # Build the response
    response = {units.lower(): value}

    # LENGTH #

    if units.lower() == 'in':                   # from inches to ...
        response['m'] = value / 39.3700787
        response['ft'] = value / 12

    elif units.lower() == 'm':                  # from meter to ...
        response['in'] = value * 39.3700787

    # VOLUME #

    elif units.lower() == 'ft3':                # from ft3 to ...
        response['gal'] = value * 7.48051948

    elif units.lower() == 'gal':                # from gal to ...
        response['ft3'] = value / 7.48051948

    # PRESSURE #

    elif units.lower() == 'in-water':           # from in-water to ...
        response['psi'] = value / 27.70759

    elif units.lower() == 'psi':                # from psi to ...
        response['in-water'] = value * 27.70759

    # VOLUMETRIC FLOW RATE #

    elif units.lower() == 'cc/min':                     # from cc/min to ...
        response['cc/sec'] = value / 60
        response['cc/hr'] = 60 * value
        response['in3/sec'] = value / 16.387064 / 60
        response['in3/min'] = value / 16.387064
        response['in3/hr'] = 60 * value / 16.387064
        response['gps'] = value / 3785.41 / 60
        response['gpm'] = value / 3785.41
        response['gph'] = 60 * value / 3785.41

    elif units.lower() == 'gpm':                        # from gpm to ...
        response['gps'] = value / 60
        response['gph'] = 60 * value
        response['cc/sec'] = value * 3785.41 / 60
        response['cc/min'] = value * 3785.41
        response['cc/hr'] = 60 * value * 3785.41
        response['in3/sec'] = value * 231 / 60
        response['in3/min'] = value * 231
        response['in3/hr'] = 60 * value * 231

    elif units.lower() == 'in3/sec':                    # from in3/sec to ...
        response['in3/min'] = value * 60
        response['in3/hr'] = 60 * value * 60
        response['cc/sec'] = value * 16.387064
        response['cc/min'] = value * 16.387064 * 60
        response['cc/hr'] = 60 * value * 16.387064 * 60
        response['gps'] = value / 231
        response['gpm'] = value / 231 * 60
        response['gph'] = 60 * value / 231 * 60

    # DENSITY #

    elif units.lower() == 'lbm/ft3' or units.lower() == 'lb/ft3':        # from lbm/ft3 to ...
        response['lbm/in3'] = value / 12**3
        response['lbf/in3'] = value / 12**3 / (32.174049 * 12)

    elif units.lower() == 'lbm/in3' or units.lower() == 'lb/in3':        # from lbm/in3 to ...
        response['lbm/ft3'] = value * 12**3
        response['lbf/ft3'] = value * 12**3 * 32.174049
        response['lbf/in3'] = value * 32.174049
        
    else:
        raise Exception('There are no conversions for {0:f} {1}'.format(value, units))

    # MASS FLOW RATE
    mass_flow = {}
    if '@' in request:
        mass_flow['ppm'] = response['in3/min'] * dens_resp['lbm/in3']
        mass_flow['pps'] = response['in3/sec'] * dens_resp['lbm/in3']
        mass_flow['pph'] = response['in3/hr'] * dens_resp['lbm/in3']
        
    # MASS #
    if units.lower() == 'lbm' or units.lower() == 'lb':      # from lbm to ...
        response['kg'] = value / 2.20462262

    # Print the response
    if verbose:
        print('\n{0:f} [{1}]\n\n\tis also:\n'.format(value, units))
        for converted in response.keys():
            print('{0:30.16f} [{1}]'.format(response[converted], converted))
        if '@' in request:
            print('\nmass flow at a density of {0} [{1}]'.format(dens_resp['lbm/ft3'], 'lbm/ft3'))
            for converted in mass_flow.keys():
                print('{0:30.16f} [{1}]'.format(mass_flow[converted], converted))

    return response


if __name__ == '__main__':
    result = convert('1 gal')
    # result = convert('290 gpm @ 54 lbm/ft3')
    # result = convert('54 lbm/ft3')
