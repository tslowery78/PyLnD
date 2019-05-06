class EZANL:
    """Class representing a ezanl file Easy5"""

    def __init__(self, name):
        """Method to initialize the object."""

        # Initialize the parameters
        self.name = name
        self.load()

    def load(self):
        """Method to read and extract the parameters from an ezanl file."""

        # Open and read the contents
        with open(self.name) as f:
            lines = f.read().splitlines()

        # Join all the string together
        contents = ''.join(lines)
        pass


if __name__ == '__main__':
    ezanl = EZANL('model0.simulation.ezanl')

    pass
