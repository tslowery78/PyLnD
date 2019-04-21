def read_msf06_dofs(f06file):
    """Read the grids in the msf06 file."""
    # Read thru the f06 file looking for the table of grids.
    in_table = False
    grid_table = []
    with open(f06file) as f:
        for line in f:
            if line.__len__() >= 16:
                if line[0:16] == "0RECORD NO.    2":
                    in_table = True
                if line.__len__() > 102:
                    if line[101:105] == "END":
                        in_table = False
                if in_table and line[7] == ')':
                    grid_table.append(line.strip())
    # Extract the grids and dof from the table.
    dof_list = []
    grids = []
    dofs = []
    for i, line in enumerate(grid_table):
        if i > 0:
            grid_list = line.split()[2::5]
            grid_list = list(map(int, grid_list))
            grids.extend(grid_list)
            d_list = line.split()[3::5]
            d_list = list(map(int, d_list))
            dof_list.extend(d_list)
    # For each grid and dof make a master list of grid*dof.
    for i, grid in enumerate(grids):
        for j in range(0, dof_list[i]):
            dofs.append((grid, j + 1))
    return grids, dofs
