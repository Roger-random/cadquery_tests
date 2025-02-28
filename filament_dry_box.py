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
        shell_bottom_radius=10,
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
        self.shell_bottom_radius = shell_bottom_radius
        self.bottom_extra_height = bottom_extra_height
        self.lid_height = lid_height

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
            .radiusArc((self.spool_volume_radius, 0), self.spool_volume_radius)
            .line(
                0,
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

        panel_top_radius = (
            self.spool_volume_radius + self.shell_thickness - wall_thickness
        )
        panel_bottom_radius = (
            self.shell_bottom_radius + self.shell_thickness - wall_thickness
        )
        panel = (
            cq.Workplane("YZ")
            .transformed(offset=(0, 0, self.spool_volume_width))
            .lineTo(0, panel_top_radius, forConstruction=True)
            .radiusArc((panel_top_radius, 0), panel_top_radius)
            .line(
                0,
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

    def tiled_lid_side(
        self,
        tile_lip_thickness=0.8,
        tile_length=56,
        tile_width=29,
        tile_thickness=3.2,
    ):
        side_thickness = tile_thickness + tile_lip_thickness * 2

        panel_half = self.fully_closed_side(side_thickness)

        panel = panel_half + panel_half.mirror("XZ")

        return panel

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
            .line(-self.lid_height, 0)
            .line(self.shell_thickness, self.shell_thickness)
            .line(self.lid_height - self.shell_thickness * 1.5, 0)
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

        angle_to_clear_exit = math.acos(
            (self.spool_volume_radius - exit_depth * 2) / self.spool_volume_radius
        )
        height_to_clear_exit = self.spool_volume_radius * math.sin(angle_to_clear_exit)

        # Add the exterior bump
        flare_exterior_half = (
            cq.Workplane("XZ")
            .lineTo(0, height_to_clear_exit)
            .lineTo(exit_depth, height_to_clear_exit)
            .lineTo(available_width, 0)
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
            .circle(self.spool_volume_radius - 1e-4)  # 1e-4 to work around CQ bug
            .extrude(self.spool_volume_width, both=True)
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
            .workplane(offset=exit_fitting_depth - height_to_clear_exit)
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
            .line(self.shell_thickness, self.shell_thickness)
            .line(-self.lid_height - self.shell_thickness / 2, 0)
            .close()
        )

        return profile.sweep(self.box_perimeter_path())

    def bearing_tray(
        self,
        bearing_diameter_outer=22,
        bearing_diameter_inner=8,
        bearing_length=7,
        bearing_separation_angle_degrees=30,
        tray_structure_thickness=6,
        tray_rail_height_delta=0.1,
        rail_lip_gap=0.5,
        bearing_lip_size=0.5,
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

        # Two rails hold two bearings each. Each rail is designed and extruded
        # in half then mirrored in X.
        tray_inner_radius = self.spool_volume_radius + bearing_diameter_outer
        rail_lip_size = self.spool_width_margin - rail_lip_gap
        bearing_rail = (
            cq.Workplane("XZ")
            .transformed(rotate=cq.Vector(bearing_separation_angle_degrees / 2, 0, 0))
            .lineTo(
                self.spool_volume_width, -self.spool_diameter / 2, forConstruction=True
            )
            # Draw the top lip
            .line(0, rail_lip_size)
            .line(-rail_lip_size, -rail_lip_size)
            .line(
                -rail_lip_gap, -bearing_diameter_outer / 2 + bearing_diameter_inner / 2
            )
            # Top of bearing center
            .line(-bearing_length, 0)
            # Bearing retaining clip
            .line(-rail_lip_gap, bearing_lip_size)
            .line(-bearing_lip_size, 0)
            .line(0, -bearing_diameter_inner / 2 - bearing_lip_size)
            # Bottom of bearing center
            .line(bearing_length + bearing_lip_size + rail_lip_gap, -bearing_lip_size)
            .lineTo(
                self.spool_volume_width - self.spool_width_margin + rail_lip_gap,
                -self.spool_diameter / 2 - bearing_diameter_outer,
            )
            # Cross member to reach the opposing bearing
            .lineTo(
                self.spool_volume_width
                - self.spool_width_margin
                + rail_lip_gap
                - bearing_length / 2,
                -tray_inner_radius,
            )
            .lineTo(0, -tray_inner_radius)
            .line(0, -tray_structure_thickness)
            .line(self.spool_volume_width, 0)
            .close()
            .extrude(tray_structure_thickness / 2, both=True)
        )
        bearing_rail = bearing_rail - bearing_placeholder

        # Bottom of the tray to support the above pair of rails. Designed in a
        # quarter then mirrored about both X and Y to create the tray.
        tray_quarter_revolve = (
            cq.Workplane("XZ")
            .lineTo(
                0, -tray_inner_radius - tray_rail_height_delta, forConstruction=True
            )
            .lineTo(0, -self.spool_diameter)
            .line(self.spool_volume_width, 0)
            .lineTo(
                self.spool_volume_width,
                bearing_length / 2 - tray_inner_radius - tray_rail_height_delta,
            )
            .lineTo(
                self.spool_volume_width - self.spool_width_margin + rail_lip_gap,
                -self.spool_diameter / 2
                - bearing_diameter_outer
                - tray_rail_height_delta,
            )
            .lineTo(
                self.spool_volume_width
                - self.spool_width_margin
                + rail_lip_gap
                - bearing_length / 2,
                -tray_inner_radius - tray_rail_height_delta,
            )
            .close()
            .revolve(bearing_separation_angle_degrees, (0, 0, 0), (1, 0, 0))
        )

        tray_length_half = bearing_x + bearing_diameter_outer / 2 + 1
        tray_quarter_intersect = (
            cq.Workplane("XZ")
            .lineTo(
                0,
                -tray_inner_radius - tray_structure_thickness,
                forConstruction=True,
            )
            .line(
                self.spool_volume_width - self.lid_height - self.shell_thickness * 2, 0
            )
            .line(self.shell_thickness, self.shell_thickness)
            .line(self.lid_height + self.shell_thickness, 0)
            .lineTo(self.spool_volume_width, -self.spool_volume_radius)
            .line(-self.spool_volume_width, 0)
            .close()
            .extrude(-tray_length_half)
        )
        tray_quarter = tray_quarter_revolve.intersect(tray_quarter_intersect)

        tray_quarter = tray_quarter - bearing_rail
        tray = tray_quarter + tray_quarter.mirror("XZ")
        tray = tray + tray.mirror("YZ")

        tray_center_cutout_size = self.spool_volume_width * 0.8
        tray = (
            # Center cutout
            tray.faces("<Z")
            .workplane()
            .transformed(rotate=cq.Vector(0, 0, 45))
            .rect(tray_center_cutout_size, tray_center_cutout_size)
            .cutThruAll()
        )

        return {
            "bearing": bearing_placeholder,
            "rail half": bearing_rail,
            "tray": tray,
            "tray length half": tray_length_half,
            "below tray": self.spool_volume_radius
            + self.bottom_extra_height
            - tray_inner_radius
            - tray_structure_thickness,
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


def mirror_xy(quarter):
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
    show_object(mirror_xy(tray["bearing"]), options={"color": "black", "alpha": 0.9})
    rail = tray["rail half"] + tray["rail half"].mirror("YZ")
    show_object(rail, options={"color": "#ABCDEF", "alpha": 0.5})
    show_object(rail.mirror("XZ"), options={"color": "#ABCDEF", "alpha": 0.5})
    show_object(tray["tray"], options={"alpha": 0.5})
    log(tray["below tray"])
    return tray["tray length half"]


def filament_feed_box():
    fdb = filament_dry_box(bottom_extra_height=28)
    show_object(fdb.spool_placeholder(), options={"color": "black", "alpha": 0.9})
    fcs = fdb.fully_closed_side(wall_thickness=1.4)
    box = fdb.box_perimeter() + fcs
    box = box + box.mirror("XZ")
    box = fdb.add_filament_exit(perimeter=box)
    show_object(box, options={"color": "blue", "alpha": 0.5})

    lid = fdb.lid_perimeter() + fdb.fully_closed_side(wall_thickness=1.4).mirror("YZ")
    lid = lid + lid.mirror("XZ")
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
    show_object(fdb.tiled_lid_side(), options={"color": "red", "alpha": 0.5})
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
    individual_components()
