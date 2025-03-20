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


def tin_placeholder_3oz():
    """
    Placeholder for a small 3oz container from McMaster-Carr
    https://www.mcmaster.com/products/tin-cans/tins-1~/
    """
    return (
        cq.Workplane("XY")
        .circle(69 / 2)
        .extrude(12.5)
        .faces(">Z")
        .workplane()
        .circle(70 / 2)
        .extrude(3)
        .faces(">Z")
        .workplane()
        .circle(72 / 2)
        .extrude(2)
        .faces(">Z")
        .workplane()
        .circle(69.5 / 2)
        .extrude(5.5)
        .faces(">Z")
        .workplane()
        .circle(61.3 / 2)
        .extrude(0.5)
        .faces("<Z")
        .fillet(2)
    )


def tin_placeholder_4oz():
    """
    Placeholder for a small 4oz container from McMaster-Carr
    https://www.mcmaster.com/products/tin-cans/tins-1~/
    """
    return (
        cq.Workplane("XY")
        .circle(64.5 / 2)
        .extrude(29)
        .faces(">Z")
        .workplane()
        .circle(65.5 / 2)
        .extrude(4)
        .faces(">Z")
        .workplane()
        .circle(67.35 / 2)
        .extrude(1.5)
        .faces(">Z")
        .workplane()
        .circle(65 / 2)
        .extrude(11.5)
        .faces(">Z")
        .workplane()
        .circle(55 / 2)
        .extrude(0.5)
        .faces("<Z")
        .fillet(2)
    )


def bearing_placeholder(
    bearing_diameter_outer=22,
    bearing_diameter_inner=8,
    bearing_length=7,
):
    return (
        cq.Workplane("YZ")
        .circle(bearing_diameter_outer / 2)
        .circle(bearing_diameter_inner / 2)
        .extrude(bearing_length)
        .translate((-bearing_length / 2, 0, 0))
    )


class filament_rm_7m74:
    """
    Turning a Rubbermaid 7M74 5 liter / 21 cup ("fits 5lb flour") container
    into a filament dispenser box with accommodations for tin cans holding
    loose dessicant
    """

    def __init__(
        self,
        width=89,
        length=210,
        corner_fillet=25,
        bottom_chamfer=10,
        spool_diameter=200,
        spool_width=72.5,
    ):
        self.width = width
        self.length = length
        self.corner_fillet = corner_fillet
        self.bottom_chamfer = bottom_chamfer
        self.spool_diameter = spool_diameter
        self.spool_width = spool_width

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

    def base_volume(
        self,
        side_extra_height=2,
    ):
        return (
            cq.Workplane("XY")
            .rect(self.width, self.length)
            .extrude(self.bottom_chamfer + side_extra_height)
            .edges("|Z")
            .fillet(self.corner_fillet)
            .faces("<Z")
            .chamfer(self.bottom_chamfer)
        )

    def tray_3oz_transform(self, tin):
        return (
            tin.translate((0, 35, 0))
            .rotate((0, 0, 0), (1, 0, 0), 40)
            .translate((0, 52, -1))
        )

    def bearing_support_cutout(
        self,
        width=7,
        ridge_size=1,
    ):
        width_half = width / 2
        height_half = self.bottom_chamfer / 2
        support_half = (
            cq.Workplane("YZ")
            .lineTo(0, -1, forConstruction=True)
            .lineTo(width_half, -1)
            .lineTo(width_half, height_half - ridge_size)
            .lineTo(width_half - ridge_size, height_half)
            .lineTo(width_half, height_half + ridge_size)
            .lineTo(width_half, 100)
            .lineTo(0, 100)
            .close()
            .extrude(self.width)
        )

        return support_half + support_half.mirror("XZ")

    def tray_3oz(self):
        base = self.base_volume(side_extra_height=2)
        tin_cutout_center = (
            cq.Workplane("XY").circle(35).extrude(24).faces("<Z").chamfer(1)
        )
        tray = base - tin_cutout_center

        tin_cutout_side = self.tray_3oz_transform(tin_cutout_center)
        tray = tray - tin_cutout_side - tin_cutout_side.mirror("XZ")

        support_cutout = self.bearing_support_cutout().translate((20, 35, 0))

        tray = (
            tray
            - support_cutout
            - support_cutout.mirror("XZ")
            - support_cutout.mirror("YZ")
            - support_cutout.mirror("XZ").mirror("YZ")
        )

        return tray

    def bearing_support_inner_3oz(self):
        slot_start_x = 20
        bearing_center_x = 34
        bearing_half = 7 / 2
        support_thickness = 7
        base_height = self.bottom_chamfer + 2
        bearing_guide_thickness = 5
        bearing_x_inner = bearing_center_x - bearing_half
        bearing_x_clear = 0.5
        bearing_y = 24
        bearing_y_top = bearing_y + 11
        side = (
            cq.Workplane("XZ")
            .lineTo(slot_start_x, 0, forConstruction=True)
            .line(0, base_height)
            .lineTo(
                bearing_x_inner - bearing_guide_thickness - bearing_x_clear,
                bearing_y_top + bearing_guide_thickness,
            )
            .line(bearing_guide_thickness, -bearing_guide_thickness)
            .lineTo(bearing_x_inner, bearing_y + 4)
            .line(0, -8)
            .lineTo(bearing_x_inner - bearing_x_clear, base_height)
            .lineTo(bearing_x_inner, base_height)
            .lineTo(bearing_x_inner, 0)
            .close()
            .extrude(support_thickness / 2, both=True)
        )

        support = side.intersect(self.bearing_support_cutout())

        return support

    def bearing_support_outer_3oz(self):
        bearing_center_x = 34
        bearing_half = 7 / 2
        support_thickness = 7
        base_height = self.bottom_chamfer + 2
        bearing_guide_thickness = 5
        bearing_x_inner = bearing_center_x - bearing_half
        bearing_x_outer = bearing_center_x + bearing_half
        bearing_x_clear = 0.5
        bearing_y = 24
        bearing_y_top = bearing_y + 11

        side = (
            cq.Workplane("XZ")
            .lineTo(bearing_x_inner, 0, forConstruction=True)
            .line(0, base_height)
            .lineTo(bearing_x_outer + bearing_x_clear, base_height)
            .lineTo(bearing_x_outer, bearing_y - 4)
            .line(0, 8)
            .lineTo(bearing_x_outer + bearing_x_clear, bearing_y_top)
            .line(bearing_guide_thickness, bearing_guide_thickness)
            .lineTo(self.width / 2, base_height)
            .line(0, -base_height + self.bottom_chamfer)
            .line(-self.bottom_chamfer, -self.bottom_chamfer)
            .close()
            .extrude(support_thickness / 2, both=True)
        )

        axle = (
            (cq.Workplane("YZ").circle(4).extrude(bearing_half * 2))
            .intersect((cq.Workplane("YZ").rect(7, 8).extrude(bearing_half * 2)))
            .translate((bearing_x_inner, 0, bearing_y))
        )

        support = (side + axle).intersect(self.bearing_support_cutout())

        return support


def assembly_3oz():
    fr7 = filament_rm_7m74()

    show_object(fr7.tray_3oz(), options={"color": "blue", "alpha": 0.5})
    show_object(tin_placeholder_3oz(), options={"color": "gray", "alpha": 0.8})
    side = fr7.tray_3oz_transform(tin_placeholder_3oz())
    show_object(side, options={"color": "gray", "alpha": 0.8})
    show_object(side.mirror("XZ"), options={"color": "gray", "alpha": 0.8})
    show_object(
        fr7.spool_placeholder().translate((0, 0, 130)),
        options={"color": "gray", "alpha": 0.8},
    )
    show_object(
        bearing_placeholder().translate((34, -35, 24)),
        options={"color": "gray", "alpha": 0.8},
    )

    bearing_support_pair = (
        fr7.bearing_support_inner_3oz() + fr7.bearing_support_outer_3oz()
    ).translate((0, -35, 0))
    show_object(
        bearing_support_pair,
        options={"color": "green", "alpha": 0.5},
    )


if "show_object" in globals():
    assembly_3oz()
