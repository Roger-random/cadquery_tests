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
        self.bracket_wall_thickness = 10

        # 3D printed mockups need a bit of margin to fit
        self.print_margin = 0.2

        # 3D printed counterbore holes facing print bed will be bridged for
        # printing to avoid supports, need to be drilled out before use.
        self.counterbore_bridge_thickness = 0.5

        # Bolt pattern via left-right and front-back spacing
        self.bolt_spacing_lr = inch_to_mm(5)
        self.bolt_spacing_fb = inch_to_mm(5 + 7 / 8)

        # Size Q drilled hole (0.332" diameter) for 5/16" thread free fit
        # Source: https://www.littlemachineshop.com/Reference/tapdrill.php
        # Any additional room is extra allowance for fine position adjustment.
        self.bolt_hole_diameter = inch_to_mm(0.4) + self.print_margin
        self.bolt_hole_thickness = 10
        self.bolt_hole_surround_size = 20
        self.bolt_washer_diameter = inch_to_mm(1) + self.print_margin
        self.bolt_hole_placeholder_length = 150

        # Dimensions of the motor metal body. Actual length is longer due to:
        # Front: flange and combination flywheel+fan+output pulley on shaft
        # Back: plasatic bell housing where all the wires come in
        self.motor_diameter = 85
        self.motor_length = 140
        self.motor_endbell_diameter = 100
        self.motor_endbell_length = 100

        # Motor body has two mounting threads used as attachment points in
        # treadmill. Seems to be a confusing mix of metric (spacing as measured
        # from front flange) and imperial (1/4"-20 thread)
        self.motor_mount_1 = 30
        self.motor_mount_2 = 90

        # Size H drilled hole (0.266" diameter) for 1/4" thread free fit
        # Source: https://www.littlemachineshop.com/Reference/tapdrill.php
        self.motor_fastener_hole_diameter = inch_to_mm(0.266) + self.print_margin
        self.motor_fastener_wall_thickness = 3
        self.motor_fastener_head_diameter = inch_to_mm(0.75) + self.print_margin

        # I have 1/4"-20 threaded rod to hold the two halves together, recycle
        # values for 1/4"-2o from motor fastener
        self.cross_rod_hole_diameter = self.motor_fastener_hole_diameter
        self.cross_rod_wall_thickness = 12
        self.cross_rod_head_length = (
            self.motor_diameter / 2
            + self.motor_fastener_wall_thickness
            - self.bracket_wall_thickness
            + self.cross_rod_wall_thickness
        )
        self.cross_rod_head_diaameter = self.motor_fastener_head_diameter
        self.cross_rod_brace_height = 15

        # To align with existing pulley, the front of motor body should
        # be about this far away from the left most set of bolts
        self.motor_position = inch_to_mm(3)

        # Machined motor mount surface is a little bit above casting center
        # surface. Take advantage of it by sinking motor into that gap.
        self.motor_height_offset = -inch_to_mm(0.175)

        # Calculated values shared by multiple methods.
        self.motor_front = -self.bolt_spacing_lr / 2 - self.motor_position

    def bolt_placeholders(self):
        stem = (
            cq.Workplane("YZ")
            .rect(
                xLen=self.bolt_spacing_lr,
                yLen=self.bolt_spacing_fb,
                forConstruction=True,
            )
            .vertices()
            # FDM printers have a hard time printing horizontal cylindrical
            # walls so switch to a polygon
            .polygon(6, diameter=self.bolt_hole_diameter, circumscribed=True)
            .extrude(self.bolt_hole_placeholder_length)
        )
        head = (
            cq.Workplane("YZ")
            .transformed(offset=(0, 0, self.bolt_hole_thickness))
            .rect(
                xLen=self.bolt_spacing_lr,
                yLen=self.bolt_spacing_fb,
                forConstruction=True,
            )
            .vertices()
            # Again technically a cylinder but make polygon for easier printing.
            .polygon(6, diameter=self.bolt_washer_diameter, circumscribed=True)
            .extrude(self.bolt_hole_placeholder_length)
        )

        return stem + head

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
            .faces(">Y")
            .workplane()
            .circle(radius=self.motor_endbell_diameter / 2)
            .extrude(self.motor_endbell_length)
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

    def cross_rod_placeholder(self):
        rod = (
            cq.Workplane("XY")
            .transformed(
                offset=(
                    self.motor_diameter
                    + self.motor_height_offset
                    + self.cross_rod_hole_diameter / 2,
                    self.motor_front + self.cross_rod_brace_height / 2,
                    0,
                )
            )
            .circle(radius=self.cross_rod_hole_diameter / 2)
            .extrude(self.cross_rod_head_length - self.counterbore_bridge_thickness)
            .faces(">Z")
            .workplane(offset=self.counterbore_bridge_thickness)
            .circle(radius=self.cross_rod_head_diaameter / 2)
            .extrude(self.cross_rod_head_length)
        )
        return rod + rod.translate(
            (0, self.motor_length - self.cross_rod_brace_height, 0)
        )

    def bracket(self):
        motor_rear = self.motor_front + self.motor_length
        bracket_top = self.bolt_spacing_fb / 2 + self.bolt_hole_surround_size
        bracket_top_left = -self.bolt_spacing_lr / 2 - self.bolt_hole_surround_size
        bracket_top_right = -bracket_top_left
        bracket_bottom = (
            self.motor_diameter / 2
            + self.motor_fastener_wall_thickness
            - self.bracket_wall_thickness
        )
        block_height = (
            self.motor_diameter + self.motor_height_offset + self.cross_rod_brace_height
        )

        bracket_block = (
            cq.Workplane("YZ")
            .lineTo(self.motor_front, bracket_bottom, forConstruction=True)
            .line(0, self.bracket_wall_thickness)
            .lineTo(bracket_top_left, bracket_top)
            .lineTo(bracket_top_right, bracket_top)
            .line(0, -self.bolt_hole_surround_size * 2)
            .lineTo(motor_rear, bracket_bottom)
            .close()
            .extrude(block_height)
        )

        motor_fastener = (
            cq.Workplane("XY")
            .transformed(
                offset=(
                    self.motor_diameter / 2 + self.motor_height_offset,
                    self.motor_front,
                    bracket_bottom,
                )
            )
            .circle(radius=self.motor_fastener_hole_diameter / 2)
            .extrude(self.bracket_wall_thickness - self.counterbore_bridge_thickness)
            .faces(">Z")
            .workplane(offset=self.counterbore_bridge_thickness)
            .circle(radius=self.motor_fastener_head_diameter / 2)
            .extrude(bracket_top)
        )

        bracket_rectangular = (
            bracket_block.edges("|Z").fillet(self.bracket_wall_thickness)
            - self.motor_placeholder()
            - motor_fastener.translate((0, self.motor_mount_1, 0))
            - motor_fastener.translate((0, self.motor_mount_2, 0))
            - self.cross_rod_placeholder()
            - self.bolt_placeholders()
        )

        bracket_wedge_intersect_xz = (
            cq.Workplane("XZ")
            .lineTo(block_height, 0)
            .lineTo(block_height, bracket_bottom + self.bracket_wall_thickness)
            .lineTo(0, bracket_top)
            .close()
            .extrude(self.motor_front, both=True)
        )

        bracket_trapezoid_intersect_xy = (
            cq.Workplane("XY")
            .lineTo(0, self.motor_front)
            .lineTo(block_height, self.motor_front)
            .lineTo(block_height, motor_rear)
            .lineTo(self.motor_diameter / 2, bracket_top_right)
            .lineTo(0, bracket_top_right)
            .close()
            .extrude(self.motor_length, both=True)
            .edges("|Z")
            .fillet(self.bracket_wall_thickness)
        )

        return bracket_rectangular.intersect(bracket_wedge_intersect_xz).intersect(
            bracket_trapezoid_intersect_xy
        )


stm = sb_treadmill_motor()

show_object(stm.bolt_placeholders(), options={"color": "gray", "alpha": 0.25})

show_object(stm.motor_placeholder(), options={"color": "gray", "alpha": 0.25})

show_object(stm.cross_rod_placeholder(), options={"color": "gray", "alpha": 0.25})

show_object(stm.bracket(), options={"color": "green", "alpha": 0.5})
show_object(stm.bracket().mirror("XY"), options={"color": "green", "alpha": 0.5})
