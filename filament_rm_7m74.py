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


class filament_rm_7m74:
    """
    Turning a Rubbermaid 7M74 5 liter / 21 cup ("fits 5lb flour") container
    into a filament dispenser box with accommodations for tin cans holding
    loose dessicant
    """

    def __init__(
        self,
        width=89.5,
        length=211,
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

    def bearing_placeholder(
        self,
        bearing_diameter_outer=22,
        bearing_diameter_inner=8,
        bearing_length=7,
    ):
        self.bearing_diameter_outer = bearing_diameter_outer
        self.bearing_diameter_inner = bearing_diameter_inner
        self.bearing_length = bearing_length
        return (
            cq.Workplane("YZ")
            .circle(bearing_diameter_outer / 2)
            .circle(bearing_diameter_inner / 2)
            .extrude(bearing_length)
            .translate((-bearing_length / 2, 0, 0))
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

    def base_volume(
        self,
        base_height=12,
    ):
        self.base_height = base_height
        return (
            cq.Workplane("XY")
            .rect(self.width, self.length)
            .extrude(base_height)
            .edges("|Z")
            .fillet(self.corner_fillet)
            .faces("<Z")
            .chamfer(self.bottom_chamfer)
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

    def tray_cutout(self, diameter, height):
        return (
            cq.Workplane("XY")
            .circle(diameter / 2)
            .extrude(height)
            .faces("<Z")
            .chamfer(1)
        )

    def tray(
        self,
        volume_height,
        cutout_diameter,
        cutout_height,
        side_transform,
        support_cutout_translate=(20, 35, 0),
    ):
        base = self.base_volume(base_height=volume_height)
        cutout_center = self.tray_cutout(diameter=cutout_diameter, height=cutout_height)

        tray = (
            base
            - cutout_center
            - side_transform(cutout_center)
            - side_transform(cutout_center).mirror("XZ")
        )

        support_cutout = self.bearing_support_cutout().translate(
            support_cutout_translate
        )
        self.support_cutout_translate = support_cutout_translate

        tray = (
            tray
            - support_cutout
            - support_cutout.mirror("XZ")
            - support_cutout.mirror("YZ")
            - support_cutout.mirror("XZ").mirror("YZ")
        )
        return tray

    def tray_3oz_side_transform(self, tin):
        return tin.translate((0, 71, 7))

    def tray_3oz(self):
        return self.tray(
            volume_height=12,
            cutout_diameter=70,
            cutout_height=24,
            side_transform=self.tray_3oz_side_transform,
        )

    def tray_4oz_side_transform(self, tin):
        return tin.translate((0, 70, 0))

    def tray_4oz(self):
        return self.tray(
            volume_height=30,
            cutout_diameter=65,
            cutout_height=45,
            side_transform=self.tray_4oz_side_transform,
        )

    def bearing_support(self):
        support_thickness = 7
        bearing_guide_thickness = 5
        bearing_x_clear = 0.5
        slot_start_x = self.support_cutout_translate[0]
        bearing_half = self.bearing_length / 2
        bearing_center_x = self.spool_width / 2 - bearing_half + 1
        bearing_x_inner = bearing_center_x - bearing_half
        bearing_x_outer = bearing_center_x + bearing_half
        bearing_y = self.base_height + self.bearing_diameter_outer / 2 + 1
        bearing_y_top = bearing_y + self.bearing_diameter_outer / 2
        bearing_axle_diameter = 8
        bearing_axle_top = bearing_y + bearing_axle_diameter / 2
        inner = (
            cq.Workplane("XZ")
            .lineTo(slot_start_x, 0, forConstruction=True)
            .line(0, self.base_height)
            .lineTo(
                bearing_x_inner - bearing_guide_thickness - bearing_x_clear,
                bearing_y_top + bearing_guide_thickness,
            )
            .line(bearing_guide_thickness, -bearing_guide_thickness)
            .lineTo(bearing_x_inner, bearing_axle_top)
            .line(0, -bearing_axle_diameter)
            .lineTo(bearing_x_inner - bearing_x_clear, self.base_height)
            .lineTo(bearing_x_outer + bearing_x_clear, self.base_height)
            .line(-bearing_x_clear, -self.base_height + self.bottom_chamfer)
            .lineTo(self.width / 2 - self.bottom_chamfer - support_thickness, 0)
            .close()
            .extrude(support_thickness / 2, both=True)
        )

        bearing_axle = (
            (
                cq.Workplane("YZ")
                .circle(bearing_axle_diameter / 2)
                .extrude(bearing_half * 2)
            )
            .intersect(
                cq.Workplane("YZ")
                .rect(support_thickness, bearing_axle_diameter)
                .extrude(bearing_half * 2)
            )
            .translate((bearing_x_inner, 0, bearing_y))
        )

        support_inner = (inner + bearing_axle).intersect(self.bearing_support_cutout())

        outer_top_x = 2 + self.width / 2

        outer = (
            cq.Workplane("XZ")
            .lineTo(
                self.width / 2 - self.bottom_chamfer - support_thickness,
                0,
                forConstruction=True,
            )
            .lineTo(bearing_x_outer, self.bottom_chamfer)
            .lineTo(bearing_x_outer + bearing_x_clear, self.base_height)
            .lineTo(bearing_x_outer, bearing_y - 4)
            .line(0, 8)
            .lineTo(bearing_x_outer + bearing_x_clear, bearing_y_top)
            .lineTo(
                outer_top_x,
                bearing_y_top + (outer_top_x) - (bearing_x_outer + bearing_x_clear),
            )
            .lineTo(self.width / 2, self.bottom_chamfer)
            .line(-self.bottom_chamfer, -self.bottom_chamfer)
            .close()
            .extrude(support_thickness / 2, both=True)
        )

        support_outer = outer.intersect(self.bearing_support_cutout())

        return support_inner, support_outer


def assembly_3oz():
    fr7 = filament_rm_7m74()

    show_object(fr7.tray_3oz(), options={"color": "blue", "alpha": 0.5})
    show_object(tin_placeholder_3oz(), options={"color": "gray", "alpha": 0.8})
    side = fr7.tray_3oz_side_transform(tin_placeholder_3oz())
    show_object(side, options={"color": "gray", "alpha": 0.8})
    show_object(side.mirror("XZ"), options={"color": "gray", "alpha": 0.8})
    show_object(
        fr7.spool_placeholder().translate((0, 0, 130)),
        options={"color": "gray", "alpha": 0.8},
    )

    show_object(
        fr7.bearing_placeholder().translate(
            (
                (fr7.spool_width / 2 - fr7.bearing_length / 2 + 1),
                -35,
                fr7.base_height + fr7.bearing_diameter_outer / 2 + 1,
            )
        ),
        options={"color": "gray", "alpha": 0.8},
    )

    bearing_support_inner, bearing_support_outer = fr7.bearing_support()
    bearing_support_pair = (bearing_support_inner + bearing_support_outer).translate(
        (0, -35, 0)
    )
    show_object(
        bearing_support_pair,
        options={"color": "green", "alpha": 0.5},
    )


def assembly_4oz():
    fr7 = filament_rm_7m74()
    show_object(fr7.tray_4oz(), options={"color": "blue", "alpha": 0.5})
    show_object(tin_placeholder_4oz(), options={"color": "gray", "alpha": 0.8})
    side = fr7.tray_4oz_side_transform(tin_placeholder_4oz())
    show_object(side, options={"color": "gray", "alpha": 0.8})
    show_object(side.mirror("XZ"), options={"color": "gray", "alpha": 0.8})
    show_object(
        fr7.spool_placeholder().translate((0, 0, 148)),
        options={"color": "gray", "alpha": 0.8},
    )
    show_object(
        fr7.bearing_placeholder().translate(
            (
                (fr7.spool_width / 2 - fr7.bearing_length / 2 + 1),
                -35,
                fr7.base_height + fr7.bearing_diameter_outer / 2 + 1,
            )
        ),
        options={"color": "gray", "alpha": 0.8},
    )
    bearing_support_inner, bearing_support_outer = fr7.bearing_support()
    bearing_support_pair = (bearing_support_inner + bearing_support_outer).translate(
        (0, -35, 0)
    )
    show_object(
        bearing_support_pair,
        options={"color": "green", "alpha": 0.5},
    )


def supportio():
    fr7 = filament_rm_7m74()
    fr7.tray_4oz()
    fr7.bearing_placeholder()
    inner, outer = fr7.bearing_support()
    show_object(inner, options={"color": "green", "alpha": 0.5})
    show_object(outer, options={"color": "red", "alpha": 0.5})


if "show_object" in globals():
    assembly_4oz()
