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


class tippe_top_jigs:
    def __init__(
        self,
        tippe_radius=inch_to_mm(0.5),
    ):
        self.tippe_radius = tippe_radius
        self.quarter_sphere_groove_radius = (
            math.sin(math.radians(45)) * self.tippe_radius
        )
        # End of the tippe top volume, this is where part off tool should cut
        self.tippe_body_top = -self.tippe_radius - self.quarter_sphere_groove_radius

        # Representing part off tool in visualization
        self.part_off_tool_end = self.tippe_body_top - inch_to_mm(0.1)
        self.partoff_placeholder_radius = inch_to_mm(0.325)

        # Groove for bar puller to grip
        self.grip_groove = inch_to_mm(0.1)

        # Lathe tool post is designed for cutters of this shank size
        self.tool_height = inch_to_mm(0.75)

        pass

    def tippe_body_round_exterior_lathe(self):
        """
        Visualizing the entire cross section of a Tippe Top body as it would sit
        on a CNC collet cut from bar stock.
        """
        return (
            cq.Workplane("ZX")
            .radiusArc(
                endPoint=(self.tippe_radius, -self.tippe_radius),
                radius=self.tippe_radius,
            )
            .radiusArc(
                endPoint=(
                    self.quarter_sphere_groove_radius,
                    -self.tippe_radius - self.quarter_sphere_groove_radius,
                ),
                radius=self.tippe_radius,
            )
            .lineTo(self.tippe_radius, -self.tippe_radius * 2)
            .line(-self.grip_groove, -self.grip_groove)
            .line(self.grip_groove, -self.grip_groove)
            .lineTo(self.tippe_radius, -self.tippe_radius * 3)
            .radiusArc(endPoint=(0, -self.tippe_radius * 2), radius=-self.tippe_radius)
            .lineTo(0, self.part_off_tool_end)
            .lineTo(self.partoff_placeholder_radius, self.part_off_tool_end)
            .lineTo(self.partoff_placeholder_radius, self.tippe_body_top)
            .lineTo(0, self.tippe_body_top)
            .close()
            .revolve(angleDegrees=360, axisStart=(0, 0, 0), axisEnd=(0, 1, 0))
        )

    def bar_puller_interface_profile(
        self,
        bar_puller_gap=0.5,  # Extra claw clearance
    ):
        """
        Profile used several times to generate bar puller
        """
        return (
            cq.Workplane("XZ")
            .lineTo(0, self.tippe_radius + bar_puller_gap)
            .lineTo(-self.tippe_radius * 2, self.tippe_radius + bar_puller_gap)
            .line(
                -self.grip_groove - bar_puller_gap,
                -self.grip_groove - bar_puller_gap,
            )
            .lineTo(-self.tippe_radius * 2 - self.grip_groove - bar_puller_gap, 0)
            .close()
        )

    def bar_puller(
        self,
        bar_puller_length=inch_to_mm(1),  # Shank length
        bar_puller_centerline_dist=inch_to_mm(1.0),  # Shank to centerline distance
        bar_puller_claw_margin=inch_to_mm(0.15),  # Claw material top and bottom
        bar_puller_claw=inch_to_mm(0.25),  # Claw thickness
    ):
        """
        A claw to be mounted on tool post for hooking onto the grip groove
        and pull out bar in preparation for next run.
        """

        subtract_cylindrical = self.bar_puller_interface_profile().revolve(
            angleDegrees=180, axisStart=(0, 0, 0), axisEnd=(1, 0, 0)
        )
        subtract_rectangular_half = self.bar_puller_interface_profile().extrude(
            -self.tippe_radius
        )

        subtract = (
            subtract_cylindrical
            + subtract_rectangular_half
            + subtract_rectangular_half.mirror("XY")
        )

        puller_min = -self.tippe_radius * 2 - self.grip_groove
        body = (
            # Shank
            cq.Workplane("XZ")
            .transformed(offset=(0, 0, bar_puller_centerline_dist))
            .lineTo(puller_min, 0, forConstruction=True)
            .line(bar_puller_length, 0)
            .line(0, -self.tool_height)
            .line(-bar_puller_length, 0)
            .close()
            .extrude(self.tool_height)
            # Prism connecting shank to claw
            .faces(">Y")
            .workplane()
            .lineTo(-puller_min, 0, forConstruction=True)
            .line(-bar_puller_length, 0)
            .line(0, -self.tool_height)
            .line(bar_puller_length, 0)
            .close()
            .workplane(offset=bar_puller_centerline_dist - self.tippe_radius)
            .lineTo(
                -puller_min,
                self.tippe_radius + bar_puller_claw_margin,
                forConstruction=True,
            )
            .line(-bar_puller_length / 2, 0)
            .line(0, -self.tippe_radius * 2 - bar_puller_claw_margin * 2)
            .line(bar_puller_length / 2, 0)
            .close()
            .loft()
            # Claw exterior
            .faces(">Y")
            .workplane()
            .lineTo(
                -puller_min,
                self.tippe_radius + bar_puller_claw_margin,
                forConstruction=True,
            )
            .line(-bar_puller_length / 2, 0)
            .line(0, -self.tippe_radius * 2 - bar_puller_claw_margin * 2)
            .line(bar_puller_length / 2, 0)
            .close()
            .workplane(offset=self.tippe_radius + bar_puller_claw_margin)
            .lineTo(
                -puller_min,
                self.tippe_radius + bar_puller_claw_margin,
                forConstruction=True,
            )
            .line(-bar_puller_claw, 0)
            .line(0, -self.tippe_radius * 2 - bar_puller_claw_margin * 2)
            .line(bar_puller_claw, 0)
            .close()
            .loft()
        )

        return (body - subtract).edges("|X").fillet(1.5)

    def catcher(
        self,
        catch_width=inch_to_mm(0.5),
        mouth_gap_radius=inch_to_mm(0.2),
        body_extra_radius=inch_to_mm(0.15),
        body_length=inch_to_mm(1.5),
        funnel_drop=inch_to_mm(0.2),
        wall_thickness=1.6,
        tiny_extra=1,
        shank_width=inch_to_mm(2.5),
    ):
        mouth_interior_radius = self.tippe_radius + mouth_gap_radius
        body_interior_radius = mouth_interior_radius + body_extra_radius

        mouth_exterior_radius = mouth_interior_radius + wall_thickness
        body_exterior_radius = body_interior_radius + wall_thickness

        mild_drop = funnel_drop * 0.35

        catcher_interior_subtract = (
            cq.Workplane("YZ")
            # Mouth opening to workpiece
            .transformed(
                offset=(
                    0,
                    0,
                    -self.tippe_radius - mouth_gap_radius - tiny_extra,
                )
            )
            .lineTo(0, mouth_interior_radius - tiny_extra, forConstruction=True)
            .radiusArc(
                endPoint=(0, -mouth_interior_radius + tiny_extra),
                radius=mouth_interior_radius - tiny_extra,
            )
            .line(-catch_width, 0)
            .radiusArc(
                endPoint=(-catch_width, mouth_interior_radius - tiny_extra),
                radius=mouth_interior_radius - tiny_extra,
            )
            .close()
            .workplane(offset=body_extra_radius + tiny_extra)
            .lineTo(0, body_interior_radius, forConstruction=True)
            .radiusArc(endPoint=(0, -body_interior_radius), radius=body_interior_radius)
            .line(-catch_width, 0)
            .radiusArc(
                endPoint=(-catch_width, body_interior_radius),
                radius=body_interior_radius,
            )
            .close()
            .loft()
            # Mild drop
            .faces(">X")
            .workplane()
            .lineTo(0, body_interior_radius, forConstruction=True)
            .radiusArc(endPoint=(0, -body_interior_radius), radius=body_interior_radius)
            .line(-catch_width, 0)
            .radiusArc(
                endPoint=(-catch_width, body_interior_radius),
                radius=body_interior_radius,
            )
            .close()
            .workplane(offset=self.tippe_radius)
            .lineTo(0, body_interior_radius - mild_drop, forConstruction=True)
            .radiusArc(
                endPoint=(0, -body_interior_radius - mild_drop),
                radius=body_interior_radius,
            )
            .line(-catch_width, 0)
            .radiusArc(
                endPoint=(-catch_width, body_interior_radius - mild_drop),
                radius=body_interior_radius,
            )
            .close()
            .loft()
            # Funnel down
            .faces(">X")
            .workplane()
            .lineTo(0, body_interior_radius - mild_drop, forConstruction=True)
            .radiusArc(
                endPoint=(0, -body_interior_radius - mild_drop),
                radius=body_interior_radius,
            )
            .line(-catch_width, 0)
            .radiusArc(
                endPoint=(-catch_width, body_interior_radius - mild_drop),
                radius=body_interior_radius,
            )
            .close()
            .workplane(offset=body_length - self.tippe_radius)
            .lineTo(
                body_extra_radius,
                -body_interior_radius - funnel_drop + self.tippe_radius * 2,
                forConstruction=True,
            )
            .radiusArc(
                endPoint=(
                    body_extra_radius,
                    -body_interior_radius - funnel_drop,
                ),
                radius=self.tippe_radius,
            )
            .line(-0.1, 0)
            .radiusArc(
                endPoint=(
                    body_extra_radius - 0.1,
                    -body_interior_radius - funnel_drop + self.tippe_radius * 2,
                ),
                radius=self.tippe_radius,
            )
            .close()
            .loft()
            # Remaining extension
            .faces(">X")
            .workplane()
            .transformed(
                offset=(
                    body_extra_radius - 0.1,
                    -body_interior_radius - funnel_drop + self.tippe_radius,
                )
            )
            .circle(radius=self.tippe_radius)
            .workplane(offset=self.tippe_radius * 2)
            .transformed(offset=(0, -inch_to_mm(0.1)))
            .circle(radius=self.tippe_radius)
            .loft()
        )

        hack_drop_factor = 1.5

        catcher_exterior = (
            cq.Workplane("YZ")
            # Mouth opening to workpiece
            .transformed(
                offset=(
                    0,
                    0,
                    -self.tippe_radius - mouth_gap_radius,
                )
            )
            .lineTo(0, mouth_exterior_radius, forConstruction=True)
            .radiusArc(
                endPoint=(0, -mouth_exterior_radius),
                radius=mouth_exterior_radius,
            )
            .line(-catch_width, 0)
            .radiusArc(
                endPoint=(-catch_width, mouth_exterior_radius),
                radius=mouth_exterior_radius,
            )
            .close()
            .workplane(offset=body_extra_radius)
            .lineTo(0, body_exterior_radius, forConstruction=True)
            .radiusArc(endPoint=(0, -body_exterior_radius), radius=body_exterior_radius)
            .line(-catch_width, 0)
            .radiusArc(
                endPoint=(-catch_width, body_exterior_radius),
                radius=body_exterior_radius,
            )
            .close()
            .loft()
            # Main body
            .faces(">X")
            .workplane()
            .lineTo(0, body_exterior_radius, forConstruction=True)
            .radiusArc(
                endPoint=(0, -body_exterior_radius),
                radius=body_exterior_radius,
            )
            .line(-catch_width, 0)
            .radiusArc(
                endPoint=(-catch_width, body_exterior_radius),
                radius=body_exterior_radius,
            )
            .close()
            .workplane(offset=body_length + self.tippe_radius * 2 + wall_thickness)
            .lineTo(
                0,
                body_exterior_radius - funnel_drop * hack_drop_factor,
                forConstruction=True,
            )
            .radiusArc(
                endPoint=(0, -body_exterior_radius - funnel_drop * hack_drop_factor),
                radius=body_exterior_radius,
            )
            .line(-catch_width, 0)
            .radiusArc(
                endPoint=(
                    -catch_width,
                    body_exterior_radius - funnel_drop * hack_drop_factor,
                ),
                radius=body_exterior_radius,
            )
            .close()
            .loft()
            # Shank
            .faces(">X")
            .workplane()
            .line(-shank_width, 0)
            .line(0, -self.tool_height)
            .line(shank_width, 0)
            .close()
            .extrude(-inch_to_mm(2.5))
        )

        part_off_subtract = (
            cq.Workplane("YZ")
            .transformed(offset=(inch_to_mm(0.1), inch_to_mm(0.1), inch_to_mm(0.1)))
            .rect(-shank_width * 2, -shank_width * 2, centered=False)
            .extrude(-shank_width)
        )

        retrieval_subtract = (
            cq.Workplane("XZ")
            .transformed(offset=(0, 0, 50))
            .lineTo(
                body_length + self.tippe_radius + tiny_extra,
                -body_exterior_radius
                - funnel_drop * hack_drop_factor
                + self.tippe_radius,
                forConstruction=True,
            )
            .line(-55, 41)
            .line(60, 0)
            .line(0, -40)
            .close()
            .extrude(-100)
        )

        return (
            catcher_exterior
            - part_off_subtract
            - retrieval_subtract
            - catcher_interior_subtract
        )


ttj = tippe_top_jigs()

show_object(
    ttj.tippe_body_round_exterior_lathe(), options={"color": "green", "alpha": 0.5}
)

# show_object(ttj.bar_puller(), options={"color": "blue", "alpha": 0.5})
show_object(ttj.catcher(), options={"color": "red", "alpha": 0.5})
