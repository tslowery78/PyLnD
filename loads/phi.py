from PyLnD.loads.read_f06 import read_msf06_dofs
from PyLnD.loads.read_op4 import read_op4_phi


class PHI:
    """Normal modes matrix object."""

    def __init__(self, op4file, f06file):
        """Initializing the PHI object attributes.

            Ex:  PHI(op4file, f06file)
        """
        self.op4file = op4file
        self.f06file = f06file
        # Extract the dof from the mode shape f06 file.
        self.grids, self.dofs = read_msf06_dofs(self.f06file)
        # Extract the mode shapes from the binary op4 file.
        self.phi_name, self.phi = read_op4_phi(self.op4file)
        self.num_dofs, self.num_modes = self.phi.shape
        if self.dofs.__len__() != self.num_dofs:
            raise Exception("The number of dofs in the binary op4 and the f06 are not the same !!!\n"
                            "\tNumber of PHI dofs: " + self.num_dofs.__str__() + "\n"
            + "\tNumber of F06 dofs: " + self.dofs.__len__().__str__())
