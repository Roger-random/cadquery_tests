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


class sb_belt_tensioner:
    """
    A 9" South Bend HMD (horizontal motor drive) lathe is designed to have a
    belt tensioning mechanism sitting between the lathe headstock and motor
    countershaft assembly. It includes a tension release lever so the belt can
    be moved to a different pulley for a different speed.

    This lever is missing on my lathe. Plus in the interest of reducing machine
    footprint I'm moving the countershaft assembly closer to the lathe (with
    help of a compact treadmill motor) so the original belt tension lever would
    not work anyway.

    Hence this 3D printed project to figure out the dimensions I'd need for my
    setup. 3D printed plastic can be decently strong in compression so there's
    a chance it'll work as-is without having to be redone in metal. So geometry
    will be optimized for 3D printing. If I have to redo this in metal I'll
    revisit the design to make it easier to mill out on a Bridgeport.

    Because the countershaft assembly can be freely installed in a range of
    positions relative to the lathe headstock, many of the dimensions will only
    work for specific setups. Further complicating dimensions, There isn't a
    nice flat machined surface to serve as obvious datum point.

    I'll start V1 by using the headstock 3/8" hole's right-side surface.
    """

    def __init__(self) -> None:
        # 3D Printer error margin
        self.print_margin = 0.2

        # Headstock
        self.headstock_hole_diameter = inch_to_mm(3 / 8)
        self.headstock_hole_length = inch_to_mm(0.77)  # 3/4" but oversized?

        # Motor drive
        self.drive_hole_diameter = inch_to_mm(3 / 8)
        self.drive_hole_length = inch_to_mm(0.5)  # 1/2" but undersized?

        # Relative positioning
        self.distance_fb = inch_to_mm(8.5)
        self.distance_lr = inch_to_mm(0)  # TBD

        # Lever dimensions
        self.lever_offset_lr = inch_to_mm(0.25)  # Clear back gear shaft
        self.lever_width = inch_to_mm(1)
        self.lever_thickness = inch_to_mm(0.25)
        self.lever_length = inch_to_mm(4)

    def front_lever(self):
        offset_cylinder = (
            cq.Workplane("YZ")
            .transformed(offset=(0, 0, self.lever_offset_lr))
            .circle(radius=self.lever_width / 2)
            .circle(radius=(self.headstock_hole_diameter / 2) + self.print_margin)
            .extrude(-self.lever_offset_lr)
        )

        lever_rod = (
            cq.Workplane("YZ")
            .transformed(offset=(0, 0, self.lever_offset_lr))
            .line(0, self.lever_width / 2)
            .line(self.lever_length, 0)
            .tangentArcPoint((0, -self.lever_width))
            .line(-self.lever_length, 0)
            .tangentArcPoint((0, self.lever_width))
            .close()
            .extrude(self.lever_thickness)
        )

        lever_rod_hole_subtract = (
            cq.Workplane("YZ")
            .circle(radius=self.headstock_hole_diameter / 2 + self.print_margin)
            .extrude(self.lever_length, both=True)
        )

        lever_rod = (
            lever_rod
            - lever_rod_hole_subtract
            - lever_rod_hole_subtract.translate((0, self.lever_length, 0))
        )

        lever = offset_cylinder + lever_rod

        return lever


sbt = sb_belt_tensioner()

show_object(sbt.front_lever(), options={"color": "blue", "alpha": 0.25})
