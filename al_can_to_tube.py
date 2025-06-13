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
        self.center_line_height = 55
        self.extrusion_beam_clear = 20.2
        self.extrusion_beam_surround = 3
        self.base_width = 70
        self.tt_bracket_width = 22.5

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

    def tt_bracket(self):
        surround = 4
        mid_fastener_offset_length = 20.5
        mid_fastener_offset_width = 17 / 2
        end_fastener_offset_length = 13.5
        end_fastener_offset_height = 7.6
        end_radius = 4
        side_thickness = 1
        end_length_offset = 11.7
        mid_length_offset = 24.6
        fastener_radius_clear = 3.4 / 2

        bracket_outer = (
            cq.Workplane("YZ")
            .line(0, -mid_length_offset)
            .line(self.tt_bracket_width / 2 + surround, 0)
            .line(
                0,
                mid_length_offset + end_length_offset - end_radius,
            )
            .tangentArcPoint(
                endpoint=(
                    -end_radius - surround,
                    end_radius + surround,
                )
            )
            .line(end_radius - self.tt_bracket_width / 2, 0)
            .close()
            .extrude(end_fastener_offset_height + side_thickness)
        )

        bracket_inner = (
            cq.Workplane("YZ")
            .line(0, -mid_length_offset)
            .line(self.tt_bracket_width / 2, 0)
            .line(
                0,
                mid_length_offset + end_length_offset - end_radius,
            )
            .tangentArcPoint(endpoint=(-end_radius, end_radius))
            .line(end_radius - self.tt_bracket_width / 2, 0)
            .close()
            .extrude(end_fastener_offset_height)
            .translate((side_thickness, 0, 0))
        )

        fastener_subtract = (
            cq.Workplane("YZ")
            .circle(radius=fastener_radius_clear)
            .extrude(side_thickness + end_fastener_offset_height)
        )

        output_shaft_subtract = (
            cq.Workplane("YZ").circle(radius=5.7 / 2).extrude(side_thickness)
        )

        bracket_half = (
            bracket_outer
            - bracket_inner
            - fastener_subtract.translate(
                (0, mid_fastener_offset_width, -mid_fastener_offset_length)
            )
            - fastener_subtract.translate((0, 0, end_fastener_offset_length))
            - output_shaft_subtract
        )

        bracket = bracket_half + bracket_half.mirror("XZ")

        return bracket

    def spindle_head(self):
        leg_width_half = 50
        leg_length = 18
        leg_half = (
            cq.Workplane("YZ")
            .lineTo(self.tt_bracket_width / 2, 0)
            .lineTo(
                leg_width_half,
                -self.center_line_height
                - self.extrusion_beam_clear
                - self.extrusion_beam_surround,
            )
            .line(-leg_width_half, 0)
            .close()
            .extrude(leg_length)
        )

        leg_subtract = (
            cq.Workplane("YZ")
            .rect(self.tt_bracket_width, self.tt_bracket_width)
            .extrude(leg_length)
        )

        beam_surround = (
            cq.Workplane("YZ")
            .transformed(
                offset=cq.Vector(
                    0,
                    -self.center_line_height
                    - self.extrusion_beam_surround
                    - self.extrusion_beam_clear / 2,
                )
            )
            .rect(
                self.extrusion_beam_clear + self.extrusion_beam_surround * 2,
                self.extrusion_beam_clear + self.extrusion_beam_surround * 2,
            )
            .rect(self.extrusion_beam_clear, self.extrusion_beam_clear)
            .extrude(leg_length + 15)
        )

        fastener_subtract = (
            cq.Workplane("XZ")
            .transformed(
                offset=cq.Vector(
                    leg_length + 15 / 2,
                    -self.center_line_height
                    - self.extrusion_beam_surround
                    - self.extrusion_beam_clear / 2,
                    self.extrusion_beam_clear / 2,
                )
            )
            .circle(radius=2.5)
            .workplane(offset=self.extrusion_beam_surround)
            .circle(radius=5)
            .loft()
        )

        leg = leg_half + leg_half.mirror("XZ")
        leg = leg.edges("|X").fillet(10)
        leg = leg.faces(">X or <X").shell(3)

        leg = leg - leg_subtract + self.tt_bracket() + beam_surround - fastener_subtract

        return leg

    def bearing_shim(self):
        return (
            cq.Workplane("YZ")
            .circle(radius=8 / 2)
            .circle(radius=0.25 * 25.4 / 2)
            .extrude(7)
        )


o = opener()
show_object(
    o.rim_clip_slot(),
    options={"color": "green", "alpha": 0.5},
)

show_object(
    o.bottom_cone().translate((100, 0, 0)),
    options={"color": "green", "alpha": 0.5},
)

show_object(
    o.bearing_shim().translate((100, 0, 0)),
    options={"color": "blue", "alpha": 0.5},
)

show_object(
    o.spindle_head().translate((-20, 0, 0)),
    options={"color": "blue", "alpha": 0.5},
)
