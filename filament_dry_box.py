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
        spool_width_margin=3,
        shell_thickness=0.8,
        shell_bottom_radius=10,
        bottom_extra_height=40,
        lid_height=10,
    ):
        self.spool_diameter = spool_diameter
        self.spool_volume_radius = spool_diameter / 2 + spool_diameter_margin
        self.spool_width = spool_width
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
        The outer perimeter of side panels
        """

        assert wall_thickness < self.shell_thickness
        profile = (
            cq.Workplane("XZ")
            .lineTo(
                self.spool_volume_width, self.spool_volume_radius, forConstruction=True
            )
            .line(0, self.shell_thickness)
            .line(wall_thickness, -wall_thickness)
            .line(0, wall_thickness - self.shell_thickness)
            .close()
        )

        rim = profile.sweep(self.box_perimeter_path())

        panel = (self.box_perimeter_path().close().extrude(wall_thickness)).translate(
            (self.spool_volume_width, 0, 0)
        )

        return rim + panel

    def box_perimeter(self):
        """
        Draw profile of perimeter all around the box, then sweep it along perimeter path.
        Lip of the box must stay in sync with lid_perimeter for the two to mesh.
        """
        box_width = self.spool_volume_width * 2 - self.lid_height
        profile = (
            cq.Workplane("XZ")
            .lineTo(
                self.spool_volume_width, self.spool_volume_radius, forConstruction=True
            )
            .line(-box_width + self.shell_thickness, 0)
            .line(-self.shell_thickness, -self.shell_thickness)
            .line(-self.lid_height, 0)
            .line(self.shell_thickness, self.shell_thickness)
            .line(self.lid_height - self.shell_thickness * 1.5, 0)
            .line(self.shell_thickness, self.shell_thickness)
            .line(box_width - self.shell_thickness / 2, 0)
            .close()
        )

        return profile.sweep(self.box_perimeter_path())

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
    ):
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

        return {"bearings": mirror_xy(bearing_placeholder)}


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
    bearings = tray["bearings"]
    show_object(bearings, options={"color": "yellow", "alpha": 0.5})


def individual_components():
    fdb = filament_dry_box()
    show_object(fdb.spool_placeholder(), options={"color": "black", "alpha": 0.75})
    show_object(fdb.fully_closed_side(), options={"color": "red", "alpha": 0.5})
    show_object(fdb.box_perimeter(), options={"color": "blue", "alpha": 0.5})
    show_object(fdb.lid_perimeter(), options={"color": "green", "alpha": 0.5})
    show_bearing_tray(fdb)


if "show_object" in globals():
    individual_components()
