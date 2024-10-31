"""
Dove-tail storage grid

Python class using CadQuery to describe storage trays that are sized to
conform to a specified grid and interlock with each other via dovetail
features on their sides.

The array of storage trays are axis aligned as follows when viewing the
storage grid from above:

X-axis: -X is left, +X is right.
Y-axis: -Y is front, +Y is rear.
Z-axis: -Z is the bottom, +Z is the top of an individual tray.

Optional ledge for labeling is tilted towards -Y and +Z because user is
expected to view the array from above and in front.
"""
import math
import cadquery as cq

class DovetailStorageGrid:
    # Dimensions (in mm) of a single cell in the grid
    def __init__(self, x, y, z,
                 tray_gap = 0.1,
                 corner_fillet = 2,
                 chamfer_top = 1, chamfer_bottom=1.5,
                 dovetail_protrusion = 2,
                 dovetail_length_fraction = 0.5,
                 dovetail_gap = 0.05):
        if tray_gap < 0:
            raise ValueError("Trays with negative gaps will not fit together.")

        self.grid_x = x
        self.grid_y = y
        self.grid_z = z
        self.tray_gap = tray_gap
        self.corner_fillet = corner_fillet
        self.chamfer_top = chamfer_top
        self.chamfer_bottom = chamfer_bottom
        self.dovetail_protrusion = dovetail_protrusion
        self.dovetail_length_fraction = dovetail_length_fraction
        self.dovetail_gap = dovetail_gap

    # Returns the nominal volume for size specified in number of grid cells.
    # Actual tray will extend beyond this volume for dovetail
    def nominal_volume(self, x=1, y=1):
        return (
            cq.Workplane("XY")
            .lineTo(0,               self.grid_y * y)
            .lineTo(self.grid_x * x, self.grid_y * y)
            .lineTo(self.grid_x * x, 0)
            .close()
            .extrude(self.grid_z)
        )

    # Feels like there should be an existing CadQuery operator for growing/
    # shrinking a shape, since the math already exists for .shell(). But
    # I haven't found it yet. In the meantime, call shell() then using the
    # result to modify original shape.
    def grow_xy_by(self, shape, amount):
        if amount < 0:
            shape = shape - shape.faces("+Z or -Z").shell(amount)
        elif amount > 0:
            shape = shape + shape.faces("+Z or -Z").shell(amount)

        return shape

    # Returns the maximum volume for size specified in number of grid cells.
    # Actual tray dovetail will not exceed this volume.
    def bounding_volume(self, x=1, y=1):
        bounds = self.grow_xy_by(self.nominal_volume(x, y), self.dovetail_protrusion)
        p = self.dovetail_protrusion
        bounds = (
            cq.Workplane("XY")
            .lineTo(-p,                   -p, forConstruction = True)
            .lineTo(-p,                    p + self.grid_y * y)
            .lineTo( p + self.grid_x * x,  p + self.grid_y * y)
            .lineTo( p + self.grid_x * x, -p)
            .close()
            .extrude(self.grid_z)
        )

        bounds = bounds.faces("+Z").chamfer(self.dovetail_protrusion + self.chamfer_top)
        bounds = bounds.faces("-Z").chamfer(self.dovetail_protrusion + self.chamfer_bottom)
        bounds = bounds.edges("not (>Z or <Z)").fillet(self.corner_fillet)
        return bounds

    # Create a trapezoidal volume for use as interlink dovetail
    def dovetail(self, width):
        return (
            cq.Workplane("XY").sketch()
            .trapezoid(
                w = width,
                h = self.dovetail_protrusion+self.tray_gap+self.dovetail_gap*2,
                a1 = 45)
            .finalize()
            .extrude(self.grid_z)
            .translate((0, -(self.dovetail_protrusion-self.tray_gap)/2,0))
            )

    # Create a trapezoidal volume for use as interlink dovetails on front
    # and back (+Y and -Y) faces
    def dovetail_y(self):
        return self.dovetail(width = self.grid_x * self.dovetail_length_fraction)

    # Create a trapezoidal volume for use as interlink dovetails on left
    # and right (+X and -X) faces
    def dovetail_x(self):
        return (
            self.dovetail(width = self.grid_y * self.dovetail_length_fraction)
            .rotate((0, 0, 0), (0, 0, 1), -90))

    # Create a tray with given size specified in number of grid cells
    def tray(self, x=1, y=1):
        tray = self.nominal_volume(x, y)
        tray = tray.edges("|Z").fillet(self.corner_fillet)
        if self.tray_gap > 0:
            tray = self.grow_xy_by(tray,-self.tray_gap)

        tray_x = x * self.grid_x
        tray_y = y * self.grid_y

        dovetail_y = self.dovetail_y()
        for x_index in range(x):
            x_position = self.grid_x/2 + x_index*self.grid_x
            tray = tray + self.grow_xy_by(dovetail_y,-self.dovetail_gap).translate((x_position, 0,      0))
            tray = tray - self.grow_xy_by(dovetail_y, self.dovetail_gap).translate((x_position, tray_y, 0))

        dovetail_x = self.dovetail_x()
        for y_index in range(y):
            y_position = self.grid_y/2 + y_index*self.grid_y
            tray = tray + self.grow_xy_by(dovetail_x,-self.dovetail_gap).translate((0,      y_position, 0))
            tray = tray - self.grow_xy_by(dovetail_x, self.dovetail_gap).translate((tray_x, y_position, 0))

        tray = tray.intersect(self.bounding_volume(x,y))

        return tray

    # Create a tray with given size specified in number of grid cells
    # Plus if there is room, cut a small area in the front suitable for a
    # label and acting as a handle.
    def label_tray(self, x=1, y=1, label_limit=10):
        nozzle_diameter = 0.4
        label_available_y = (
            (self.grid_y * (1-self.dovetail_length_fraction))/2
            - self.dovetail_gap
            - nozzle_diameter*2
        )
        label_size = min(label_available_y, label_limit/math.sqrt(2))

        tray = self.tray(x,y)

        if label_size > 0:
            tray = tray - (
                cq.Workplane("YZ")
                .lineTo(  label_size,               self.grid_z, forConstruction = True)
                .lineTo( -self.dovetail_protrusion, self.grid_z)
                .lineTo( -self.dovetail_protrusion, self.grid_z - self.dovetail_protrusion - label_size)
                .close()
                .extrude(x*self.grid_x)
            )

        return tray
