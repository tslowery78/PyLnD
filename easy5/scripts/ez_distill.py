#!/ots/sw/osstoolkit/15.4/sles12-x86_64/bin/python3.6

import argparse
from PyLnD.easy5.eztxt import EZTXT
from PyLnD.easy5.ezmf import EZMF
from PyLnD.easy5.ezmap import EZMAP
import xlwt


def write_row(row, sheet, columns, **kwargs):
    """Function to use xlwt to write all the columns of a row"""

    # Get options
    use_style = None
    if 'style' in kwargs.keys():
        use_style = kwargs['style']

    for c, col in enumerate(columns):
        if use_style:
            sheet.write(row, c, col, style=use_style)
        else:
            sheet.write(row, c, col)
        col_width = sheet.col(c).width
        try:
            if len(col)*250 > col_width:
                sheet.col(c).width = (len(col)*250)
        except TypeError:
            if len(str(col))*75 > col_width:
                sheet.col(c).width = (len(str(col))*75)

    return sheet


if __name__ == '__main__':

    # Get the command line inputs
    parser = argparse.ArgumentParser()
    parser.add_argument("-eztxt", nargs=1, help="eztxt file", required=True)
    parser.add_argument('-ezmf', nargs=1, help='ezmf file', required=True)
    parser.add_argument("-ezmap", nargs=1, help="ezmap list file")
    parser.add_argument('-xls', nargs=1, help="xls output file", required=True)
    args = parser.parse_args()
    eztxt_filename = args.eztxt
    ezmf_filename = args.ezmf
    ezmap_filename = args.ezmap
    xls_filename = args.xls

    # Setup styles
    style = xlwt.XFStyle()
    font = xlwt.Font()
    font.bold = True
    font.underline = True
    style.font = font

    # Create the eztxt, ezmf, and ezmap objects
    eztxt = EZTXT(eztxt_filename[0])
    ezmf = EZMF(ezmf_filename[0])

    try:
        ezmap = EZMAP(ezmap_filename[0])
        s_list = None
    except TypeError:
        ezmap = None

    # Echo inputs
    print("Inputs:\n")
    print("\t\teztxt: {0}".format(eztxt_filename[0]))
    print("\t\tezmf: {0}".format(ezmf_filename[0]))

    # Create the columns
    xls_columns = ['path', 'submodel name', 'submodel desc', 'component']
    xls_columns = xls_columns + ['desc', 'port_config', 'vol', 'dh', 'len', 'od', 'xln', 'dzh', 'dens', 'spht']

    # Write out distillation into a xls
    workbook = xlwt.Workbook()
    all_sheet = workbook.add_sheet("All Components")
    all_sheet = write_row(0, all_sheet, xls_columns[1:], style=style)
    if ezmap:
        print("\t\tezmap: {0}".format(ezmap_filename[0]))
        path_sheet = workbook.add_sheet(ezmap.list_file)
        path_sheet = write_row(0, path_sheet, xls_columns, style=style)
        r = 1
        for path in ezmap.paths_list:
            for i, submodel in enumerate(ezmap.paths[path]['submodels']):
                if type(submodel) is not list:
                    s_model = [submodel]
                else:
                    s_model = submodel
                for smod in s_model:
                    s_list = ezmap.paths[path][smod]
                    if type(s_list) is not list:
                        s_list = [ezmap.paths[path][smod]]
                    else:
                        s_list = ezmap.paths[path][smod]
                    row_out_lead = [path, smod.upper()]
                    row_out = row_out_lead.copy()
                    for j, component in enumerate(s_list):
                        row_out.append(eztxt.component[component.upper()]['submodel_desc'])
                        row_out.append(component.upper())
                        for xls_column in xls_columns[4:]:
                            if xls_column in eztxt.component[component.upper()].keys():
                                row_out.append(eztxt.component[component.upper()][xls_column])
                            else:
                                if component[0:2] == 'pi':
                                    if xls_column == 'dens':
                                        ez_index = ezmf.components['pi']['ids'] == component.upper()
                                        row_out.append(ezmf.components['pi']['dens'][ez_index][0])
                                    elif xls_column == 'od':
                                        ez_index = ezmf.components['pi']['ids'] == component.upper()
                                        row_out.append(ezmf.components['pi']['od'][ez_index][0])
                                    elif xls_column == 'spht':
                                        ez_index = ezmf.components['pi']['ids'] == component.upper()
                                        row_out.append(ezmf.components['pi']['spht'][ez_index][0])
                                    else:
                                        row_out.append(None)
                                else:
                                    row_out.append(None)
                        path_sheet = write_row(r, path_sheet, row_out)
                        r += 1
                        row_out = row_out_lead.copy()
    row_out = []
    r = 1
    s_list = sorted(list(eztxt.component.keys()))
    for j, component in enumerate(s_list):
        row_out.append(eztxt.component[component.upper()]['submodel_id'])
        row_out.append(eztxt.component[component.upper()]['submodel_desc'])
        row_out.append(component.upper())
        row_out.append(eztxt.component[component.upper()]['desc'])
        for xls_column in xls_columns[5:]:
            if xls_column in eztxt.component[component.upper()].keys():
                row_out.append(eztxt.component[component.upper()][xls_column])
            else:
                if component[0:2].lower() == 'pi':
                    if xls_column == 'dens':
                        ez_index = ezmf.components['pi']['ids'] == component.upper()
                        row_out.append(ezmf.components['pi']['dens'][ez_index][0])
                    elif xls_column == 'od':
                        ez_index = ezmf.components['pi']['ids'] == component.upper()
                        row_out.append(ezmf.components['pi']['od'][ez_index][0])
                    elif xls_column == 'spht':
                        ez_index = ezmf.components['pi']['ids'] == component.upper()
                        row_out.append(ezmf.components['pi']['spht'][ez_index][0])
                    else:
                        row_out.append(None)
                else:
                    row_out.append(None)
        all_sheet = write_row(r, all_sheet, row_out)
        r += 1
        row_out = []
    workbook.save(xls_filename[0])
    print("\nOutput:")
    print("\t\txls file: {0}".format(xls_filename[0]))

