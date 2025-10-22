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


class sb_switch_box:
    """
    Mounting box for a paddle switch, which is turned on by a small recessed
    button that is difficult to press by accident. In contrast, there is a
    large paddle so turning it off is very easy. This assymetry is useful in
    case of emergency when I'm likely frantic for some other reason.

    https://www.grizzly.com/products/woodstock-110v-paddle-switch/d4160
    """

    def __init__(self):
        # Extra margin for 3D printed parts to fit.
        self.print_margin = 0.2

        # Relevant table dimensions.  The coordinate zero point is the inner
        # corner where bottom of the table and outer surface of the support
        # beam meet.
        self.table_depth_front = inch_to_mm(2 + 3 / 8)
        self.table_beam_height = inch_to_mm(1 + 3 / 4)
        self.table_beam_depth = inch_to_mm(1 + 1 / 16)
        self.table_inner_height = inch_to_mm(7 / 8)
        self.table_thickness = inch_to_mm(0.5)

        # Wood screw to fasten to table
        self.table_screw_diameter = inch_to_mm(0.175) + self.print_margin * 2
        self.table_screw_length = inch_to_mm(1) + self.print_margin
        self.table_screw_head_diameter = inch_to_mm(0.3) + self.print_margin * 2
        self.table_screw_head_height = inch_to_mm(0.1)

        # Relevant paddle switch dimensions.
        self.switch_height = inch_to_mm(4.4)
        self.switch_width = inch_to_mm(2.650)
        self.switch_panel_depth = inch_to_mm(1.6)  # Includes paddle
        self.switch_fastener_distance = inch_to_mm(3.29)
        self.switch_fastener_hole_diameter = 3.0  # M3 as self-tapping screw
        self.switch_opening_height = inch_to_mm(3)
        self.switch_opening_width = inch_to_mm(2)
        self.switch_rear_clearance = inch_to_mm(4)

        # Paddle switch placement distance of upper inner edge relative to
        # table bottom beam corner.
        self.switch_offset_depth = self.table_depth_front - self.switch_panel_depth
        self.switch_offset_height = inch_to_mm(0.25)

        self.box_fillet = 5
        self.box_bottom_thickness = 5

    def table_placeholder(self):
        """
        Placeholder object representing the table this box will be mounted
        under.
        Not precise because the table is built of warped wood pieces.
        """
        return (
            cq.Workplane("YZ")
            .line(0, -self.table_beam_height)
            .line(self.table_beam_depth, 0)
            .line(0, self.table_inner_height)
            .line(self.table_depth_front, 0)
            .line(
                0,
                self.table_thickness + self.table_beam_height - self.table_inner_height,
            )
            .lineTo(-self.table_depth_front, self.table_thickness)
            .line(0, -self.table_thickness)
            .close()
            .extrude(self.switch_width, both=True)
        )

    def table_fit_test_template(self):
        """
        Thin printed piece to hold up against actual table to verify table
        placeholder dimensions are good enough.
        Not precise because the table is built of warped wood pieces.
        """
        return (
            cq.Workplane("YZ")
            .line(-self.table_depth_front, 0)
            .line(0, -self.table_beam_height * 1.5)
            .line(self.table_depth_front * 2, 0)
            .line(0, self.table_beam_height * 1.5)
            .close()
            .extrude(5)
        ) - self.table_placeholder()

    def paddle_switch_placeholder(self):
        """
        Placeholder object representing the paddle switch that will be mounted
        to table.
        """
        panel = cq.Workplane("XZ").box(
            length=self.switch_width,
            width=self.switch_height,
            height=self.switch_panel_depth,
            centered=(True, True, False),
        )

        switch = (
            cq.Workplane("XZ")
            .box(
                length=self.switch_opening_width,
                width=self.switch_opening_height,
                height=self.switch_rear_clearance,
                centered=(True, True, False),
            )
            .mirror("XZ")
            .edges("|Y")
            .fillet(self.box_fillet)
        )

        fastener = (
            cq.Workplane("XZ")
            .transformed(offset=(0, self.switch_fastener_distance / 2, 0))
            .circle(radius=self.switch_fastener_hole_diameter / 2)
            .extrude(-self.switch_rear_clearance)
        )

        placeholder = (panel + switch + fastener + fastener.mirror("XY")).translate(
            (
                0,
                -self.switch_offset_depth,
                -self.switch_height / 2 - self.switch_offset_height,
            )
        )

        return placeholder

    def wood_screw_clearance(self):
        return (
            cq.Workplane("XY")
            # Screw head
            .circle(radius=self.table_screw_head_diameter / 2)
            .workplane(offset=self.table_screw_head_height)
            .circle(radius=self.table_screw_diameter / 2)
            .loft()
            # Screw shaft
            .faces(">Z")
            .workplane()
            .circle(radius=self.table_screw_diameter / 2)
            .extrude(self.table_screw_length)
            # Screwdriver reach
            .faces("<Z")
            .workplane()
            .circle(radius=self.table_screw_head_diameter * 0.75)
            .workplane(offset=self.table_screw_length)
            .circle(radius=self.table_screw_head_diameter * 0.75)
            .loft()
        )

    def box(self):
        rear_slope_distance = (
            self.switch_height + self.switch_offset_height - self.table_beam_height
        )
        profile = (
            cq.Workplane("YZ")
            .line(-self.print_margin, -self.print_margin, forConstruction=True)
            .lineTo(-self.switch_offset_depth, -self.print_margin)
            .lineTo(
                -self.switch_offset_depth,
                -self.switch_offset_height - self.switch_height + self.print_margin,
            )
            .lineTo(
                -self.switch_offset_depth + self.box_bottom_thickness,
                -self.switch_offset_height - self.switch_height + self.print_margin,
            )
            .line(rear_slope_distance, rear_slope_distance)
            .line(0, self.table_inner_height - self.print_margin * 2)
            .lineTo(
                self.table_beam_depth + self.print_margin,
                -self.table_beam_height + self.table_inner_height - self.print_margin,
            )
            .line(0, -self.table_inner_height)
            .line(-self.table_beam_depth - self.print_margin * 2, 0)
            .close()
            .extrude(self.switch_width / 2, both=True)
        )

        # Round things off to help with printing

        # Bottom
        profile = profile.faces("<Z").edges("|Y").fillet(self.box_fillet)

        # Top
        profile = profile.faces(">Z").edges("|Y").fillet(self.box_fillet)

        # Back
        profile = profile.faces(">Y").edges("|Z").fillet(self.box_fillet)

        # Cut holes to clear other components
        box = (
            profile
            - self.paddle_switch_placeholder()
            - self.wood_screw_clearance().translate(
                (
                    0,
                    self.table_beam_depth + inch_to_mm(0.5),
                    -self.table_beam_height
                    + self.table_inner_height
                    - self.table_screw_head_height,
                )
            )
            - self.wood_screw_clearance()
            .rotate((0, 0, 0), (1, 0, 0), -90)
            .translate(
                (
                    0,
                    -inch_to_mm(0.2),
                    -(
                        self.switch_offset_height
                        + (self.switch_height - self.switch_opening_height) / 2
                    )
                    / 2,
                )
            )
        )

        return box


ssb = sb_switch_box()

show_object(ssb.table_placeholder(), options={"color": "gray", "alpha": 0.25})

show_object(ssb.paddle_switch_placeholder(), options={"color": "gray", "alpha": 0.25})

show_object(ssb.box(), options={"color": "green", "alpha": 0.5})
