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


class tippe_top:
    """
    A 3D-printable Tippe Tops design because they are cool.
    https://en.wikipedia.org/wiki/Tippe_top
    """

    def __init__(
        self,
        stem_radius: float = inch_to_mm(0.125),
        body_radius: float = inch_to_mm(0.6),
        body_shell_thickness: float = 0.8,
        body_truncate: float = inch_to_mm(0.2),
        cavity_height: float = 0,
        layer_thickness: float = 0.2,
    ):
        self.stem_radius = stem_radius
        self.body_radius = body_radius
        self.body_shell_thickness = body_shell_thickness
        self.body_truncate = body_truncate
        self.cavity_height = cavity_height
        self.layer_thickness = layer_thickness

    def body_exterior_volume(self):
        return cq.Workplane("XY").sphere(radius=self.body_radius)

    def body_interior_cavity(self):
        return cq.Workplane("XY").sphere(
            radius=self.body_radius - self.body_shell_thickness
        )

    def body_truncation_subtract(self):
        return (
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(0, 0, self.body_truncate - self.body_radius))
            .circle(radius=self.body_radius)
            .extrude(-self.body_radius)
        )

    def bridged_counterbore(self):
        side_half = (
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(self.stem_radius, 0, self.cavity_height))
            .line(0, self.body_radius)
            .line(self.body_radius, 0)
            .line(0, -self.body_radius * 2)
            .line(-self.body_radius, 0)
            .close()
            .extrude(self.body_radius)
        )
        paired = side_half + side_half.mirror("YZ")

        interior = (
            paired
            + paired.rotate((0, 0, 0), (0, 0, 1), 90).translate(
                (0, 0, self.layer_thickness)
            )
            + paired.rotate((0, 0, 0), (0, 0, 1), 45).translate(
                (0, 0, self.layer_thickness * 2)
            )
            + paired.rotate((0, 0, 0), (0, 0, 1), -45).translate(
                (0, 0, self.layer_thickness * 2)
            )
        )

        interior = interior.intersect(
            cq.Workplane("XY").sphere(
                radius=self.body_radius - self.body_shell_thickness / 2
            )
        )

        return interior

    def body(self):
        return (
            self.body_exterior_volume()
            - self.body_truncation_subtract()
            - self.body_interior_cavity()
            + self.bridged_counterbore()
        )


t = tippe_top()

show_object(
    t.body(),
    options={"color": "green", "alpha": 0.5},
)
