"""
MIT License

Copyright (c) 2024 Roger Cheng

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import math
import cadquery as cq
import cadquery.selectors as sel

# When not running in CQ-Editor, turn log into print
if "log" not in globals():

    def log(*args):
        print(args)


class bearing:
    """
    Placeholder for a bearing for the purpose of design layout and
    visualization. No need to print this - use real bearings!
    """

    @staticmethod
    def preset_608():
        """
        Create an instance with dimensions of generic 608 bearings
        """
        return bearing(
            diameter_outer=22,
            diameter_inner=8,
            width=7,
        )

    def __init__(
        self,
        diameter_outer,
        diameter_inner,
        width,
    ):
        self.diameter_outer = diameter_outer
        self.diameter_inner = diameter_inner
        self.width = width

    def placeholder(self):
        return (
            cq.Workplane("YZ")
            .circle(self.diameter_outer / 2)
            .circle(self.diameter_inner / 2)
            .extrude(self.width)
            .translate((-self.width / 2, 0, 0))
        )


class spool:
    """
    Placeholder for a filament spool for the purpose of design layout and
    visualization. No need to print this - use real spools!
    """

    @staticmethod
    def preset_jesse():
        """
        Create an instance with dimensions of Printed Solid Jesse
        """
        return spool(
            diameter_outer=200,
            diameter_inner=55,
            width=72.5,
            side_thickness=5,
        )

    @staticmethod
    def preset_mhbuild():
        """
        Create an instance with dimensions of MatterhHackers Build
        """
        return spool(
            diameter_outer=200,
            diameter_inner=55,
            width=67.5,
            side_thickness=5,
        )

    @staticmethod
    def preset_esun3kg():
        """
        Create an instance with dimensions of eSun 3kg
        """
        return spool(
            diameter_outer=270,
            diameter_inner=52.5,
            width=100,
            side_thickness=7,
        )

    def __init__(
        self,
        diameter_outer,
        diameter_inner,
        width,
        side_thickness,
    ):
        self.diameter_outer = diameter_outer
        self.width = width
        self.side_thickness = side_thickness
        self.diameter_inner = diameter_inner

    def placeholder(self):
        """
        Generate a shape centered around origin that is a visual representation
        (not intended for printing) of a filament spool.
        """
        center = (
            cq.Workplane("YZ")
            .circle(self.diameter_inner / 2 + self.side_thickness)
            .circle(self.diameter_inner / 2)
            .extrude(self.width / 2)
        )

        side = (
            cq.Workplane("YZ")
            .transformed(offset=cq.Vector(0, 0, self.width / 2))
            .circle(self.diameter_outer / 2)
            .circle(self.diameter_inner / 2 + self.side_thickness)
            .extrude(-self.side_thickness)
        )

        half = center + side

        spool = half + half.mirror("YZ")

        return spool


class filament_bag_base:
    """
    A 3D printed base that serves as a filament dispensing container and can
    become a dry box in conjunction with the bag that the filament came in.
    Put some dessicant on the bottom, put the bag on top, then packing tape
    around the sides to create an airtight(-ish) seal between the bag and the
    base. Assuming the bag is not already torn, becase if it was then the
    filament is starting on the wrong foot for staying dry.
    """

    @staticmethod
    def preset_mhbuild():
        instance = filament_bag_base(
            spool.preset_mhbuild(),
            bearing.preset_608(),
            bottom_x=35,
            bottom_y=100,
            bottom_corner_radius=25,
            bottom_height_below_spool=30,
        )
        instance.calculate_perimeter()
        instance.generate_bearing_support()
        instance.generate_dessicant_grate()
        instance.generate_filament_exit_subtract()

        instance.base = (
            instance.tray_perimeter
            + instance.bottom
            + instance.bearing_support
            + instance.dessicant_shelf
            - instance.filament_exit_subtract
        )

        return instance

    def __init__(
        self,
        spool: spool,
        bearing: bearing,
        bottom_x,
        bottom_y,
        bottom_corner_radius,
        bearing_separation_angle=30,
        tray_margin=5,
        top_height_above_bearing=10,
        tray_top_corner_radius=25,
        top_vertical_height=45,
        bottom_height_below_spool=30,
        tray_wall_thickness=0.8,
        axle_hook_height=0.5,
        filament_exit_diameter=5.5,
        dessicant_grate_height=3,
    ):
        # Remember our given parameters
        self.spool = spool
        self.bearing = bearing
        self.bearing_separation_angle = bearing_separation_angle
        self.tray_margin = tray_margin
        self.top_height_above_bearing = top_height_above_bearing
        self.tray_top_corner_radius = tray_top_corner_radius
        self.top_vertical_height = top_vertical_height
        self.bottom_height_below_spool = bottom_height_below_spool
        self.bottom_corner_radius = bottom_corner_radius
        self.bottom_x = bottom_x
        self.bottom_y = bottom_y
        self.tray_wall_thickness = tray_wall_thickness
        self.axle_hook_height = axle_hook_height
        self.filament_exit_diameter = filament_exit_diameter
        self.dessicant_grate_height = dessicant_grate_height

        # Make use of those parameters for additional setup calculations
        self.calculate_dimensions()

    def calculate_dimensions(self):
        """
        Once parameters are set in the constructor, we can derive
        dimensions that can be referenced during construction
        """
        # Values calculated from given parameters
        self.spool_offset_z = self.spool.diameter_outer / 2
        self.spool_offset = (0, 0, self.spool_offset_z)
        self.bearing_distance = (
            self.spool.diameter_outer / 2 + self.bearing.diameter_outer / 2
        )
        self.bearing_offset_x = self.spool.width / 2 - self.spool.side_thickness / 2
        self.bearing_offset_y = (
            math.sin(math.radians(self.bearing_separation_angle))
            * self.bearing_distance
        )
        self.bearing_offset_z = self.spool_offset_z - (
            math.cos(math.radians(self.bearing_separation_angle))
            * self.bearing_distance
        )
        self.bearing_offset = (
            self.bearing_offset_x,
            self.bearing_offset_y,
            self.bearing_offset_z,
        )
        self.tray_top_x = self.spool.width / 2 + self.tray_margin
        self.tray_top_y = self.spool.diameter_outer / 2 + self.tray_margin
        self.tray_top_z = (
            self.bearing_offset_z
            + self.bearing.diameter_outer / 2
            + self.top_height_above_bearing
        )
        self.tray_bottom_z = -self.bottom_height_below_spool

    def top_corner_outer_path(self, firstLineConstruction: bool):
        """
        Only the outer perimeter portion of top_corner_path, not closed.
        """
        return (
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(0, 0, self.tray_top_z))
            .lineTo(0, self.tray_top_y, forConstruction=firstLineConstruction)
            .lineTo(self.tray_top_x - self.tray_top_corner_radius, self.tray_top_y)
            .tangentArcPoint(
                (self.tray_top_x, self.tray_top_y - self.tray_top_corner_radius),
                relative=False,
            )
            .lineTo(self.tray_top_x, 0)
        )

    def top_corner_path(self):
        """
        Closed path for one quarter of top section
        """
        return self.top_corner_outer_path(firstLineConstruction=False).close()

    def bottom_corner_path(self):
        """
        Closed path for one quarter of bottom section
        """
        return (
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(0, 0, self.tray_bottom_z))
            .lineTo(0, self.bottom_y)
            .lineTo(self.bottom_x - self.bottom_corner_radius, self.bottom_y)
            .tangentArcPoint(
                (self.bottom_x, self.bottom_y - self.bottom_corner_radius),
                relative=False,
            )
            .lineTo(self.bottom_x, 0)
            .close()
        )

    def quarter_to_whole(self, quarter):
        """
        Given an object representing a quarter of the shape, mirror it about
        YZ and XZ planes to create the whole shape.
        """
        half = quarter + quarter.mirror("YZ")
        return half + half.mirror("XZ")

    def create_flat_bottom(self):
        """
        Create a flat bottom intended for 3D printing
        """
        self.bottom_corner = self.bottom_corner_path().extrude(1.2)

        self.bottom = self.quarter_to_whole(self.bottom_corner)

    def calculate_perimeter(self):
        """
        Returns CadQuery object that is the bottom tray, majority of the
        filament base.
        """
        top_outer_corner = self.top_corner_path().extrude(-self.top_vertical_height)

        self.create_flat_bottom()

        fairing_outer_corner = (
            top_outer_corner.faces("<Z").add(self.bottom_corner.faces(">Z")).loft()
        )

        self.tray_outer = self.quarter_to_whole(top_outer_corner + fairing_outer_corner)
        self.tray_shell = self.tray_outer.faces("+Z or -Z").shell(
            -self.tray_wall_thickness
        )
        self.tray_inner = self.tray_outer - self.tray_shell
        self.tray_inner = self.tray_inner.faces("+Z or -Z").chamfer(
            self.tray_margin / 2
        )

        self.tray_perimeter = self.tray_outer - self.tray_inner

    def generate_filament_exit_subtract(self):
        self.filament_exit_subtract = (
            cq.Workplane("XZ")
            .transformed(
                offset=cq.Vector(
                    0,
                    self.bearing_offset_z
                    - self.bearing.diameter_outer / 2
                    + self.filament_exit_diameter / 2,
                    0,
                )
            )
            .circle(self.filament_exit_diameter / 2)
            .extrude(self.tray_top_y)
        )

    def generate_bearing_support(self):
        """
        Generate the U shape that will support bearing axle, as well as the
        bearing axle itself.
        """

        printable_intersect = (
            cq.Workplane("YZ")
            .transformed(
                offset=cq.Vector(
                    self.bearing_offset_y,
                    self.bearing_offset_z,
                    self.tray_top_x - self.tray_wall_thickness,
                )
            )
            .rect(
                self.bearing.diameter_inner - 1,
                self.bearing.diameter_outer + self.spool.side_thickness,
            )
            .extrude(-self.tray_top_x)
        )

        cone_height = (
            self.tray_margin
            - self.tray_wall_thickness
            + self.spool.side_thickness / 2
            - self.bearing.width / 2
        )
        cone = (
            cq.Workplane("YZ")
            .transformed(
                offset=cq.Vector(
                    self.bearing_offset_y,
                    self.bearing_offset_z,
                    self.tray_top_x - self.tray_wall_thickness,
                )
            )
            .circle(self.bearing.diameter_outer / 2)
            .workplane(offset=-cone_height)
            .circle(1 + self.bearing.diameter_inner / 2)
            .loft()
        )

        slot_width_half = self.bearing.diameter_inner / 2
        slotted = (
            cq.Workplane("YZ")
            .transformed(
                offset=cq.Vector(
                    self.bearing_offset_y,
                    self.bearing_offset_z,
                    self.tray_top_x - self.tray_wall_thickness,
                )
            )
            .lineTo(0, self.bearing.diameter_outer, forConstruction=True)
            .lineTo(slot_width_half, self.bearing.diameter_outer)
            .lineTo(slot_width_half, 0)
            .tangentArcPoint((-slot_width_half, 0), relative=False)
            .lineTo(-slot_width_half, self.bearing.diameter_outer)
            .close()
            .workplane(offset=-cone_height)
            .lineTo(0, self.bearing.diameter_outer, forConstruction=True)
            .lineTo(
                slot_width_half - self.axle_hook_height, self.bearing.diameter_outer
            )
            .lineTo(slot_width_half - self.axle_hook_height, 0)
            .tangentArcPoint(
                (-slot_width_half + self.axle_hook_height, 0), relative=False
            )
            .lineTo(
                -slot_width_half + self.axle_hook_height, self.bearing.diameter_outer
            )
            .close()
            .loft()
            .intersect(printable_intersect)
            .rotate(
                (self.bearing_offset_x, self.bearing_offset_y, self.bearing_offset_z),
                (
                    self.bearing_offset_x + 1,
                    self.bearing_offset_y,
                    self.bearing_offset_z,
                ),
                self.bearing_separation_angle,
            )
        )

        self.bearing_support = self.quarter_to_whole(cone - slotted)

        ideal_axle_half = (
            cq.Workplane("YZ")
            .transformed(
                offset=cq.Vector(
                    self.bearing_offset_y,
                    self.bearing_offset_z,
                    self.tray_top_x - self.tray_wall_thickness,
                )
            )
            .circle(self.bearing.diameter_inner / 2)
            .workplane(offset=-cone_height)
            .circle(self.bearing.diameter_inner / 2 - self.axle_hook_height)
            .loft()
            .faces("-X")
            .workplane()
            .circle(self.bearing.diameter_inner / 2)
            .extrude(self.bearing.width)
            .faces("-X")
            .workplane()
            .circle(1 + self.bearing.diameter_inner / 2)
            .workplane(offset=0.5)
            .circle(self.bearing.diameter_outer / 2)
            .loft()
            .faces("-X")
            .workplane()
            .circle(self.bearing.diameter_outer / 2)
            .workplane(offset=self.spool.side_thickness / 2)
            .circle(self.spool.side_thickness / 2 + self.bearing.diameter_outer / 2)
            .loft()
            .faces("-X")
            .workplane()
            .circle((self.bearing.diameter_outer + self.bearing.diameter_inner) / 4)
            .extrude(
                self.tray_top_x
                - self.tray_wall_thickness
                - cone_height
                - self.bearing.width
                - 0.5
                - self.spool.side_thickness / 2
            )
        )

        # Sadly the ideal axle shape is difficult to print on FDM printer, so
        # take a slice to make it easy to lie flat on the print bed
        printable_axle_half = ideal_axle_half.intersect(printable_intersect).rotate(
            (self.bearing_offset_x, self.bearing_offset_y, self.bearing_offset_z),
            (
                self.bearing_offset_x + 1,
                self.bearing_offset_y,
                self.bearing_offset_z,
            ),
            self.bearing_separation_angle,
        )

        self.bearing_axle = printable_axle_half + printable_axle_half.mirror("YZ")

    def generate_dessicant_grate(self):
        """
        Generate a shape that, when printed with no top or bottom layers,
        turns infill into a grate to keep loose dessicant in place.
        Also generates the shelf that needs to be added to the perimeter to
        hold this grate.
        """
        grate_top_z = (
            self.bearing_offset_z
            - self.bearing.diameter_outer / 2
            - self.spool.side_thickness / 2
        )
        shelf_size = self.tray_margin / 2
        shelf_profile = (
            cq.Workplane("YZ")
            .lineTo(self.tray_top_y, grate_top_z + shelf_size, forConstruction=True)
            .lineTo(
                self.tray_top_y - shelf_size - self.dessicant_grate_height / 2,
                grate_top_z - self.dessicant_grate_height / 2,
            )
            .lineTo(
                self.tray_top_y - shelf_size - self.dessicant_grate_height / 2,
                grate_top_z - self.dessicant_grate_height,
            )
            .lineTo(
                self.tray_top_y,
                grate_top_z - shelf_size - self.dessicant_grate_height * 1.5,
            )
            .close()
        )
        self.dessicant_shelf = self.quarter_to_whole(
            shelf_profile.sweep(self.top_corner_outer_path(firstLineConstruction=True))
        )

        self.dessicant_grate = (
            self.quarter_to_whole(
                self.top_corner_path()
                .extrude(-self.dessicant_grate_height)
                .translate((0, 0, grate_top_z - self.tray_top_z))
            )
            - self.dessicant_shelf
        )

    def show_placeholders(
        self,
        show_object_options={"color": "gray", "alpha": 0.8},
    ):
        """
        If running in CQ-Editor, where show_object() is defined in global
        namespace, show all placeholder objects at their appropriate locations
        with the given options. (Default of mostly transparent gray.)

        When not running in CQ-Editor, does nothing and returns to caller.
        """
        if "show_object" in globals():

            show_object(
                self.spool.placeholder().translate(self.spool_offset),
                options=show_object_options,
            )

            positioned_bearing = self.bearing.placeholder().translate(
                self.bearing_offset
            )
            show_object(
                positioned_bearing,
                options=show_object_options,
            )
            show_object(
                positioned_bearing.mirror("XZ"),
                options=show_object_options,
            )
            show_object(
                positioned_bearing.mirror("YZ"),
                options=show_object_options,
            )
            show_object(
                positioned_bearing.mirror("XZ").mirror("YZ"),
                options=show_object_options,
            )


if "show_object" in globals():
    fbb = filament_bag_base.preset_mhbuild()
    fbb.show_placeholders()
    show_object(
        fbb.base,
        options={"color": "blue", "alpha": 0.5},
    )
    show_object(
        fbb.bearing_axle,
        options={"color": "green", "alpha": 0.5},
    )
    show_object(
        fbb.bearing_axle.mirror("XZ"),
        options={"color": "green", "alpha": 0.5},
    )

    show_object(
        fbb.dessicant_grate,
        options={"color": "red", "alpha": 0.5},
    )
