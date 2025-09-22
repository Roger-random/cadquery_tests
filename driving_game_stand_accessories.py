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

    def beam_transform(self, beam, width, thickness):
        beam_rotate = 10
        return (
            beam.translate((0, 0, thickness))
            .rotate(
                (0, self.beam_side + thickness * 2, thickness),
                (1, self.beam_side + thickness * 2, thickness),
                beam_rotate,
            )
            .translate(
                (
                    width / 2 - self.beam_side / 2 - thickness,
                    0,
                    0,
                )
            )
        )

    def shifter(self):
        mounting_holes_space = inch_to_mm(1.9)
        thickness = 4
        base_width = 60
        base_depth = 80

        beam_bracket_outer = cq.Workplane("XY").box(
            self.beam_side + thickness * 2,
            self.beam_side + thickness * 2,
            mounting_holes_space + self.beam_side,
            centered=(True, True, False),
        )

        beam_channel = self.beam_transform(
            (
                cq.Workplane("XY")
                .box(
                    self.beam_side + self.print_margin,
                    self.beam_side + self.print_margin + thickness,
                    mounting_holes_space * 6,
                    centered=(True, True, True),
                )
                .translate((0, thickness, 0))
            ),
            base_width,
            thickness,
        )

        fastener_hole = (
            cq.Workplane("YZ")
            .transformed(offset=(0, self.beam_side / 2, 0))
            .circle(radius=3 + self.print_margin)
            .extrude(self.beam_side, both=True)
        )

        beam_bracket = self.beam_transform(
            (
                beam_bracket_outer
                - fastener_hole
                - fastener_hole.translate((0, 0, mounting_holes_space))
            ),
            base_width,
            thickness,
        )

        shifter_base = cq.Workplane("XY").box(
            base_width, base_depth, thickness, centered=(True, True, False)
        )

        bracket_trim = (
            cq.Workplane("XY")
            .box(
                base_width + self.print_margin,
                base_depth + self.print_margin,
                self.beam_side,
            )
            .translate((0, 0, -self.beam_side / 2))
        )

        bracket_edge_y = base_depth / 2 - self.beam_side / 2 - thickness
        shifter_mount = (
            shifter_base
            + beam_bracket.translate((0, bracket_edge_y, 0))
            - beam_channel.translate((0, bracket_edge_y, 0))
            - bracket_trim
        )

        return shifter_mount


dgsa = driving_game_stand_accessories()

show_object(dgsa.shifter(), options={"color": "green", "alpha": 0.5})
