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


class wrench:
    """
    Partially 3D printed implementation of a pin spanner hook wrench. Such
    tools grip with a small cylindrical pin inserted into a matching hole on
    the side of the workpiece. The body of the wrench wraps around the
    cylindrical body of the workpiece anywhere from 90 to 180 degrees.
    Annoyingly, there is ambiguity in "pin wrench" because there are two types
    fitting that description. One type have the pins (and matching holes)
    coaxial with the axis of rotation, and the other perpendicular. To
    differentiate between them, the type with pin perpendicular to axis of
    rotation is sometimes called a hook wrench.

    Designs that wrap 180 degrees around the body of the workpiece need to
    have a hinge, so the pin has articulation clearance. This 3D-printable
    design skips the hinge and is dependent on flexibilty of plastic to give
    this articulation.

    The wrench body is 3D-printed, but plastic is not strong enough to be the
    pin. So this design has a hole for inserting a small metal cylinder.
    """

    def __init__(self):
        # Parameter dependent on 3D printer precision
        self.snug_fit_margin = 0.1

        # Parameter dependent on target workpiece
        self.pin_diameter = inch_to_mm(0.196)
        self.body_diameter = inch_to_mm(0.95)
        self.pin_hole_radius = self.pin_diameter / 2 + self.snug_fit_margin
        self.arch_radius_inner = self.body_diameter / 2 + self.snug_fit_margin
        self.pin_hold_length = 12

        # Not sure yet if these will stay ratios of other parameters or if
        # they should be independent parameters by themselves.
        self.thickness = self.pin_diameter * 3.5
        self.handle_width = self.thickness * 3

        # Long enough to get a good hand hold
        self.handle_length = 100

        # Arch width is a tradeoff. Too small would break, too big would
        # prevent articulation necessary for pin to fit. If tradeoff could
        # not be found, would need to add a hinge like metal wrenches.
        # Alternatively, make the pin retractable so we don't need to flex.
        self.arch_width = 10

        self.arch_radius_outer = self.arch_radius_inner + self.arch_width

    def arch(self):
        return (
            cq.Workplane("XY")
            .lineTo(self.arch_radius_inner, 0, forConstruction=True)
            .lineTo(self.arch_radius_outer, 0)
            .radiusArc(
                endPoint=(-self.arch_radius_outer, 0), radius=-self.arch_radius_outer
            )
            .lineTo(-self.arch_radius_inner, 0)
            .radiusArc(
                endPoint=(self.arch_radius_inner, 0), radius=self.arch_radius_inner
            )
            .close()
            .extrude(self.thickness / 2, both=True)
        )

    def pin_add(self):
        return (
            cq.Workplane("YZ")
            .transformed(offset=(0, 0, -self.arch_radius_inner))
            .circle(radius=self.thickness / 2)
            .extrude(-self.pin_hold_length)
            .faces("<X")
            .chamfer(length=self.pin_hole_radius)
        )

    def pin_subtract(self):
        return (
            cq.Workplane("YZ")
            .circle(radius=self.pin_hole_radius)
            .extrude(-self.arch_radius_outer - self.handle_width)
        )

    def handle_add(self):
        return (
            cq.Workplane("YZ")
            .transformed(offset=(0, 0, self.arch_radius_inner))
            .circle(radius=self.thickness / 2)
            .extrude(self.arch_width + self.handle_length)
            .faces(">X")
            .chamfer(length=self.pin_hole_radius)
        )

    def handle_add_2(self):
        return (
            cq.Workplane("XY")
            .lineTo(-self.arch_radius_inner, 0, forConstruction=True)
            .lineTo(-self.arch_radius_inner, -self.thickness / 2)
            .lineTo(-self.arch_radius_inner - self.pin_hold_length, -self.thickness / 2)
            .lineTo(-self.arch_radius_inner - self.pin_hold_length, self.thickness / 2)
            .lineTo(-self.arch_radius_inner, self.arch_radius_outer)
            .lineTo(self.arch_radius_inner, self.arch_radius_outer)
            .lineTo(self.arch_radius_inner + self.handle_length, self.thickness / 2)
            .lineTo(self.arch_radius_inner + self.handle_length, -self.thickness / 2)
            .lineTo(self.arch_radius_inner, -self.thickness / 2)
            .lineTo(self.arch_radius_inner, 0)
            .radiusArc(
                endPoint=(-self.arch_radius_inner, 0), radius=-self.arch_radius_inner
            )
            .close()
            .extrude(self.thickness / 2, both=True)
            .edges("|Z")
            .fillet(2)
        )

    def wrench(self):
        wrench = w.handle_add_2() - w.pin_subtract()

        return wrench


w = wrench()
show_object(w.wrench())
