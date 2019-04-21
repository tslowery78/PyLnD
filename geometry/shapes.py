import math


class CYLINDER:
    """Class of representing a cylinder and it's attributes.
            ex:  cyl = CYLINDER(d=5, h=1)
                 cyl = CYLINDER(r=3, h=2)
    """
    
    def __init__(self, **kwargs):
        """Method to initialize the cylinder."""
        
        # Initialize attributes
        self.volume = 0
        self.radius = 0
        self.diameter = 0
        self.height = 0

        # Get the keyword arguments
        if 'd' in kwargs.keys():
            self.diameter = kwargs['d']
            self.radius = self.diameter / 2
        elif 'r' in kwargs.keys():
            self.radius = kwargs['r']
        else:
            print(self.__doc__)
            raise Exception('You must provide a radius or diameter')
        if 'h' in kwargs.keys():
            self.height = kwargs['h']
        else:
            print(self.__doc__)
            raise Exception('You must provide a height')
                       
        # Find the volume of a cylinder
        self.calculate_volume()
        
        # Print out inputs and attributes
        self.print_info()
        
    def calculate_volume(self):
        """Method to calculate the volume of a cylinder."""
        
        # Calculate the volume
        self.volume = math.pi * self.radius**2 * self.height

    def print_info(self):
        """Method to print out the inputs and attributes."""
        
        # Print the inputs
        print('cylinder:\n\tradius: {0}\n\tdiameter: {1}\n\theight: {2}\n'.
              format(self.radius, self.diameter, self.height))

        # Print the attributes
        print('\tattributes:\n\tvolume: {0}\n'.format(self.volume))


if __name__ == '__main__':
    cyl = CYLINDER(h=6, d=2)
