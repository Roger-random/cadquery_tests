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


class jaw_placeholder:
    def __init__(self):
        self.jaw_thickness = inch_to_mm(0.75)
        self.step_radius_1 = inch_to_mm(0.765)
        self.step_radius_2 = self.step_radius_1 + inch_to_mm(0.9)
        self.step_radius_3 = self.step_radius_2 + inch_to_mm(0.9)
        self.step_intermediate = inch_to_mm(0.025)
        self.step_height_3 = inch_to_mm(0.25)
        self.step_height_2 = (
            self.step_height_3 + self.step_intermediate + inch_to_mm(0.31)
        )
        self.step_height_1 = (
            self.step_height_2 + self.step_intermediate + inch_to_mm(0.385)
        )
        self.inner_height = inch_to_mm(0.625)

    def placeholder(self):
        back = (
            cq.Workplane("YZ")
            .circle(radius=self.step_radius_3)
            .extrude(-self.inner_height)
        )
        step_3 = (
            cq.Workplane("YZ")
            .circle(radius=self.step_radius_3)
            .extrude(self.step_height_3)
        )
        step_2 = (
            cq.Workplane("YZ")
            .circle(radius=self.step_radius_2)
            .extrude(self.step_height_2)
        )
        step_1 = (
            cq.Workplane("YZ")
            .circle(radius=self.step_radius_1)
            .extrude(self.step_height_1)
        )
        cylinders = back + step_3 + step_2 + step_1

        pentagon = (
            cq.Workplane("YZ")
            .lineTo(
                self.jaw_thickness / 2,
                math.tan(math.radians(30)) * self.jaw_thickness / 2,
            )
            .lineTo(self.jaw_thickness / 2, self.step_radius_3)
            .lineTo(-self.jaw_thickness / 2, self.step_radius_3)
            .lineTo(
                -self.jaw_thickness / 2,
                math.tan(math.radians(30)) * self.jaw_thickness / 2,
            )
            .close()
            .extrude(self.step_height_1, both=True)
        )

        return cylinders.intersect(pentagon)

    def sleeve(self, length: float, thickness: float = 0.8):
        assert length > thickness
        jaw_edge_height = math.tan(math.radians(30)) * self.jaw_thickness / 2
        jaw_thickness_half = self.jaw_thickness / 2
        gripper = (
            cq.Workplane("YZ")
            .lineTo(jaw_thickness_half, jaw_edge_height)
            .line(0, -length)
            .line(-jaw_thickness_half, -jaw_edge_height)
            .line(-jaw_thickness_half, jaw_edge_height)
            .line(0, length)
            .close()
            .extrude(self.step_height_1)
        )

        loop_outer_half = (
            cq.Workplane("YZ")
            .transformed(offset=(0, 0, self.step_height_2))
            .lineTo(0, -thickness, forConstruction=True)
            .lineTo(jaw_thickness_half + thickness, jaw_edge_height - thickness)
            .lineTo(jaw_thickness_half + thickness, self.step_radius_1 + thickness)
            .lineTo(0, self.step_radius_1 + thickness)
            .close()
            .extrude(self.step_height_1 - self.step_height_2)
        )
        loop_inner_half = (
            cq.Workplane("YZ")
            .transformed(offset=(0, 0, self.step_height_2))
            .lineTo(jaw_thickness_half, jaw_edge_height)
            .lineTo(jaw_thickness_half, self.step_radius_1)
            .lineTo(0, self.step_radius_1)
            .close()
            .extrude(self.step_height_1 - self.step_height_2)
        )

        loop_half = loop_outer_half - loop_inner_half
        loop = loop_half + loop_half.mirror("XZ")

        sleeve = loop + gripper

        return sleeve


def grip_ball(diameter: float = inch_to_mm(1)):
    grip_height = diameter / 3
    translate_z = diameter / 2 + 0.4
    j = jaw_placeholder()
    show_object(
        j.placeholder().translate((0, 0, translate_z)),
        options={"color": "green", "alpha": 0.5},
    )

    sleeve = j.sleeve(length=grip_height).translate((0, 0, translate_z))

    ball = (
        cq.Workplane("XZ")
        .sphere(radius=diameter / 2)
        .translate((j.step_height_1 - diameter * 0.2, 0, 0))
    )
    show_object(
        sleeve - ball,
        options={"color": "red", "alpha": 0.5},
    )


grip_ball()
