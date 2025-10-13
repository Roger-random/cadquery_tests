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
        self.bolt_hole_diameter = inch_to_mm(0.332) + self.print_margin
        self.bolt_hole_thickness = 10
        self.bolt_hole_surround_size = 20
        self.bolt_washer_diameter = inch_to_mm(0.9) + self.print_margin
        self.bolt_hole_placeholder_length = 150

        # Dimensions of the motor metal body. Actual length is longer due to:
        # Front: flange and combination flywheel+fan+output pulley on shaft
        # Back: plasatic bell housing where all the wires come in
        self.motor_diameter = 85
        self.motor_length = 135
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
        self.cross_rod_head_diameter = self.motor_fastener_head_diameter
        self.cross_rod_brace_height = self.motor_fastener_head_diameter

        # To align with existing pulley, the front of motor body should
        # be about this far away from the left most set of bolts
        self.motor_position = inch_to_mm(3)

        # Machined motor mount surface is a little bit above casting center
        # surface. Take advantage of it by sinking motor into that gap.
        self.motor_height_offset = -inch_to_mm(0.150)

        # Calculated values shared by multiple methods.
        self.motor_front = -self.bolt_spacing_lr / 2 - self.motor_position
        self.motor_rear = self.motor_front + self.motor_length
        self.bracket_top = self.bolt_spacing_fb / 2 + self.bolt_hole_surround_size
        self.bracket_top_left = -self.bolt_spacing_lr / 2 - self.bolt_hole_surround_size
        self.bracket_top_right = -self.bracket_top_left
        self.bracket_bottom = (
            self.motor_diameter / 2
            + self.motor_fastener_wall_thickness
            - self.bracket_wall_thickness
        )
        self.block_height = (
            self.motor_diameter + self.motor_height_offset + self.cross_rod_brace_height
        )

    def bolt_placeholders(self):
        stem = (
            cq.Workplane("YZ")
            .rect(
                xLen=self.bolt_spacing_lr,
                yLen=self.bolt_spacing_fb,
                forConstruction=True,
            )
            .vertices()
            .circle(radius=self.bolt_hole_diameter / 2)
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
            .circle(radius=self.bolt_washer_diameter / 2)
            .extrude(self.bolt_hole_placeholder_length)
        )

        return stem + head

    def motor_placeholder(self):
        # 90 for bracket V1
        # 180 for bracket V3
        motor_rotation = 180
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
            .transformed(rotate=(motor_rotation, 0, 0))
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
            .circle(radius=self.cross_rod_head_diameter / 2)
            .extrude(self.cross_rod_head_length)
        )
        return rod + rod.translate(
            (0, self.motor_length - self.cross_rod_brace_height, 0)
        )

    def bracket_v1(self):
        bracket_block = (
            cq.Workplane("YZ")
            .lineTo(self.motor_front, self.bracket_bottom, forConstruction=True)
            .line(0, self.bracket_wall_thickness)
            .lineTo(self.bracket_top_left, self.bracket_top)
            .lineTo(self.bracket_top_right, self.bracket_top)
            .line(0, -self.bolt_hole_surround_size * 2)
            .lineTo(self.motor_rear, self.bracket_bottom)
            .close()
            .extrude(self.block_height)
        )

        bracket_rectangular = (
            bracket_block.edges("|Z").fillet(self.bracket_wall_thickness)
            - self.motor_placeholder()
            - self.motor_fastener().translate((0, self.motor_mount_1, 0))
            - self.motor_fastener().translate((0, self.motor_mount_2, 0))
            - self.cross_rod_placeholder()
            - self.bolt_placeholders()
        )

        return bracket_rectangular.intersect(
            self.bracket_wedge_intersect_xz()
        ).intersect(self.bracket_trapezoid_intersect_xy())

    def motor_fastener(self):
        return (
            cq.Workplane("XY")
            .transformed(
                offset=(
                    self.motor_diameter / 2 + self.motor_height_offset,
                    self.motor_front,
                    self.bracket_bottom,
                )
            )
            .circle(radius=self.motor_fastener_hole_diameter / 2)
            .extrude(self.bracket_wall_thickness - self.counterbore_bridge_thickness)
            .faces(">Z")
            .workplane(offset=self.counterbore_bridge_thickness)
            .circle(radius=self.motor_fastener_head_diameter / 2)
            .extrude(self.bracket_top)
        )

    def motor_fastener_yz(self):
        fastener_xy = self.motor_fastener()

        return fastener_xy.rotate(
            (
                self.motor_diameter / 2 + self.motor_height_offset,
                self.motor_front,
                0,
            ),
            (
                self.motor_diameter / 2 + self.motor_height_offset,
                0,
                0,
            ),
            90,
        )

    def bracket_wedge_intersect_xz(self):
        return (
            cq.Workplane("XZ")
            .lineTo(self.block_height, 0)
            .lineTo(
                self.block_height, self.bracket_bottom + self.bracket_wall_thickness
            )
            .lineTo(0, self.bracket_top)
            .close()
            .extrude(self.motor_front, both=True)
        )

    def bracket_trapezoid_intersect_xy(self):
        return (
            cq.Workplane("XY")
            .lineTo(0, self.motor_front)
            .lineTo(self.block_height, self.motor_front)
            .lineTo(self.block_height, self.motor_rear)
            .lineTo(self.motor_diameter / 2, self.bracket_top_right)
            .lineTo(0, self.bracket_top_right)
            .close()
            .extrude(self.motor_length, both=True)
            .edges("|Z")
            .fillet(self.bracket_wall_thickness)
        )

    def bracket_v2(self):
        """
        Minimal L that's just big enough for bolts. Helps visualize what it
        looks like when I rebuild with commodity metal L sections.
        """
        bolt_y = self.bolt_spacing_fb / 2
        minimal_bottom = (
            bolt_y - self.bolt_washer_diameter / 2 - self.bracket_wall_thickness
        )
        minimal_top = bolt_y + self.bolt_washer_diameter / 2
        minimal_block = (
            cq.Workplane("YZ")
            .lineTo(self.motor_front, minimal_bottom, forConstruction=True)
            .line(0, self.cross_rod_wall_thickness)
            .lineTo(self.bracket_top_left, minimal_top)
            .lineTo(self.bracket_top_right, minimal_top)
            .lineTo(self.bracket_top_right, minimal_bottom)
            .lineTo(self.motor_rear, minimal_bottom)
            .close()
            .extrude(self.block_height)
        )

        minimal_intersect_xz = (
            cq.Workplane("XZ")
            .lineTo(self.block_height, 0)
            .line(0, minimal_bottom + self.bracket_wall_thickness)
            .line(-self.block_height + self.bracket_wall_thickness, 0)
            .line(0, self.bolt_washer_diameter)
            .line(-self.bracket_wall_thickness, 0)
            .close()
            .extrude(self.motor_front, both=True)
        )

        return (
            minimal_block.intersect(minimal_intersect_xz).intersect(
                self.bracket_trapezoid_intersect_xy()
            )
            - self.motor_fastener().translate(
                (0, self.motor_mount_1, minimal_bottom - self.motor_diameter / 2)
            )
            - self.motor_fastener().translate(
                (0, self.motor_mount_2, minimal_bottom - self.motor_diameter / 2)
            )
            - self.cross_rod_placeholder().translate(
                (0, 0, minimal_bottom - self.motor_diameter / 2)
            )
            - self.bolt_placeholders()
        )

    def bracket_v3(self, spacer_thickness):
        """
        L shape geometry has been tricky to get right. Try to simplify with a
        blocky rectangular design that will be easier to print and build.
        My first instinct is that it isn't as strong but perhaps it'll be
        strong enough in plastic. Pretty confident it will be strong enough in
        aluminum.
        """
        cross_rod_height = (
            self.motor_diameter
            + self.motor_height_offset
            + self.cross_rod_hole_diameter / 2
        )
        bracket_height = cross_rod_height + self.cross_rod_head_diameter / 2
        motor_mount_front = self.motor_front + self.motor_mount_1
        cross_rod_front = self.motor_front + self.cross_rod_head_diameter / 2
        cross_rod_motor_mount_offset = motor_mount_front - cross_rod_front
        cross_rod_rear = (
            self.motor_front + self.motor_mount_2 + cross_rod_motor_mount_offset
        )

        subtract_length = self.bolt_spacing_fb / 2 + self.bolt_washer_diameter / 2

        bracket_body_rear = cross_rod_rear + self.cross_rod_head_diameter / 2
        bracket_body = (
            cq.Workplane("XY")
            .transformed(offset=(0, 0, self.bolt_spacing_fb / 2))
            .line(0, self.motor_front, forConstruction=True)
            .line(bracket_height, 0)
            .lineTo(bracket_height, bracket_body_rear)
            .line(-bracket_height, 0)
            .close()
            .extrude(self.bolt_washer_diameter / 2, both=True)
            .edges("|Z")
            .fillet(self.cross_rod_head_diameter / 2)  # Help 3D print adhesion
        )

        bracket_tang_tail = inch_to_mm(0.6) + self.bolt_hole_diameter / 2

        bracket_tang_subtract = (
            cq.Workplane("XY")
            .transformed(
                offset=(0, 0, self.bolt_spacing_fb / 2 - self.bolt_washer_diameter / 2)
            )
            .lineTo(
                self.bracket_wall_thickness, bracket_body_rear, forConstruction=True
            )
            .line(bracket_height, 0)
            .line(0, self.bolt_spacing_lr)
            .line(-bracket_height, 0)
            .close()
            .extrude(self.bolt_washer_diameter)
            .edges("|Z and <Y and <X")
            .fillet(bracket_height / 2)
            .faces(">Z")
            .edges("not >X")
            .fillet(self.cross_rod_head_diameter / 2)
        )

        bracket_wall = (
            cq.Workplane("XY")
            .transformed(
                offset=(0, 0, self.bolt_spacing_fb / 2 - self.bolt_washer_diameter / 2)
            )
            .lineTo(0, self.motor_front)
            .line(bracket_height, 0)
            .lineTo(bracket_height, bracket_body_rear)
            .lineTo(
                self.bracket_wall_thickness,
                self.bolt_spacing_lr / 2 + bracket_tang_tail,
            )
            .line(-self.bracket_wall_thickness, 0)
            .close()
            .extrude(self.bracket_wall_thickness + self.bolt_washer_diameter)
            .edges("|Z and >Y")
            .fillet(self.bracket_wall_thickness / 4)
            .edges("|Z")
            .fillet(self.cross_rod_head_diameter / 2)
        )

        bracket_tang_bolt_subtract = (
            cq.Workplane("YZ")
            .transformed(
                offset=(
                    self.bolt_spacing_lr / 2,
                    self.bolt_spacing_fb / 2,
                    self.bracket_wall_thickness,
                )
            )
            .circle(radius=self.bolt_washer_diameter / 2)
            .extrude(bracket_height)
            .faces("<X")
            .workplane()
            .circle(radius=self.bolt_hole_diameter / 2)
            .extrude(self.bracket_wall_thickness)
        )

        cross_thread_holes = (
            cq.Workplane("XY")
            .lineTo(cross_rod_height, cross_rod_front, forConstruction=True)
            .lineTo(cross_rod_height, cross_rod_rear)
            .vertices()
            .circle(radius=self.cross_rod_hole_diameter / 2)
            .extrude(subtract_length * 2, both=True)
        )

        bolt_y = -(self.bolt_spacing_lr / 2)
        clearance_hole_width = self.bolt_washer_diameter
        clearance_hole_height = inch_to_mm(1.5) + self.print_margin
        bolt_clearance = (
            cq.Workplane("XY")
            .lineTo(
                self.bracket_wall_thickness,
                bolt_y + clearance_hole_width / 2,
                forConstruction=True,
            )
            .line(0, -clearance_hole_width)
            .line(clearance_hole_height, 0)
            .line(0, clearance_hole_width)
            .close()
            .extrude(subtract_length)
            .edges("not <X")
            .fillet(self.cross_rod_head_diameter / 2)
        )

        bolt_hole = (
            cq.Workplane("YZ")
            .transformed(offset=(bolt_y, self.bolt_spacing_fb / 2, 0))
            .circle(radius=self.bolt_hole_diameter / 2)
            .extrude(subtract_length * 2)
        )

        bracket = (
            bracket_wall
            - bracket_tang_subtract
            - bracket_tang_bolt_subtract
            - cross_thread_holes
            - bolt_clearance
            - bolt_hole
        )

        motor_subtract = (
            cq.Workplane("XZ")
            .transformed(
                offset=(
                    self.motor_diameter / 2 + self.motor_height_offset,
                    0,
                    -self.motor_front,
                )
            )
            .circle(radius=self.motor_diameter / 2)
            .extrude(self.motor_front)
        )

        top_center_y = (bracket_body_rear + self.motor_front) / 2
        top_dimension_y = bracket_body_rear - self.motor_front
        top_dimension_z = self.motor_diameter - self.cross_rod_head_diameter
        top_thickness = self.cross_rod_head_diameter

        top_block = (
            cq.Workplane("YZ")
            .transformed(offset=(top_center_y, 0, bracket_height))
            .rect(top_dimension_y, top_dimension_z)
            .extrude(-top_thickness)
        )

        top = (
            top_block
            - stm.motor_fastener_yz().translate((0, stm.motor_mount_1, 0))
            - stm.motor_fastener_yz().translate((0, stm.motor_mount_2, 0))
            - cross_thread_holes
            - motor_subtract
        )

        spacer_top_lip_depth = 5
        spacer_top_lip_height = 10
        spacer = (
            cq.Workplane("XZ")
            .transformed(offset=((bracket_height, top_dimension_z / 2, -top_center_y)))
            .line(spacer_top_lip_height / 2, -spacer_top_lip_depth)
            .line(spacer_top_lip_height / 2, 0)
            .line(0, spacer_top_lip_depth * 2 + spacer_thickness)
            .line(-spacer_top_lip_height / 2, 0)
            .line(-spacer_top_lip_height / 2, -spacer_top_lip_depth)
            .line(-self.motor_diameter / 2 - top_thickness, 0)
            .line(0, -spacer_thickness)
            .close()
            .extrude(
                top_dimension_y / 2 - self.cross_rod_head_diameter * 1.5, both=True
            )
        )
        spacer = (spacer - motor_subtract).faces("<X").chamfer(1)
        return (bracket, top, spacer)


stm = sb_treadmill_motor()

show_object(stm.bolt_placeholders(), options={"color": "gray", "alpha": 0.25})

show_object(stm.motor_placeholder(), options={"color": "gray", "alpha": 0.25})

show_object(stm.cross_rod_placeholder(), options={"color": "gray", "alpha": 0.25})

# show_object(stm.bracket_v1(), options={"color": "green", "alpha": 0.5})
# show_object(stm.bracket_v1().mirror("XY"), options={"color": "green", "alpha": 0.5})

# show_object(stm.bracket_v2(), options={"color": "yellow", "alpha": 0.5})

(v3_side, v3_top, v3_spacer_top) = stm.bracket_v3(inch_to_mm(0.515))

show_object(v3_side, options={"color": "blue", "alpha": 0.25})
show_object(v3_side.mirror("XY"), options={"color": "blue", "alpha": 0.25})
show_object(v3_top, options={"color": "blue", "alpha": 0.25})
show_object(v3_spacer_top, options={"color": "blue", "alpha": 0.25})
