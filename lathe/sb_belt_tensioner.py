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

        # Relative positioning between headstock and motor stand
        self.distance_fb = inch_to_mm(8.5)
        self.distance_lr = inch_to_mm(0.075)

        # Lever
        self.lever_offset_lr = inch_to_mm(0.25)  # Clear back gear shaft
        self.lever_offset_taper = inch_to_mm(0.05)  # Conform to casting surface
        self.lever_width = inch_to_mm(1)
        self.lever_thickness = inch_to_mm(0.5)
        self.lever_length = inch_to_mm(4)
        self.lever_retention_clip = inch_to_mm(0.075)

        # Pivot pin
        self.pivot_range_degrees = 60
        self.pivot_over_angle_degrees = 5
        self.pivot_diameter = inch_to_mm(3 / 8)
        self.pivot_length = inch_to_mm(1)
        self.pivot_rod_diameter = inch_to_mm(0.25)

        self.pivot_pin_surround_radius = self.pivot_diameter * 1.5

    def pivot_pin(self):
        pin_body = (
            cq.Workplane("YZ")
            .circle(radius=self.pivot_diameter / 2)
            .extrude(-self.pivot_length)
            .translate(
                (
                    self.lever_offset_lr + self.lever_thickness - self.distance_lr,
                    0,
                    0,
                )
            )
            .edges()
            .chamfer(0.5)
        )
        pivot_rod = (
            cq.Workplane("XZ")
            .circle(radius=self.pivot_rod_diameter / 2 - self.print_margin)
            .extrude(self.pivot_diameter, both=True)
        )
        return pin_body - pivot_rod

    def pivot_pin_slice(self):
        slice_intersect = (
            cq.Workplane("XZ")
            .transformed(offset=(0, 0, -inch_to_mm(0.1)))
            .rect(self.lever_length, self.lever_length)
            .extrude(self.pivot_diameter)
        )

        pin_slice = (
            self.pivot_pin()
            .intersect(slice_intersect)
            .translate(
                (
                    self.distance_lr,
                    self.lever_length,
                    0,
                )
            )
        )

        return pin_slice

    def pivot_pin_half(self):
        half_intersect = (
            cq.Workplane("XY")
            .rect(self.lever_length, self.lever_length)
            .extrude(self.pivot_diameter)
        )

        pin_half = (
            self.pivot_pin()
            .intersect(half_intersect)
            .translate(
                (
                    self.distance_lr,
                    self.lever_length,
                    0,
                )
            )
        )

        return pin_half

    def front_lever(self):
        offset_cone_intersect = (
            cq.Workplane("YZ")
            .line(0, self.lever_width / 2)
            .line(self.lever_length, 0)
            .line(0, -self.lever_width)
            .line(-self.lever_length, 0)
            .tangentArcPoint((0, self.lever_width))
            .close()
            .extrude(self.lever_offset_lr)
        )
        offset_cone = (
            cq.Workplane("YZ")
            .circle(radius=(self.headstock_hole_diameter / 2) + self.print_margin)
            .workplane(offset=self.lever_offset_taper)
            .circle(radius=self.lever_width / 2)
            .loft()
            .faces(">X")
            .workplane()
            .circle(radius=self.lever_width / 2)
            .workplane(offset=self.lever_offset_lr - self.lever_offset_taper)
            .circle(radius=self.lever_width / 2 + self.lever_offset_lr)
            .loft()
            .intersect(offset_cone_intersect)
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

        lever_pin_subtract = (
            cq.Workplane("YZ")
            .circle(radius=self.headstock_hole_diameter / 2 + self.print_margin)
            .extrude(self.lever_length, both=True)
        )

        pivot_pin_surround = (
            cq.Workplane("YZ")
            .circle(radius=self.pivot_pin_surround_radius)
            .extrude(
                -self.pivot_length  #  * 0.65 for test print without support requirement
            )
            .translate(
                (self.lever_offset_lr + self.lever_thickness, self.lever_length, 0)
            )
        )

        pivot_pin_subtract = (
            cq.Workplane("YZ")
            .circle(radius=self.pivot_diameter / 2 + self.print_margin)
            .extrude(self.pivot_length, both=True)
            .translate((0, self.lever_length, 0))
        )

        # The most complicated part: remove volume required for pivot rod
        # range of
        pivot_subtract_radius = self.pivot_pin_surround_radius * 2
        pivot_rod_subtract = (
            cq.Workplane("XZ")
            .circle(radius=self.pivot_rod_diameter / 2)
            .extrude(pivot_subtract_radius, both=True)
        )

        pivot_range_subtract = (
            cq.Workplane("YZ")
            .lineTo(-pivot_subtract_radius, 0)
            .radiusArc(
                (
                    -pivot_subtract_radius
                    * math.cos(math.radians(self.pivot_range_degrees)),
                    pivot_subtract_radius
                    * math.sin(math.radians(self.pivot_range_degrees)),
                ),
                radius=pivot_subtract_radius,
            )
            .close()
            .extrude(self.pivot_rod_diameter / 2, both=True)
        )

        pivot_range_subtract = (
            (
                pivot_range_subtract
                + pivot_range_subtract.mirror("XZ").mirror("XY")
                + pivot_rod_subtract
                + pivot_rod_subtract.rotate(
                    (0, 0, 0), (1, 0, 0), -self.pivot_range_degrees
                )
            )
            .rotate((0, 0, 0), (1, 0, 0), self.pivot_over_angle_degrees)
            .translate((self.distance_lr, self.lever_length, 0))
        )

        lever = (
            offset_cone
            + lever_rod
            + pivot_pin_surround
            - lever_pin_subtract
            - pivot_pin_subtract
            - pivot_range_subtract
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
                radius=(self.headstock_hole_diameter / 2) - self.lever_retention_clip
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
                radius=(self.headstock_hole_diameter / 2) - self.lever_retention_clip
            )
            .extrude(-clip_thickness)
        )

        clip_interior_rect_half = (
            cq.Workplane("YZ")
            .transformed(offset=clip_transform)
            .line(
                (self.headstock_hole_diameter / 2)
                - self.lever_retention_clip
                - self.print_margin * 2,
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

    def vise_block(self):
        """
        3D printed blocks to help hold ~380" diameter aluminum pins in a vise
        so I can drill and tap 1/4"-20 threads in them.
        """
        # Small gap between pieces to give vise room to squeeze and deform
        # for custom fit
        clamp_gap = 1

        pin_diameter = inch_to_mm(0.380)

        block_height = inch_to_mm(0.5)
        block_length = inch_to_mm(1.5)
        block_width = inch_to_mm(0.5)

        block = cq.Workplane("XY").box(block_length, block_height, block_width)

        pin = (
            cq.Workplane("YZ")
            .circle(radius=pin_diameter / 2)
            .extrude(block_length, both=True)
        )

        rod = (
            cq.Workplane("XZ")
            .circle(radius=inch_to_mm(1 / 8))
            .extrude(block_height, both=True)
        )

        block_intersect = (
            cq.Workplane("XY")
            .transformed(offset=(0, 0, -clamp_gap))
            .rect(block_length, block_height)
            .extrude(-block_width)
        )

        return (block - pin - rod).intersect(block_intersect).edges("|Z").fillet(3)


sbt = sb_belt_tensioner()

show_object(sbt.front_lever(), options={"color": "blue", "alpha": 0.25})
show_object(
    sbt.front_lever_pin_placeholder(), options={"color": "green", "alpha": 0.25}
)

show_object(sbt.front_lever_pin_clip(), options={"color": "red", "alpha": 0.25})
show_object(sbt.pivot_pin_slice(), options={"color": "yellow", "alpha": 0.25})

show_object(
    sbt.vise_block().translate((0, -inch_to_mm(2), 0)),
    options={"color": "purple", "alpha": 0.25},
)
