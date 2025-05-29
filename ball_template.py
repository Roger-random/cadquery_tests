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


class ball_template:
    """
    There's no ball cutting attachment for the manual lathe (yet?) so use a
    3D-printed template as reference to carefully cut one manually.
    """

    def __init__(
        self,
        radius: float = inch_to_mm(0.5),
        thickness: float = 2,
        margin=inch_to_mm(0.25),
        fillet: float = 3,
    ):
        self.radius = radius
        self.thickness = thickness
        self.margin = margin
        self.fillet = fillet

    def hemisphere(self):
        plate = (
            cq.Workplane("XY")
            .box(
                length=self.radius * 2 + self.margin,
                width=self.radius + self.margin,
                height=self.thickness,
                centered=(False, False, True),
            )
            .edges("|Z")
            .fillet(self.fillet)
        )

        cylinder = cq.Workplane("YZ").cylinder(
            height=self.radius * 2, radius=self.radius
        )

        ball = (
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(self.radius, 0, 0))
            .sphere(radius=self.radius)
        )
        return plate - (cylinder + ball)


t = ball_template()

show_object(t.hemisphere())
