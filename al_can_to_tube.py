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
        self.rim_tip_lip = 3
        self.can_radius_outer = 57.8 / 2
        self.nozzle_diameter = 0.4
        self.claw_size = 1
        self.wedge_width = 3
        self.rim_length_rear = 15
        self.binder_clip_tab_size = 4
        self.binder_clip_tab_thickness = 4
        self.tt_hub_radius = 10
        self.tt_hub_thickness = 7
        self.tt_shaft_diameter = 5.6
        self.tt_shaft_thickness = 3.8
        self.bottom_cone_radius_small = 42.3 / 2
        self.bottom_cone_radius_large = 44 / 2
        self.bottom_cone_height = 3
        self.bottom_cone_bearing_radius = 22.2 / 2
        self.bottom_cone_bearing_height = 7
        self.bottom_cone_bearing_lip = 0.5
        self.top_lip_slope = self.rim_radius_outer - self.can_radius_outer

    def rim_clip(self):
        revolve = (
            cq.Workplane("XZ")
            .lineTo(0, self.rim_radius_outer - self.rim_tip_lip, forConstruction=True)
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
            .line(
                -self.rim_length_rear,
                0,
            )
            .line(0, -self.claw_size - self.wedge_width - self.rim_tip_lip)
            .close()
            .revolve(
                angleDegrees=360,
                axisStart=cq.Vector(0, 0, 0),
                axisEnd=cq.Vector(1, 0, 0),
            )
            .translate(
                cq.Vector(
                    self.rim_length_rear
                    - self.rim_height
                    - self.claw_size
                    - self.wedge_width,
                    0,
                    0,
                )
            )
        )

        return revolve

    def binder_clip_tab_half(self):
        tab_half = (
            cq.Workplane("YZ")
            .lineTo(
                0,
                self.can_radius_outer + self.wedge_width + self.claw_size,
                forConstruction=True,
            )
            .line(0, -self.binder_clip_tab_thickness)
            .line(self.binder_clip_tab_size / 4, self.binder_clip_tab_size)
            .line(
                self.binder_clip_tab_thickness / 8, self.binder_clip_tab_thickness / 2
            )
            .line(
                -self.binder_clip_tab_thickness / 8, self.binder_clip_tab_thickness / 2
            )
            .close()
            .extrude(self.rim_length_rear)
        )
        return tab_half

    def tt_mount_hub(self):
        hub = (
            cq.Workplane("YZ")
            .circle(radius=self.tt_hub_radius)
            .extrude(self.tt_hub_thickness)
        )
        arm = (
            cq.Workplane("YZ")
            .rect(
                xLen=self.tt_hub_radius * 2,
                yLen=-self.rim_radius_outer,
                centered=(True, False),
            )
            .extrude(self.tt_hub_thickness)
        )

        motor_shaft_subtract = (
            cq.Workplane("YZ")
            .circle(radius=self.tt_shaft_diameter / 2)
            .extrude(self.tt_hub_thickness)
        ).intersect(
            cq.Workplane("YZ")
            .rect(xLen=self.tt_shaft_thickness, yLen=self.tt_shaft_diameter)
            .extrude(self.tt_hub_thickness)
        )
        return (hub + arm - motor_shaft_subtract).faces("<X").chamfer(1)

    def rim_clip_slot(self):
        rim_clip = self.rim_clip()

        slot = (
            cq.Workplane("XZ")
            .line(-self.rim_radius_outer, 0)
            .line(0, self.rim_radius_outer * 2)
            .line(self.rim_radius_outer * 2, 0)
            .line(0, -self.rim_radius_outer * 2)
            .close()
            .extrude(0.1, both=True)
        )

        binder_tab_half = self.binder_clip_tab_half()
        binder_tab = binder_tab_half + binder_tab_half.mirror("XZ")

        return rim_clip + binder_tab - slot + self.tt_mount_hub()

    def bottom_cone(self):
        cone = (
            cq.Workplane("YZ")
            .circle(radius=self.bottom_cone_radius_small)
            .workplane(offset=self.bottom_cone_height)
            .circle(radius=self.bottom_cone_radius_large)
            .loft()
            .faces(">X")
            .workplane()
            .circle(radius=self.bottom_cone_radius_large)
            .extrude(
                self.bottom_cone_bearing_height
                + self.bottom_cone_bearing_lip
                - self.bottom_cone_height
            )
        )

        bearing_subtract = (
            cq.Workplane("YZ")
            .circle(
                radius=self.bottom_cone_bearing_radius - self.bottom_cone_bearing_lip
            )
            .extrude(self.bottom_cone_bearing_lip)
            .faces(">X")
            .workplane()
            .circle(radius=self.bottom_cone_bearing_radius)
            .extrude(self.bottom_cone_bearing_height)
        )
        return (cone - bearing_subtract).faces(">X").chamfer(1)


o = opener()
show_object(
    o.rim_clip_slot(),
    options={"color": "green", "alpha": 0.5},
)

show_object(
    o.bottom_cone().translate((100, 0, 0)),
    options={"color": "green", "alpha": 0.5},
)
