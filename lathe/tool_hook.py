"""
MIT License

Copyright (c) 2024 Roger Cheng

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

    def show_object(*args):
        pass


mm_per_inch = 25.4
nozzle_diameter = 0.4


class tool_hook:
    """
    3D printed hook to hold a tool over the edge of the work table for a
    Logan 555 lathe
    """

    def __init__(self):
        self.inside_slope_degrees = 25
        self.inside_slope_radians = math.radians(self.inside_slope_degrees)
        self.hook_thickness = nozzle_diameter * 6
        self.tray_lip_radius_inner = (1 / 4) * mm_per_inch
        self.tray_lip_radius_outer = self.tray_lip_radius_inner + self.hook_thickness
        self.hook_height_outside = 30
        self.hook_height_inside = 30
        pass

    def hook(self):
        hook_top = (
            cq.Workplane("XZ")
            .line(self.tray_lip_radius_inner, 0, forConstruction=True)
            .line(self.hook_thickness, 0)
            .line(0, self.tray_lip_radius_outer)
            .line(-self.tray_lip_radius_outer, 0)
            .radiusArc(
                (
                    -self.tray_lip_radius_outer * math.cos(self.inside_slope_radians),
                    self.tray_lip_radius_outer * math.sin(self.inside_slope_radians),
                ),
                -self.tray_lip_radius_outer,
            )
            .lineTo(
                -self.tray_lip_radius_inner * math.cos(self.inside_slope_radians),
                self.tray_lip_radius_inner * math.sin(self.inside_slope_radians),
            )
            .radiusArc(
                (self.tray_lip_radius_inner, 0),
                self.tray_lip_radius_inner,
            )
            .close()
            .extrude(20)
        )

        hook_inner = (
            cq.Workplane("XZ")
            .transformed(rotate=cq.Vector(0, 0, -self.inside_slope_degrees))
            .line(-self.tray_lip_radius_inner, 0)
            .line(0, -self.hook_height_inside)
            .tangentArcPoint((-self.hook_thickness, 0))
            .line(0, self.hook_height_inside)
            .close()
            .extrude(20)
        )

        hook_outer = (
            cq.Workplane("XZ")
            .line(self.tray_lip_radius_inner, 0)
            .line(0, -self.hook_height_outside)
            .tangentArcPoint((self.hook_thickness, 0))
            .line(0, self.hook_height_outside)
            .close()
            .extrude(20)
        )

        return hook_top + hook_inner + hook_outer


th = tool_hook()
show_object(th.hook(), options={"color": "white", "alpha": 0.5})
