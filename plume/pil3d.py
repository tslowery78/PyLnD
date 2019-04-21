import numpy as np
import vtk
import sys


class PIL3D:
    """Class representing a PILAGER3D output file."""

    def __init__(self, name):
        """Method to initialize class."""

        # Define attributes
        self.name = name
        self.pos = []
        self.Pn = []
        self.flux = []
        self.pointCloud = []
        self.readpil3d()

    def readpil3d(self):
        """Method to read in the pil3d txt file."""

        # Read the data in as an array.
        res = np.loadtxt(self.name, delimiter=' ')

        # Split into useful chunks
        self.pos = res[:, 0:3]      # Grid point locations
        self.Pn = res[:, 3:4]       # Normal pressure [Pa]
        self.flux = res[:, -1]      # Flux

    def make_point_cloud(self):
        """Method to plot the point cloud."""

        self.pointCloud = VtkPointCloud()
        for k in range(np.size(self.pos, 0)):
            self.pointCloud.addPoint(self.pos[k, :])

        # Renderer
        renderer = vtk.vtkRenderer()
        renderer.AddActor(self.pointCloud.vtkActor)
        renderer.SetBackground(.2, .3, .4)
        renderer.SetBackground(0.0, 0.0, 0.0)
        renderer.ResetCamera()

        # Render Window
        renderWindow = vtk.vtkRenderWindow()
        renderWindow.AddRenderer(renderer)

        # Interactor
        renderWindowInteractor = vtk.vtkRenderWindowInteractor()
        renderWindowInteractor.SetRenderWindow(renderWindow)

        # Begin Interaction
        renderWindow.Render()
        renderWindow.SetWindowName("XYZ Data Viewer: ")
        renderWindowInteractor.Start()


class VtkPointCloud:
    def __init__(self, zMin=-10.0, zMax=10.0, maxNumPoints=1e6):
        self.maxNumPoints = maxNumPoints
        self.vtkPolyData = vtk.vtkPolyData()
        self.clearPoints()
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(self.vtkPolyData)
        mapper.SetColorModeToDefault()
        mapper.SetScalarRange(zMin, zMax)
        mapper.SetScalarVisibility(1)
        self.vtkActor = vtk.vtkActor()
        self.vtkActor.SetMapper(mapper)

    def addPoint(self, point):
        if self.vtkPoints.GetNumberOfPoints() < self.maxNumPoints:
            pointId = self.vtkPoints.InsertNextPoint(point[:])
            self.vtkDepth.InsertNextValue(point[2])
            self.vtkCells.InsertNextCell(1)
            self.vtkCells.InsertCellPoint(pointId)
        else:
            r = np.random.randint(0, self.maxNumPoints)
            self.vtkPoints.SetPoint(r, point[:])
        self.vtkCells.Modified()
        self.vtkPoints.Modified()
        self.vtkDepth.Modified()

    def clearPoints(self):
        self.vtkPoints = vtk.vtkPoints()
        self.vtkCells = vtk.vtkCellArray()
        self.vtkDepth = vtk.vtkDoubleArray()
        self.vtkDepth.SetName('DepthArray')
        self.vtkPolyData.SetPoints(self.vtkPoints)
        self.vtkPolyData.SetVerts(self.vtkCells)
        self.vtkPolyData.GetPointData().SetScalars(self.vtkDepth)
        self.vtkPolyData.GetPointData().SetActiveScalars('DepthArray')

