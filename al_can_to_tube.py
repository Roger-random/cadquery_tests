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


class opener:
    def __init__(self):
        self.inner_lip_radius_outer = 56.4 / 2
        self.inner_lip_radius_inner = 54 / 2
        self.inner_lip_radius_clear = 50 / 2
        self.rim_radius_outer = 59.5 / 2
        self.inner_lip_depth = 6
        self.nozzle_diameter = 0.4

    def inner_lip(self):
        ring = (
            cq.Workplane("XZ")
            .lineTo(0, self.inner_lip_radius_clear, forConstruction=True)
            .lineTo(0, self.inner_lip_radius_outer)
            .lineTo(self.inner_lip_depth, self.inner_lip_radius_inner)
            .line(0, -self.nozzle_diameter)
            .close()
            .revolve(
                angleDegrees=360,
                axisStart=cq.Vector(0, 0, 0),
                axisEnd=cq.Vector(1, 0, 0),
            )
        )

        ring_base = (
            cq.Workplane("YZ")
            .circle(radius=self.rim_radius_outer)
            .circle(radius=self.inner_lip_radius_clear - 3)
            .extrude(-2)
        )
        return ring + ring_base


o = opener()
show_object(
    o.inner_lip(),
    options={"color": "green", "alpha": 0.5},
)
