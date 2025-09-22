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


class driving_game_stand_accessories:
    def __init__(self):
        self.beam_side = inch_to_mm(1.0)
        self.print_margin = 0.1

    def shifter(self):
        mounting_holes_space = inch_to_mm(1.9)
        thickness = 1.2
        base_width = 100 + 2 * thickness
        base_depth = 100 + thickness
        base_height = mounting_holes_space + self.beam_side

        rotation_degrees = 35
        rotation_back_radians = math.radians(rotation_degrees)
        rotation_front_radians = math.radians(40 - rotation_degrees)

        wall = (
            cq.Workplane("XY")
            .line(0, base_depth / 2 - thickness, forConstruction=True)
            .line(0, thickness)
            .line(base_width / 2 - thickness - self.beam_side - self.print_margin, 0)
            .line(0, -self.beam_side - self.print_margin)
            .line(self.beam_side + self.print_margin * 2, 0)
            .line(0, self.beam_side + self.print_margin)
            .line(thickness - self.print_margin, 0)
            .line(0, -base_depth)
            .line(-thickness, 0)
            .line(0, base_depth - self.beam_side - thickness)
            .line(-self.beam_side - thickness, 0)
            .line(0, self.beam_side)
            .close()
            .extrude(base_height)
        )

        inner_floor = (
            cq.Workplane("YZ")
            .line(base_depth / 2 - self.beam_side, 0, forConstruction=True)
            .line(0, thickness)
            .line(self.beam_side, self.beam_side * math.sin(rotation_front_radians))
            .line(0, -thickness)
            .close()
            .extrude(base_width / 2 - thickness * 2 - self.beam_side)
        )

        outer_floor_length = base_depth - self.beam_side
        outer_floor = (
            cq.Workplane("YZ")
            .line(base_depth / 2 - self.beam_side, 0, forConstruction=True)
            .line(0, thickness)
            .line(
                -outer_floor_length,
                outer_floor_length * math.sin(rotation_back_radians),
            )
            .line(0, -thickness)
            .close()
            .extrude(base_width / 2 - thickness)
        )

        floor_subtract = (
            cq.Workplane("YZ")
            .line(base_depth / 2 - self.beam_side, 0, forConstruction=True)
            .line(
                -outer_floor_length,
                outer_floor_length * math.sin(rotation_back_radians),
            )
            .lineTo(-base_depth / 2, -base_depth)
            .line(base_depth, 0)
            .lineTo(base_depth / 2, self.beam_side * math.sin(rotation_front_radians))
            .close()
            .extrude(base_width / 2)
        )
        wall_subtract = (
            cq.Workplane("YZ")
            .lineTo(
                -base_depth / 2,
                outer_floor_length * math.sin(rotation_back_radians),
                forConstruction=True,
            )
            .line(
                thickness * math.sin(rotation_back_radians),
                thickness * math.cos(rotation_back_radians),
            )
            .lineTo(base_depth / 2 - self.beam_side - thickness, base_height)
            .lineTo(base_depth / 2 - self.beam_side - thickness, base_height * 2)
            .lineTo(-base_depth, base_height * 2)
            .lineTo(-base_depth, base_height)
            .close()
            .extrude(base_width)
        )

        fastener_hole = (
            cq.Workplane("YZ")
            .transformed(
                offset=(base_depth / 2 - self.beam_side / 2, self.beam_side / 2, 0)
            )
            .circle(radius=3 + self.print_margin)
            .extrude(base_width, both=True)
        )

        fastener_holes = fastener_hole + fastener_hole.translate(
            (0, 0, mounting_holes_space)
        )

        return (
            wall
            + inner_floor
            + outer_floor
            - fastener_holes
            - floor_subtract
            - wall_subtract
        )


dgsa = driving_game_stand_accessories()

show_object(dgsa.shifter(), options={"color": "green", "alpha": 0.5})
