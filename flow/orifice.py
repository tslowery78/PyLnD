from PyLnD.utilities.convert import convert
import numpy as np


def orifice_size(flow_rate, dens, dp, cd, units):
    """Function to find the area and diameter of a circular orifice based
        on flow conditions to effect a dp.

        flow_rate:  either volumetric or mass flow rate
        dens:  density of the fluid at the target temperature
        dp: pressure drop across the orifice
        cd: discharge coefficient
        units:  list of strings that belong to the above values.
        
        solving for area / dia:  cd * area = Q * sqrt(rho_w / 2 * dp)
            rho_w: weight density [lbf/in3]"""

    # Echo the current inputs
    print('\nOrifice Flow Conditions:')
    print('\t{0}: {2:f} [{1}]'.format('flow rate', units[0], flow_rate))
    print('\t{0}: {2:f} [{1}]'.format('density', units[1], dens))
    print('\t{0}: {2:f} [{1}]'.format('dp', units[2], dp))
    print('\t{0}: {1:f}'.format('cd', cd))

    # Convert to compatible units

    # Flow rate needs to be in in3/sec
    vol_flow_conversions = convert(str(flow_rate) + ' ' + units[0], verbose=False)
    flow_rate = vol_flow_conversions['in3/sec']

    # Density needs to be a weight density lbf/in3
    dens_conversions = convert(str(dens) + ' ' + units[1], verbose=False)
    dens = dens_conversions['lbf/in3']

    # delta Pressure needs to be psi
    dp_conversions = convert(str(dp) + ' ' + units[2], verbose=False)
    dp = dp_conversions['psi']

    # Calculate the orifice area and diameter
    area = (flow_rate * np.sqrt(dens / (2 * dp))) / cd
    dia = 2 * np.sqrt(area / np.pi)

    # Print out the results
    print('\narea: {0} [in2]'.format(area))
    print('diameter: {0} [in]'.format(dia))

    return area, dia


if __name__ == '__main__':
    [A, d] = orifice_size(300, 54, 2, 0.61, ['gpm', 'lbm/ft3', 'psi'])
