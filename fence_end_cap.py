"""
MIT License

Copyright (c) 2026 Roger Cheng

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


class fence_end_cap:
    def __init__(self):
        self.end_box_edge_full = 25.3
        self.end_box_edge_beveled = 22
        self.end_box_bevel_height = 4
        self.end_box_fillet = 1
        self.end_box_inner_chamfer = 0.5
        self.internal_side_long = 14.4
        self.internal_side_short = 7
        self.internal_setback = 0.5
        self.internal_length = 7
        self.internal_bevel = 2
        self.internal_thickness = 0.8
        self.internal_x_width = self.internal_side_long * 2 * math.sqrt(2)
        self.internal_x_depth = 10
        pass

    def outside_cap(self):
        return (
            (
                cq.Workplane("XZ")
                .rect(self.end_box_edge_full, self.end_box_edge_full)
                .workplane(self.end_box_bevel_height)
                .rect(self.end_box_edge_beveled, self.end_box_edge_beveled)
                .loft()
                .edges("not <Y or >Y")
                .fillet(self.end_box_fillet)
            )
            .faces(">Y")
            .chamfer(self.end_box_inner_chamfer)
        )

    def inside_square(self):
        return (
            cq.Workplane("XZ")
            .rect(
                self.internal_side_long - self.internal_setback,
                self.internal_side_long - self.internal_setback,
            )
            .workplane(-self.internal_length)
            .rect(self.internal_side_long, self.internal_side_long)
            .loft()
            .faces(">Y")
            .rect(self.internal_side_long, self.internal_side_long)
            .workplane(self.internal_bevel)
            .rect(
                self.internal_side_long - self.internal_bevel,
                self.internal_side_long - self.internal_bevel,
            )
            .loft()
        )

    def inside_x(self):
        x_half = (
            cq.Workplane("XY")
            .transformed(rotate=(0, 45, 0))
            .rect(self.internal_x_width, self.internal_x_depth, centered=(True, False))
            .extrude(self.internal_thickness, both=True)
        )

        inside = (x_half + x_half.mirror("YZ")).intersect(self.inside_square())

        return inside

    def cap_square(self):
        return self.outside_cap() + self.inside_x()


fec = fence_end_cap()

show_object(fec.cap_square(), options={"color": "green", "alpha": 0.5})
