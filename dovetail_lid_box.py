"""
MIT License

Copyright (c) 2025 Roger Cheng

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

# When not running in CQ-Editor, turn log into print
if "log" not in globals():

    def log(*args):
        print(args)


# When not running in CQ-Editor, turn show_object into no-op
if "show_object" not in globals():

    def show_object(*args, **kwargs):
        pass


def inch_to_mm(length_inch: float):
    return length_inch * 25.4


class box:
    def __init__(
        self,
        length: float,
        width: float,
        height: float,
        lid_thickness: float = 1.2,
        dovetail_thickness: float = 2.4,
        dovetail_width: float = 3,
        dovetail_bump_width: float = 0.4,
        dovetail_bump_radius: float = 5,
        corner_fillet: float = 3,
        face_chamfer: float = 0.8,
    ):
        self.length = length
        self.width = width
        self.height = height
        self.lid_thickness = lid_thickness
        self.dovetail_thickness = dovetail_thickness
        self.dovetail_width = dovetail_width
        self.dovetail_bump_width = dovetail_bump_width
        self.dovetail_bump_radius = dovetail_bump_radius
        self.corner_fillet = corner_fillet
        self.face_chamfer = face_chamfer

    def dovetail_profile(self, workplane: cq.Workplane):
        return (
            workplane.line(0, self.height, forConstruction=True)
            .line(self.width / 2, 0)
            .line(0, -self.lid_thickness - self.dovetail_thickness)
            .line(-self.dovetail_width, 0)
            .line(
                self.dovetail_thickness / 2,
                self.dovetail_thickness,
            )
            .lineTo(0, self.height - self.lid_thickness)
            .close()
        )

    def dovetail_bump_profile(self, workplane: cq.Workplane):
        bump_max_y = self.width / 2 - self.dovetail_width + self.dovetail_bump_width
        return (
            workplane.lineTo(0, bump_max_y)
            .radiusArc(
                endPoint=(
                    self.dovetail_bump_radius,
                    bump_max_y - self.dovetail_bump_radius,
                ),
                radius=self.dovetail_bump_radius,
            )
            .close()
        )

    def lid(self):
        majority = self.dovetail_profile(cq.Workplane("YZ")).extrude(
            self.length / 2 - self.corner_fillet
        )

        edge = (
            self.dovetail_profile(majority.faces(">X").workplane())
            .workplane(offset=self.corner_fillet)
            .line(0, self.height, forConstruction=True)
            .line(self.width / 2, 0)
            .line(0, -self.lid_thickness - self.dovetail_thickness)
            .line(-1, 0)
            .lineTo(
                self.width / 2 - self.dovetail_width / 2,
                self.height - self.lid_thickness,
            )
            .lineTo(0, self.height - self.lid_thickness)
            .close()
            .loft()
        )

        quarter = majority + edge

        if self.dovetail_bump_width > 0:
            quarter = quarter - self.dovetail_bump_profile(cq.Workplane("XY")).extrude(
                self.height - self.lid_thickness
            )

        half = quarter + quarter.mirror("YZ")

        lid = half + half.mirror("XZ")

        lid = lid.intersect(self.box_volume())

        return lid

    def box_volume(self):
        return (
            cq.Workplane("XY")
            .box(self.length, self.width, self.height, centered=(True, True, False))
            .edges("|Z")
            .fillet(self.corner_fillet)
            .faces("<Z or >Z")
            .chamfer(self.face_chamfer)
        )

    def base(self):
        base_subtract_quarter = self.dovetail_profile(cq.Workplane("YZ")).extrude(
            self.length
        )

        if self.dovetail_bump_width > 0:
            base_subtract_quarter = base_subtract_quarter - self.dovetail_bump_profile(
                cq.Workplane("XY")
            ).extrude(self.height - self.lid_thickness)

        base_subtract_half = base_subtract_quarter + base_subtract_quarter.mirror("YZ")

        base_subtract = base_subtract_half + base_subtract_half.mirror("XZ")

        return self.box_volume() - base_subtract


def bearing_ball_pair():
    generator = box(
        length=inch_to_mm(3),
        width=inch_to_mm(1.75),
        height=inch_to_mm(1.5),
        dovetail_bump_width=0,
    )
    base = generator.base()

    ball_radius_clear = 17
    ball_center_x = ball_radius_clear + 1
    ball_center_y = 1.5
    ball_center_z = generator.height - generator.lid_thickness - ball_radius_clear
    ball_subtract = cq.Workplane("XY").sphere(radius=ball_radius_clear) + (
        cq.Workplane("XY").circle(radius=ball_radius_clear).extrude(ball_radius_clear)
    )

    base = (
        base
        - ball_subtract.translate((ball_center_x, ball_center_y, ball_center_z))
        - ball_subtract.translate((-ball_center_x, -ball_center_y, ball_center_z))
    )

    show_object(
        generator.lid(),
        options={"color": "red", "alpha": 0.5},
    )

    show_object(
        base,
        options={"color": "green", "alpha": 0.5},
    )


bearing_ball_pair()
