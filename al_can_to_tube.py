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
        self.rim_radius_outer = 59.35 / 2
        self.rim_height = 2.73
        self.can_radius_outer = 57.8 / 2
        self.nozzle_diameter = 0.4
        self.claw_size = 1
        self.wedge_width = 3
        self.top_lip_slope = self.rim_radius_outer - self.can_radius_outer

    def rim_clip(self):
        revolve = (
            cq.Workplane("XZ")
            .lineTo(0, self.rim_radius_outer - 3, forConstruction=True)
            .lineTo(0, self.rim_radius_outer)
            .lineTo(self.rim_height, self.rim_radius_outer)
            .lineTo(self.rim_height + self.top_lip_slope, self.can_radius_outer)
            .lineTo(
                self.rim_height + self.claw_size + self.top_lip_slope,
                self.can_radius_outer,
            )
            .lineTo(
                self.rim_height + self.claw_size + self.wedge_width,
                self.can_radius_outer + self.wedge_width,
            )
            .lineTo(
                self.rim_height + self.claw_size + self.wedge_width,
                self.can_radius_outer + self.wedge_width + self.claw_size,
            )
            .lineTo(
                -self.wedge_width,
                self.can_radius_outer + self.wedge_width + self.claw_size,
            )
            .lineTo(-self.wedge_width, self.rim_radius_outer - 3)
            .close()
            .revolve(
                angleDegrees=360,
                axisStart=cq.Vector(0, 0, 0),
                axisEnd=cq.Vector(1, 0, 0),
            )
        )

        return revolve

    def rim_clip_slot(self):
        rim_clip = self.rim_clip()

        slot = (
            cq.Workplane("XZ")
            .line(-self.rim_radius_outer, 0)
            .line(0, self.rim_radius_outer * 2)
            .line(self.rim_radius_outer * 2, 0)
            .line(0, -self.rim_radius_outer * 2)
            .close()
            .extrude(0.1)
        )

        return rim_clip - slot


o = opener()
show_object(
    o.rim_clip_slot(),
    options={"color": "green", "alpha": 0.5},
)
