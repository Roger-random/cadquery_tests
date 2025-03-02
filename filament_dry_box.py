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


class filament_dry_box:
    """
    3D-printed filaments tend to pick up moisture to varying degrees (depending
    on chemical formulation) and that moisture interferes with the process of
    printing. Sometimes the interference is negligible and can be safely
    ignored but not always. There are lots of solutions floating around the
    internet for keeping filament dry. Here is my take building something
    tailored to my personal preferences.
    """

    def __init__(
        self,
        spool_diameter=200,
        spool_diameter_margin=3.4,
        spool_width=70,
        spool_width_margin=5,
        shell_thickness=1.6,
        shell_top_radius=50,
        shell_bottom_radius=25,
        bottom_extra_height=40,
        lid_height=10,
    ):
        self.spool_diameter = spool_diameter
        self.spool_diameter_margin = spool_diameter_margin
        self.spool_volume_radius = spool_diameter / 2 + spool_diameter_margin
        self.spool_width = spool_width
        self.spool_width_margin = spool_width_margin
        self.spool_volume_width = spool_width / 2 + spool_width_margin
        self.shell_thickness = shell_thickness
        self.shell_top_radius = shell_top_radius
        self.shell_bottom_radius = shell_bottom_radius
        self.bottom_extra_height = bottom_extra_height
        self.lid_height = lid_height

        # Debug output text describes print bed size requirement
        log(
            "Print bed requirements: {0}mm x {1}mm".format(
                self.spool_volume_radius * 2
                + bottom_extra_height
                + shell_thickness * 2,
                self.spool_volume_radius * 2 + shell_thickness * 2,
            )
        )

    def spool_placeholder(self, spool_side_thickness=5):
        """
        Generate a shape centered around origin that is a visual representation
        (not intended for printing) of the filament spool we want to enclose.
        """
        center = (
            cq.Workplane("YZ")
            .circle(self.spool_diameter / 4)
            .circle(self.spool_diameter / 4 - spool_side_thickness)
            .extrude(self.spool_width / 2)
        )

        side = (
            cq.Workplane("YZ")
            .transformed(offset=cq.Vector(0, 0, self.spool_width / 2))
            .circle(self.spool_diameter / 2)
            .circle(self.spool_diameter / 4 - spool_side_thickness)
            .extrude(-spool_side_thickness)
        )

        half = center + side

        spool = half + half.mirror("YZ")

        return spool

    def box_perimeter_path(self):
        """
        Path describing the shape of enclosed volume. Used to sweep the outer
        perimeter as well as generating the flat side panels.
        """
        return (
            cq.Workplane("YZ")
            .lineTo(0, self.spool_volume_radius, forConstruction=True)
            .lineTo(
                self.spool_volume_radius - self.shell_top_radius,
                self.spool_volume_radius,
            )
            .radiusArc(
                (
                    self.spool_volume_radius,
                    self.spool_volume_radius - self.shell_top_radius,
                ),
                self.shell_top_radius,
            )
            .lineTo(
                self.spool_volume_radius,
                self.shell_bottom_radius
                - self.spool_volume_radius
                - self.bottom_extra_height,
            )
            .radiusArc(
                (
                    self.spool_volume_radius - self.shell_bottom_radius,
                    -self.spool_volume_radius - self.bottom_extra_height,
                ),
                self.shell_bottom_radius,
            )
            .line(-self.spool_volume_radius + self.shell_bottom_radius, 0)
        )

    def fully_closed_side(self, wall_thickness=0.6):
        """
        Featureless enclosed side panel of specified thickness
        """
        profile = (
            cq.Workplane("XZ")
            .lineTo(
                self.spool_volume_width, self.spool_volume_radius, forConstruction=True
            )
            .line(0, self.shell_thickness)
            .line(wall_thickness, -wall_thickness)
            .line(-wall_thickness, 0)
            .close()
        )

        rim = profile.sweep(self.box_perimeter_path())

        panel_top_edge = (
            self.spool_volume_radius + self.shell_thickness - wall_thickness
        )
        panel_top_radius = self.shell_top_radius + self.shell_thickness - wall_thickness
        panel_bottom_radius = (
            self.shell_bottom_radius + self.shell_thickness - wall_thickness
        )
        panel = (
            cq.Workplane("YZ")
            .transformed(offset=(0, 0, self.spool_volume_width))
            .lineTo(0, panel_top_edge, forConstruction=True)
            .lineTo(panel_top_edge - panel_top_radius, panel_top_edge)
            .radiusArc(
                (panel_top_edge, panel_top_edge - panel_top_radius), panel_top_radius
            )
            .lineTo(
                panel_top_edge,
                -self.spool_volume_radius
                - self.bottom_extra_height
                + self.shell_bottom_radius,
            )
            .radiusArc(
                (
                    self.spool_volume_radius - self.shell_bottom_radius,
                    -self.spool_volume_radius
                    - self.bottom_extra_height
                    - self.shell_thickness
                    + wall_thickness,
                ),
                panel_bottom_radius,
            )
            .line(
                -self.spool_volume_radius
                + panel_bottom_radius
                + wall_thickness
                - self.shell_thickness,
                0,
            )
            .close()
            .extrude(wall_thickness)
        )

        panel_half = rim + panel

        return panel_half

    def cross_tiled_lid_side(
        self,
        tile_lip_thickness=0.8,
        tile_lip_depth=1.6,
        tile_length=56,
        tile_width=29,
        tile_thickness=3.2,
        tile_spacing=2.4,
    ):
        side_thickness = tile_thickness + tile_lip_thickness * 2

        panel_half = self.fully_closed_side(side_thickness)

        panel = panel_half + panel_half.mirror("XZ")

        sine45 = math.sin(math.radians(45))
        tile_square_side = tile_length * sine45 + tile_width * sine45 + tile_spacing

        available_width = (
            self.spool_volume_radius + self.shell_thickness - side_thickness
        ) * 2
        available_height = available_width + self.bottom_extra_height

        max_tiles_horiz = math.floor(available_width / tile_square_side)
        max_tiles_vert = math.floor(available_height / tile_square_side)

        extra_spacing_horiz = (
            available_width - max_tiles_horiz * tile_square_side
        ) / max_tiles_horiz
        extra_spacing_vert = (
            available_height - max_tiles_vert * tile_square_side
        ) / max_tiles_vert

        extra_spacing = min(extra_spacing_horiz, extra_spacing_vert)

        tile_subtract = (
            cq.Workplane("YZ")
            .transformed(rotate=cq.Vector(0, 0, 45))
            .box(tile_length, tile_width, tile_thickness)
            .box(
                tile_length - tile_lip_depth * 2,
                tile_width - tile_lip_depth * 2,
                side_thickness * 2,
            )
            .edges("|X")
            .fillet(1)
            .translate((self.spool_volume_width + side_thickness / 2, 0, 0))
        )

        tile_row_width = (tile_square_side + extra_spacing) * max_tiles_horiz
        tile_row_wide_start = (
            -tile_row_width / 2 + tile_square_side / 2 + extra_spacing / 2
        )
        tile_row_wide = tile_subtract.translate((0, tile_row_wide_start, 0))
        for x in range(1, max_tiles_horiz):
            tile_row_wide = tile_row_wide + tile_subtract.translate(
                (0, tile_row_wide_start + x * (tile_square_side + extra_spacing), 0)
            )
        tile_row_wide = tile_row_wide.mirror("XZ")

        tile_row_narrow_start = (
            tile_row_wide_start + tile_square_side / 2 + extra_spacing / 2
        )
        tile_row_narrow = tile_subtract.translate((0, tile_row_narrow_start, 0))
        for x in range(1, max_tiles_horiz - 1):
            tile_row_narrow = tile_row_narrow + tile_subtract.translate(
                (0, tile_row_narrow_start + x * (tile_square_side + extra_spacing), 0)
            )

        tile_column_height = (
            tile_square_side + extra_spacing
        ) * max_tiles_vert - tile_square_side / 2

        lowest_row_z = -tile_column_height / 2 - extra_spacing / 2

        for z in range(max_tiles_vert):
            panel = panel - tile_row_wide.translate(
                (0, 0, lowest_row_z + (tile_square_side + extra_spacing) * z)
            )

        for z in range(max_tiles_vert - 1):
            panel = panel - tile_row_narrow.translate(
                (
                    0,
                    0,
                    lowest_row_z + (tile_square_side + extra_spacing) * (z + 0.5),
                )
            )

        return panel

    def single_panel_side(
        self,
        panel_lip_thickness=1.6,
        panel_lip_depth=2.4,
        panel_thickness=2.8,
        panel_border=3,
    ):
        side_thickness = panel_thickness + panel_lip_thickness * 2

        # Dimensions driven by panel lip parameters
        # panel_edge_compensation = self.shell_thickness - side_thickness - panel_border

        # Dimensions for reusing acrylic panels already cut to different parameters
        panel_edge_compensation = (
            self.shell_thickness
            - (panel_thickness + 0.8 * 2)
            - panel_border
            - (3.2 - panel_thickness)
        )
        panel_edge_top_and_sides = self.spool_volume_radius + panel_edge_compensation
        panel_opening_edge_compensation = panel_edge_compensation - panel_lip_depth
        panel_opening_top_and_sides = (
            self.spool_volume_radius + panel_opening_edge_compensation
        )

        printed_half = self.fully_closed_side(side_thickness)
        printed = printed_half + printed_half.mirror("XZ")

        panel_half = (
            cq.Workplane("YZ")
            .lineTo(0, panel_edge_top_and_sides)
            .lineTo(
                self.spool_volume_radius - self.shell_top_radius,
                panel_edge_top_and_sides,
            )
            .radiusArc(
                (
                    panel_edge_top_and_sides,
                    self.spool_volume_radius - self.shell_top_radius,
                ),
                self.shell_top_radius + panel_edge_compensation,
            )
            .lineTo(
                panel_edge_top_and_sides,
                -self.spool_volume_radius
                - self.bottom_extra_height
                + self.shell_bottom_radius,
            )
            .radiusArc(
                (
                    self.spool_volume_radius - self.shell_bottom_radius,
                    -panel_edge_top_and_sides - self.bottom_extra_height,
                ),
                self.shell_bottom_radius + panel_edge_compensation,
            )
            .lineTo(0, -panel_edge_top_and_sides - self.bottom_extra_height)
            .close()
            .extrude(panel_thickness / 2, both=True)
        )

        panel = panel_half + panel_half.mirror("XZ")
        self.panel_outline = panel.section()
        panel = panel.translate((self.spool_volume_width + side_thickness / 2, 0, 0))

        panel_opening_half = (
            cq.Workplane("YZ")
            .lineTo(0, panel_opening_top_and_sides)
            .lineTo(
                self.spool_volume_radius - self.shell_top_radius,
                panel_opening_top_and_sides,
            )
            .radiusArc(
                (
                    panel_opening_top_and_sides,
                    self.spool_volume_radius - self.shell_top_radius,
                ),
                self.shell_top_radius + panel_opening_edge_compensation,
            )
            .lineTo(
                panel_opening_top_and_sides,
                -self.spool_volume_radius
                - self.bottom_extra_height
                + self.shell_bottom_radius,
            )
            .radiusArc(
                (
                    self.spool_volume_radius - self.shell_bottom_radius,
                    -panel_opening_top_and_sides - self.bottom_extra_height,
                ),
                self.shell_bottom_radius + panel_opening_edge_compensation,
            )
            .lineTo(0, -panel_opening_top_and_sides - self.bottom_extra_height)
            .close()
            .extrude(panel_thickness + panel_lip_thickness, both=True)
        )
        panel_opening = panel_opening_half + panel_opening_half.mirror("XZ")
        panel_opening = panel_opening.translate(
            (self.spool_volume_width + side_thickness / 2, 0, 0)
        )

        subtract = panel + panel_opening
        printed = printed - subtract

        return printed

    def box_perimeter(self):
        """
        Draw profile of perimeter all around the box, then sweep it along perimeter path.
        Lip of the box must stay in sync with lid_perimeter for the two to mesh.
        """
        box_width = self.spool_volume_width * 2 - self.lid_height
        profile = (
            cq.Workplane("XZ")
            .lineTo(
                self.spool_volume_width,
                self.spool_volume_radius - self.shell_thickness,
                forConstruction=True,
            )
            .line(-self.lid_height, 0)
            .line(-self.shell_thickness, self.shell_thickness)
            .line(-box_width + self.shell_thickness * 2 + self.lid_height, 0)
            .line(-self.shell_thickness, -self.shell_thickness)
            .line(-self.lid_height + self.shell_thickness / 2, 0)
            .line(0, self.shell_thickness)
            .line(self.lid_height - self.shell_thickness, 0)
            .line(self.shell_thickness, self.shell_thickness)
            .line(box_width - self.shell_thickness / 2, 0)
            .close()
        )

        return profile.sweep(self.box_perimeter_path())

    def add_filament_exit(
        self,
        perimeter,
        exit_fitting_diameter=5.5,
        exit_fitting_depth=5,
    ):
        """
        Adding provision for a PTFE tube fitting for the filament to exit
        allows a printer to draw directly from this box.
        """
        available_width = (
            self.spool_volume_width - self.lid_height - self.shell_thickness * 2
        )
        exit_depth = exit_fitting_diameter * 1.5

        ramp_bottom_z = self.spool_volume_radius - self.shell_top_radius

        assert self.shell_top_radius > exit_depth

        angle_to_clear_exit = math.acos(
            (self.shell_top_radius - exit_depth * 2) / self.shell_top_radius
        )
        height_to_clear_exit = ramp_bottom_z + self.shell_top_radius * math.sin(
            angle_to_clear_exit
        )

        # Add the exterior bump
        flare_exterior_half = (
            cq.Workplane("XZ")
            .lineTo(0, ramp_bottom_z, forConstruction=True)
            .lineTo(0, height_to_clear_exit)
            .lineTo(exit_depth, height_to_clear_exit)
            .lineTo(available_width, ramp_bottom_z)
            .close()
            .workplane(offset=exit_depth * 2)
            .lineTo(
                0, height_to_clear_exit - self.shell_thickness, forConstruction=True
            )
            .lineTo(0, height_to_clear_exit)
            .lineTo(available_width, height_to_clear_exit)
            .lineTo(available_width, height_to_clear_exit - self.shell_thickness)
            .close()
            .loft()
        ).translate((0, self.spool_volume_radius + self.shell_thickness, 0))

        flare_exterior = flare_exterior_half + flare_exterior_half.mirror("YZ")

        spool_volume_subtract = (
            cq.Workplane("YZ")
            .transformed(offset=cq.Vector(ramp_bottom_z, ramp_bottom_z, 0))
            .circle(self.shell_top_radius - 1e-4)  # 1e-4 to work around CQ bug
            .extrude(
                self.spool_volume_width - self.lid_height - self.shell_thickness,
                both=True,
            )
        )

        perimeter = perimeter + flare_exterior - spool_volume_subtract

        # PTFE tube fitting has M6 thread, brass metal should be strong
        # enough to self-tap into this plastic cylindrical hole
        fitting_hole = (
            cq.Workplane("XY")
            .transformed(
                offset=(
                    0,
                    self.spool_volume_radius - exit_depth / 2,
                    height_to_clear_exit,
                )
            )
            .circle(exit_fitting_diameter / 2)
            .extrude(-exit_fitting_depth)
        )
        perimeter = perimeter - fitting_hole

        # Interior funnel for guiding filament into the fitting
        flare_end_size = self.spool_volume_width
        flare_end_angle = 75
        flare_interior = (
            cq.Workplane("XY")
            .transformed(
                offset=(
                    0,
                    self.spool_volume_radius - exit_depth / 2,
                    height_to_clear_exit - exit_fitting_depth,
                )
            )
            .circle(1.8 / 2)
            .workplane(offset=(height_to_clear_exit - ramp_bottom_z) * -1.5)
            .transformed(
                offset=cq.Vector(
                    0, -flare_end_size * math.cos(math.radians(flare_end_angle)), 0
                )
            )
            .transformed(rotate=cq.Vector(-flare_end_angle, 0, 0))
            .circle(flare_end_size)
            .loft()
        )

        perimeter = perimeter - flare_interior

        return perimeter

    def lid_perimeter(self):
        """
        Draw profile of lid all around the box, then sweep it along perimeter path.
        Must stay in sync with box_perimeter for the two to mesh.
        """
        profile = (
            cq.Workplane("XZ")
            .lineTo(
                -self.spool_volume_width, self.spool_volume_radius, forConstruction=True
            )
            .line(self.lid_height - self.shell_thickness / 2, 0)
            .line(
                0, self.shell_thickness
            )  # .line(self.shell_thickness, self.shell_thickness)
            .line(
                -self.lid_height + self.shell_thickness / 2, 0
            )  # .line(-self.lid_height - self.shell_thickness / 2, 0)
            .close()
        )

        return profile.sweep(self.box_perimeter_path())

    def bearing_tray(
        self,
        bearing_diameter_outer=22,
        bearing_diameter_inner=8,
        bearing_length=7,
        bearing_separation_angle_degrees=30,
        bearing_clearance_gap=0.25,
        bearing_axle_slot_fraction=0.8,
    ):
        """
        Allows a quartet of bearings to support the filament spool, reduces
        friction when printer is fed directly from this box. (Versus a non-
        printing storage box.) Printed in multiple pieces to optimize strength
        from layer orientation.
        """

        # Placeholder bearings for visualization.
        # (Not for printing - use real bearings!)
        bearing_distance = self.spool_diameter / 2 + bearing_diameter_outer / 2
        bearing_x = self.spool_width / 2 - bearing_length
        bearing_separation_angle_radians = math.radians(
            180 - bearing_separation_angle_degrees / 2
        )
        bearing_y = bearing_distance * math.sin(bearing_separation_angle_radians)
        bearing_z = bearing_distance * math.cos(bearing_separation_angle_radians)

        bearing_placeholder = (
            cq.Workplane("YZ")
            .circle(bearing_diameter_outer / 2)
            .circle(bearing_diameter_inner / 2)
            .extrude(bearing_length)
        ).translate((bearing_x, bearing_y, bearing_z))

        bearing_axle_lip_x = (
            self.spool_width / 2 - bearing_length - bearing_clearance_gap
        )
        bearing_axle_lip_y = bearing_diameter_inner * 0.25
        bearing_axle_half = (
            # outer parts of the axle that go through middle of bearings
            cq.Workplane("YZ")
            .transformed(offset=cq.Vector(bearing_y, bearing_z))
            .circle(bearing_diameter_inner / 2 - bearing_clearance_gap)
            .extrude(self.spool_volume_width)
        ) + (
            cq.Workplane("YZ")
            # Middle part of the axle thicker to keep bearings in place
            .transformed(offset=cq.Vector(bearing_y, bearing_z))
            .circle(bearing_diameter_inner / 2 + bearing_axle_lip_y)
            .extrude(bearing_axle_lip_x)
        )

        bearing_axle_half = bearing_axle_half.edges(
            sel.NearestToPointSelector(
                (
                    bearing_axle_lip_x,
                    bearing_y,
                    bearing_diameter_inner / 2 + bearing_axle_lip_y,
                )
            )
        ).chamfer(bearing_axle_lip_y)

        bearing_axle_half = bearing_axle_half.faces(">X").fillet(
            bearing_diameter_inner / 8
        )

        bearing_axle_center_slice = (
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(0, bearing_y, bearing_z))
            .box(
                self.spool_width * 3,
                bearing_diameter_inner * bearing_axle_slot_fraction,
                bearing_diameter_outer,
            )
        )

        bearing_axle_half = bearing_axle_half.intersect(bearing_axle_center_slice)
        bearing_axle = bearing_axle_half + bearing_axle_half.mirror("YZ")

        # Now create a truck to carry a pair of the above axles
        bearing_axle_truck_bottom_z = (
            bearing_z - bearing_diameter_outer / 2 - self.spool_width_margin
        )
        bearing_axle_truck_y = (
            bearing_y + bearing_diameter_outer / 2 + bearing_clearance_gap
        )

        bearing_axle_truck_xz = (
            cq.Workplane("XZ")
            .lineTo(0, bearing_axle_truck_bottom_z, forConstruction=True)
            .line(self.spool_volume_width, 0)
            .line(0, bearing_diameter_outer + self.spool_width_margin * 1.5)
            .line(-self.spool_width_margin + bearing_clearance_gap, 0)
            .line(0, -bearing_diameter_outer - self.spool_width_margin * 0.5)
            .tangentArcPoint((-bearing_clearance_gap * 2, -bearing_clearance_gap * 2))
            .line(-self.spool_width / 2 + bearing_clearance_gap, 0)
            .close()
            .extrude(-bearing_axle_truck_y)
        )

        truck_reinforcement_rib_bottom_z = (
            bearing_axle_truck_bottom_z
            + self.spool_width_margin
            - bearing_clearance_gap * 2
        )
        truck_reinforcement_rib = (
            cq.Workplane("XZ")
            .lineTo(
                self.spool_width / 2 + bearing_clearance_gap,
                -self.spool_diameter / 2,
                forConstruction=True,
            )
            # Bezier is fancy version of .lineTo(0, truck_reinforcement_rib_bottom_z)
            .bezier(
                (
                    (
                        self.spool_width / 2 + bearing_clearance_gap,
                        -self.spool_diameter / 2,
                    ),
                    (
                        self.spool_width / 2 + bearing_clearance_gap,
                        -self.spool_diameter / 2 - bearing_diameter_outer / 2,
                    ),
                    (
                        self.spool_width / 4,
                        truck_reinforcement_rib_bottom_z,
                    ),
                    (0, truck_reinforcement_rib_bottom_z),
                )
            )
            .lineTo(
                self.spool_width / 2 + bearing_clearance_gap,
                truck_reinforcement_rib_bottom_z,
            )
            .close()
            .extrude(-self.spool_width_margin)
        )
        bearing_axle_truck_xz = bearing_axle_truck_xz + truck_reinforcement_rib

        spool_centering_guide_cut = (
            cq.Workplane("XZ")
            .lineTo(self.spool_volume_width, 0)
            .lineTo(
                self.spool_volume_width,
                -self.spool_diameter / 2 + self.spool_width_margin,
            )
            .lineTo(self.spool_width / 2, -self.spool_diameter / 2)
            .lineTo(0, -self.spool_diameter / 2)
            .close()
            .revolve(bearing_separation_angle_degrees, (0, 0, 0), (1, 0, 0))
        )

        bearing_axle_slot_offset = (
            bearing_diameter_inner * bearing_axle_slot_fraction
        ) / 2
        bearing_axle_slot = (
            cq.Workplane("YZ")
            .lineTo(bearing_y - bearing_axle_slot_offset, 0, forConstruction=True)
            .lineTo(
                bearing_y - bearing_axle_slot_offset,
                bearing_z - bearing_diameter_inner / 2 + bearing_clearance_gap,
            )
            .line(bearing_axle_slot_offset * 2, 0)
            .line(0, bearing_diameter_inner)
            .line(bearing_diameter_outer, 0)
            .lineTo(bearing_axle_truck_y, 0)
            .close()
            .extrude(self.spool_volume_width)
        )
        bearing_axle_truck_quarter = (
            (bearing_axle_truck_xz - spool_centering_guide_cut - bearing_axle_slot)
            .faces(">Y")
            .edges(">Z")
            .fillet(bearing_diameter_outer / 4)
            .faces(">X")
            .edges(">Y")
            .fillet(self.spool_width_margin * 0.8)
        )

        bearing_axle_truck = quarter_to_whole(bearing_axle_truck_quarter)

        spacer_height = (
            self.spool_volume_radius
            + self.bottom_extra_height
            + bearing_axle_truck_bottom_z
            - self.shell_thickness
        )

        assert (
            spacer_height > 0
        ), "Not enough room for bearings. Parameter bottom_extra_height is {} but needs to be at least {}".format(
            self.bottom_extra_height, self.bottom_extra_height - spacer_height
        )

        # Create a spacer to raise bearings up to the proper height. This
        # space is available for other use, such as extra dessicant or a
        # microcontroller and associated sensors.
        spacer_quarter = (
            cq.Workplane("XZ")
            .lineTo(0, bearing_axle_truck_bottom_z, forConstruction=True)
            .line(self.spool_volume_width, 0)
            .line(0, -spacer_height)
            .line(-self.lid_height - self.shell_thickness, 0)
            .line(-self.shell_thickness, -self.shell_thickness)
            .lineTo(
                0, bearing_axle_truck_bottom_z - spacer_height - self.shell_thickness
            )
            .close()
            .extrude(bearing_axle_truck_y)
        )
        spacer = quarter_to_whole(spacer_quarter)
        spacer = spacer.edges("|Z").fillet(self.spool_width_margin * 0.8)

        return {
            "bearing": bearing_placeholder,
            "bearing axle": bearing_axle,
            "tray": bearing_axle_truck,
            "tray length half": bearing_axle_truck_y,
            "below tray": spacer_height,
            "spacer": spacer,
        }

    def dessicant_tray_gyroid(
        self,
        wall_thickness=3,
        top_opening=10,
        center_y=0,
    ):
        """
        A tray to hold loose dessicant particles (not enclosed in paper bag)
        Printed with zero top layers, zero perimeters, and Gyroid infill in
        order to generate a container with highly porous walls. Adjust infill
        percentage proportional to size of dessicant particcles to avoid leaks.
        """
        top_edge_length = top_opening + wall_thickness * 2

        spool_angle_for_depth = math.acos(
            (self.spool_volume_radius - top_edge_length - self.shell_thickness)
            / self.spool_volume_radius
        )
        top_edge_height_z = math.sin(spool_angle_for_depth) * self.spool_volume_radius

        tray_bottom_z = (
            -self.spool_volume_radius - self.bottom_extra_height + self.shell_thickness
        )
        tray_back_y = self.spool_volume_radius - self.shell_thickness
        volume = (
            cq.Workplane("YZ")
            .lineTo(tray_back_y, -top_edge_height_z, forConstruction=True)
            .line(-top_edge_length, 0)
            .lineTo(center_y, top_edge_length - self.spool_volume_radius)
            .lineTo(center_y, tray_bottom_z)
            .lineTo(tray_back_y, tray_bottom_z)
            .close()
            .extrude(self.spool_volume_width - self.shell_thickness, both=True)
            .faces("<Z")
            .edges(">Y")
            .chamfer(self.shell_bottom_radius)
        )

        spool_subtract = (
            cq.Workplane("YZ")
            .circle(self.spool_volume_radius)
            .extrude(self.spool_volume_width, both=True)
        )

        volume = volume - spool_subtract

        volume = volume.faces("+Z").shell(-wall_thickness)
        volume = volume.faces("<X").fillet(wall_thickness / 2)
        volume = volume.faces(">X").fillet(wall_thickness / 2)

        return volume


def quarter_to_whole(quarter):
    return (
        quarter
        + quarter.mirror("XZ")
        + quarter.mirror("YZ")
        + quarter.mirror("YZ").mirror("XZ")
    )


def compact_storage_box():
    fdb = filament_dry_box(bottom_extra_height=0)
    show_object(fdb.spool_placeholder(), options={"color": "black", "alpha": 0.75})
    box_half = fdb.box_perimeter() + fdb.fully_closed_side()
    show_object(
        box_half + box_half.mirror("XZ"), options={"color": "blue", "alpha": 0.5}
    )

    lid_half = fdb.lid_perimeter() + fdb.fully_closed_side().mirror("YZ")
    show_object(
        lid_half + lid_half.mirror("XZ"), options={"color": "green", "alpha": 0.5}
    )


def show_bearing_tray(fdb):
    assert "show_object" in globals()
    tray = fdb.bearing_tray()
    show_object(
        quarter_to_whole(tray["bearing"]), options={"color": "black", "alpha": 0.9}
    )
    axle = tray["bearing axle"]
    show_object(axle, options={"color": "#ABCDEF", "alpha": 0.5})
    show_object(axle.mirror("XZ"), options={"color": "#ABCDEF", "alpha": 0.5})
    show_object(tray["tray"], options={"color": "#ABCDFF", "alpha": 0.5})
    show_object(tray["spacer"], options={"color": "#FFCDEF", "alpha": 0.5})
    log("Remaining height below bearing tray: {0}mm".format(tray["below tray"]))
    return tray["tray length half"]


def filament_feed_box():
    fdb = filament_dry_box()
    show_object(fdb.spool_placeholder(), options={"color": "black", "alpha": 0.9})
    box = fdb.box_perimeter()
    box = box + box.mirror("XZ")
    box = fdb.add_filament_exit(perimeter=box)
    box = box + fdb.single_panel_side()
    show_object(box, options={"color": "blue", "alpha": 0.5})

    lid = fdb.lid_perimeter()
    lid = lid + lid.mirror("XZ")
    lid = lid + fdb.single_panel_side().mirror("YZ")
    show_object(lid, options={"color": "green", "alpha": 0.5})
    half_length = show_bearing_tray(fdb)
    show_object(
        fdb.dessicant_tray_gyroid(center_y=half_length + fdb.shell_thickness),
        options={"color": "#AF3", "alpha": 0.5},
    )
    show_object(
        fdb.dessicant_tray_gyroid(center_y=half_length + fdb.shell_thickness).mirror(
            "XZ"
        ),
        options={"color": "#AF3", "alpha": 0.5},
    )


def individual_components():
    fdb = filament_dry_box(bottom_extra_height=28)
    show_object(fdb.spool_placeholder(), options={"color": "black", "alpha": 0.9})
    show_object(fdb.fully_closed_side(), options={"color": "red", "alpha": 0.5})
    show_object(fdb.box_perimeter(), options={"color": "blue", "alpha": 0.5})
    show_object(fdb.lid_perimeter(), options={"color": "green", "alpha": 0.5})
    half_length = show_bearing_tray(fdb)
    show_object(
        fdb.dessicant_tray_gyroid(center_y=half_length + fdb.shell_thickness),
        options={"color": "#AF3", "alpha": 0.5},
    )


def filament_exit_test():
    fdb = filament_dry_box(bottom_extra_height=28)
    exit_test = fdb.add_filament_exit(fdb.box_perimeter())
    test_height = 60
    test_intersect = (
        cq.Workplane("XZ")
        .lineTo(fdb.spool_volume_width / 3, 0)
        .line(0, test_height)
        .line(-fdb.spool_volume_width * 2 / 3, 0)
        .line(0, -test_height)
        .close()
        .extrude(-fdb.spool_volume_radius - fdb.shell_thickness * 2)
    )

    show_object(
        exit_test.intersect(test_intersect), options={"color": "blue", "alpha": 0.5}
    )


if "show_object" in globals():
    filament_feed_box()
