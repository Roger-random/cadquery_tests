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
from cadquery import exporters
from placeholders import bearing, spool

# When not running in CQ-Editor, turn log into print
if "log" not in globals():

    def log(*args):
        print(args)


class acrylic_bottom_panel:
    """
    Class consolidating math related to using an acrylic panel in the bottom
    as an alternative to a solid slab of 3D printed plastic.
    """

    @staticmethod
    def preset_mhtest():
        return acrylic_bottom_panel(
            length=190, width=60, thickness=2.7, corner_radius=20, border=2.4
        )

    def __init__(
        self,
        length,
        width,
        thickness,
        corner_radius,
        lip_thickness=1.6,
        lip_depth=2.4,
        border=3,
    ):
        self.length = length
        self.width = width
        self.thickness = thickness
        self.corner_radius = corner_radius
        self.lip_thickness = lip_thickness
        self.lip_depth = lip_depth
        self.border = border

        self.calculate_minimum_dimensions()

    def placeholder(self):
        """
        Returns a solid representing a sheet of acrylic cut to the parameters
        given in our constructor.
        """
        half_length = self.length / 2
        half_width = self.width / 2
        quarter = (
            cq.Workplane("XY")
            .lineTo(0, half_length)
            .lineTo(half_width - self.corner_radius, half_length)
            .tangentArcPoint(
                (half_width, half_length - self.corner_radius), relative=False
            )
            .lineTo(half_width, 0)
            .close()
            .extrude(self.thickness / 2, both=True)
        )

        return filament_bag_base.quarter_to_whole(quarter)

    def exportDXF(self, filename="./tray_bottom_acrylic_panel.dxf"):
        """
        Export placeholder solid to DXF outline for laser cutting
        """
        exporters.exportDXF(self.placeholder().section(), filename)

    def opening_cutter(self):
        """
        Returns a solid that can be used in a geometric subtraction operation
        to cut a window area to fit the acrylic panel.
        """
        cutter_half_length = self.length / 2 - self.lip_depth
        cutter_half_width = self.width / 2 - self.lip_depth
        cutter_radius = self.corner_radius - self.lip_depth

        window_quarter = (
            cq.Workplane("XY")
            .lineTo(0, cutter_half_length)
            .lineTo(cutter_half_width - cutter_radius, cutter_half_length)
            .tangentArcPoint(
                (cutter_half_width, cutter_half_length - cutter_radius), relative=False
            )
            .lineTo(cutter_half_width, 0)
            .close()
            .extrude(self.thickness * 4, both=True)
        )

        window = filament_bag_base.quarter_to_whole(window_quarter)

        cutter = window + self.placeholder()

        return cutter

    def calculate_minimum_dimensions(self):
        """
        Based on parameters given in the constructor, calculate minimum
        dimensions necessary to accommodate this panel
        """
        self.minimum_length = self.length + self.border * 2
        self.minimum_width = self.width + self.border * 2
        self.minimum_thickness = self.thickness + self.lip_thickness * 2
        self.minimum_radius = self.corner_radius + self.border


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
        panel = acrylic_bottom_panel.preset_mhtest()

        wall_thickness = 0.8
        chamfer_room_bottom_thickness = (
            panel.minimum_thickness
            + panel.lip_depth
            + panel.border
            - wall_thickness
            - panel.lip_thickness
        )

        instance = filament_bag_base(
            spool.preset_mhbuild(),
            bearing.preset_608(),
            bottom_x=panel.minimum_width / 2,
            bottom_y=panel.minimum_length / 2,
            bottom_corner_radius=panel.minimum_radius,
            bottom_thickness=chamfer_room_bottom_thickness,
            bottom_height_below_spool=40,
            tray_wall_thickness=wall_thickness,
        )
        instance.calculate_perimeter()
        instance.generate_bearing_support()
        instance.generate_dessicant_grate()
        instance.generate_filament_exit_subtract()

        assemble_base = (
            instance.tray_perimeter
            + instance.bottom
            + instance.bearing_support
            + instance.dessicant_shelf
            - instance.filament_exit_subtract
            - panel.opening_cutter().translate(
                (0, 0, instance.tray_bottom_z + panel.minimum_thickness / 2)
            )
        )
        assemble_base = assemble_base.edges(
            sel.NearestToPointSelector(
                (
                    0,
                    0,
                    instance.tray_bottom_z + chamfer_room_bottom_thickness,
                )
            )
        ).chamfer(panel.lip_depth + panel.border - wall_thickness - 0.3)

        assemble_base = assemble_base.edges(
            sel.NearestToPointSelector(
                (panel.minimum_width / 2, 0, instance.tray_bottom_z)
            )
        ).fillet(panel.border)

        instance.base = assemble_base
        instance.panel_placeholder = panel.placeholder().translate(
            (0, 0, instance.tray_bottom_z + panel.minimum_thickness / 2)
        )

        return instance

    def __init__(
        self,
        spool: spool,
        bearing: bearing,
        bottom_x,
        bottom_y,
        bottom_corner_radius,
        bottom_thickness=1.2,
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
        self.bottom_x = bottom_x
        self.bottom_y = bottom_y
        self.bottom_corner_radius = bottom_corner_radius
        self.bottom_thickness = bottom_thickness
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

    @staticmethod
    def quarter_to_whole(quarter):
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
        self.bottom_corner = self.bottom_corner_path().extrude(self.bottom_thickness)

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
        self.tray_inner = self.tray_inner.faces("+Z").chamfer(self.tray_margin / 2)

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
    show_object(
        fbb.panel_placeholder,
        options={"color": "white", "alpha": 0.1},
    )
