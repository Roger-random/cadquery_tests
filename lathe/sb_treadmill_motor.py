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


class sb_treadmill_motor:
    """
    Standard motor for a South Bend 9" Model A Lathe is a big industrial motor
    because that was the standard in 1942. Technology has evolved since then.
    This project supports a common hobbyist retrofit: adapting a motor salvaged
    from an exercise treadmill to drive this lathe. It can deliver more power,
    which is nice but not the goal. My primary objective is the compact size
    allowing me to shrink the footprint of the machine. The secondary objective
    is its electronically variable speed control, which opens up future project
    potential but it won't matter until this is actually worked out.
    """

    def __init__(self):
        # 3D printed mockups need a bit of margin to fit
        self.print_margin = 0.2

        # Bolt pattern via left-right and front-back spacing
        self.bolt_spacing_lr = inch_to_mm(5)
        self.bolt_spacing_fb = inch_to_mm(5 + 7 / 8)

        # Size Q drilled hole (0.332" diameter) for 5/16" thread free fit
        # Source: https://www.littlemachineshop.com/Reference/tapdrill.php
        self.bolt_hole_diameter = inch_to_mm(0.332) + self.print_margin
        self.bolt_hole_placeholder_length = 50

        # Washer for motor mounting bolt
        self.bolt_washer_diameter = inch_to_mm(0.75) + self.print_margin

        # Dimensions of the motor metal body. Actual length is longer due to:
        # Front: flange and combination flywheel+fan+output pulley on shaft
        # Back: plasatic bell housing where all the wires come in
        self.motor_diameter = 85
        self.motor_length = 140

        # Motor body has two mounting threads used as attachment points in
        # treadmill. Seems to be a confusing mix of metric (spacing as measured
        # from front flange) and imperial (1/4"-20 thread)
        self.motor_mount_1 = 30
        self.motor_mount_2 = 90

        # Size H drilled hole (0.266" diameter) for 1/4" thread free fit
        # Source: https://www.littlemachineshop.com/Reference/tapdrill.php
        self.motor_fastener_hole_diameter = inch_to_mm(0.266) + self.print_margin

        # To align with existing pulley, the front of motor body should
        # be about this far away from the left most set of bolts
        self.motor_position = inch_to_mm(3)
        self.motor_height_offset = -inch_to_mm(0.150)

    def bolt_placeholders(self):
        return (
            cq.Workplane("YZ")
            .rect(
                xLen=self.bolt_spacing_fb,
                yLen=self.bolt_spacing_lr,
                forConstruction=True,
            )
            .vertices()
            .circle(radius=self.bolt_hole_diameter / 2)
            .extrude(self.bolt_hole_placeholder_length, both=True)
        )

    def motor_placeholder(self):
        body = (
            cq.Workplane("XZ")
            .transformed(
                offset=(
                    (self.motor_diameter / 2) + self.motor_height_offset,
                    0,
                    self.bolt_spacing_lr / 2 + self.motor_position,
                )
            )
            .circle(radius=self.motor_diameter / 2)
            .extrude(-self.motor_length)
        )

        mount_point = (
            cq.Workplane("YZ")
            .transformed(
                offset=(
                    -self.bolt_spacing_lr / 2 - self.motor_position,
                    0,
                    (self.motor_diameter / 2) + self.motor_height_offset,
                )
            )
            .transformed(rotate=(90, 0, 0))
            .circle(radius=self.motor_fastener_hole_diameter / 2)
            .extrude(-self.motor_diameter)
        )

        return (
            body
            - mount_point.translate((0, self.motor_mount_1, 0))
            - mount_point.translate((0, self.motor_mount_2, 0))
        )


stm = sb_treadmill_motor()

show_object(stm.bolt_placeholders(), options={"color": "gray", "alpha": 0.25})

show_object(stm.motor_placeholder(), options={"color": "gray", "alpha": 0.25})
