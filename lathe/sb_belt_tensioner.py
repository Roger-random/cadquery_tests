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
        self.headstock_hole_diameter = inch_to_mm(0.388)
        self.headstock_hole_length = inch_to_mm(0.82)

        # Motor stand
        self.stand_hole_diameter = inch_to_mm(3 / 8)
        self.stand_hole_length = inch_to_mm(0.5)  # 1/2" but undersized?

        # Relative positioning
        self.distance_fb = inch_to_mm(8.5)
        self.distance_lr = inch_to_mm(0)  # TBD

        # Lever
        self.lever_offset_lr = inch_to_mm(0.25)  # Clear back gear shaft
        self.lever_offset_taper = inch_to_mm(0.05)  # Conform to casting surface
        self.lever_width = inch_to_mm(1)
        self.lever_thickness = inch_to_mm(0.25)
        self.lever_length = inch_to_mm(4)
        self.lever_retention_clip = inch_to_mm(0.075)

    def front_lever(self):
        offset_cylinder = (
            cq.Workplane("YZ")
            .transformed(offset=(0, 0, self.lever_offset_lr))
            .circle(radius=self.lever_width / 2)
            .extrude(-self.lever_offset_lr - self.lever_offset_taper)
            .faces("<X")
            .workplane()
            .circle(radius=self.lever_width / 2)
            .workplane(offset=self.lever_offset_taper)
            .circle(radius=(self.headstock_hole_diameter / 2) + self.print_margin * 2)
            .loft()
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

        lever = (
            offset_cylinder
            + lever_rod
            - lever_rod_hole_subtract
            - lever_rod_hole_subtract.translate((0, self.lever_length, 0))
        )

        return lever

    def front_lever_pin_placeholder(self):
        """
        3D-printed placeholder for metal pins
        """
        pin_body = (
            cq.Workplane("YZ")
            # Section inside lever
            .circle(radius=(self.headstock_hole_diameter / 2) - self.print_margin)
            .extrude(self.lever_offset_lr + self.lever_thickness + self.print_margin)
            # Wider section to hold lever
            .faces(">X")
            .workplane()
            .circle(radius=self.headstock_hole_diameter)
            .extrude(self.headstock_hole_diameter / 4)
            # Other side: section inside headstock
            .faces("<X")
            .workplane()
            .circle(radius=(self.headstock_hole_diameter / 2) - self.print_margin)
            .extrude(self.headstock_hole_length)
            # Slot for retention clip
            .faces("<X")
            .workplane()
            .circle(
                radius=(self.headstock_hole_diameter / 2)
                - self.lever_retention_clip
                - self.print_margin
            )
            .extrude(self.lever_retention_clip)
            # Hold retention clip
            .faces("<X")
            .workplane()
            .circle(radius=(self.headstock_hole_diameter / 2) - self.print_margin)
            .extrude(self.lever_retention_clip)
        )

        # Slice in half for printing
        half_slice = (
            cq.Workplane("XY")
            .rect(self.lever_length, self.lever_length)
            .extrude(self.lever_length)
        )

        placeholder = pin_body.intersect(half_slice)

        return placeholder

    def front_lever_pin_clip(self):
        clip_transform = (0, 0, -self.headstock_hole_length - self.print_margin)
        clip_thickness = self.lever_retention_clip - self.print_margin * 2
        clip_exterior = (
            cq.Workplane("YZ")
            .transformed(offset=clip_transform)
            .circle(
                radius=(self.headstock_hole_diameter / 2)
                + self.lever_retention_clip
                + self.print_margin
            )
            .extrude(-clip_thickness)
        )

        clip_interior_circle = (
            cq.Workplane("YZ")
            .transformed(offset=clip_transform)
            .circle(
                radius=(self.headstock_hole_diameter / 2)
                - self.lever_retention_clip
                + self.print_margin
            )
            .extrude(-clip_thickness)
        )

        clip_interior_rect_half = (
            cq.Workplane("YZ")
            .transformed(offset=clip_transform)
            .line(
                (self.headstock_hole_diameter / 2)
                - self.lever_retention_clip
                - self.print_margin,
                0,
            )
            .line(0, -self.lever_width)
            .lineTo(0, -self.lever_width)
            .close()
            .extrude(-clip_thickness)
        )

        clip_interior_rect = clip_interior_rect_half + clip_interior_rect_half.mirror(
            "XZ"
        )

        clip_loop_radius_outer = inch_to_mm(0.4)
        clip_loop_radius_inner = inch_to_mm(0.3)
        clip_loop = (
            cq.Workplane("YZ")
            .transformed(offset=clip_transform)
            .transformed(
                offset=(
                    0,
                    self.headstock_hole_diameter / 2
                    + self.lever_retention_clip
                    + clip_loop_radius_inner
                    + self.print_margin,
                    0,
                )
            )
            .circle(radius=clip_loop_radius_outer)
            .circle(radius=clip_loop_radius_inner)
            .extrude(-clip_thickness)
        )

        clip = clip_exterior + clip_loop - clip_interior_circle - clip_interior_rect

        return clip


sbt = sb_belt_tensioner()

show_object(sbt.front_lever(), options={"color": "blue", "alpha": 0.25})
show_object(
    sbt.front_lever_pin_placeholder(), options={"color": "green", "alpha": 0.25}
)

show_object(sbt.front_lever_pin_clip(), options={"color": "red", "alpha": 0.25})
