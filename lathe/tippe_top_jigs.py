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
        self.part_off_tool_width = inch_to_mm(0.123)
        self.part_off_tool_end = self.tippe_body_top - self.part_off_tool_width
        self.partoff_placeholder_radius = inch_to_mm(0.325)

        # Groove for bar puller to grip
        self.grip_groove = self.part_off_tool_width

        # Lathe tool post is designed for cutters of this shank size
        self.tool_height = inch_to_mm(0.75)

        # End of the tippe body ball
        self.ball_end = -self.tippe_radius - self.quarter_sphere_groove_radius

        pass

    def tippe_body_round_exterior_lathe(self):
        """
        Visualizing the entire cross section of a Tippe Top body as it would sit
        on a CNC collet cut from bar stock.
        """

        groove_end = (
            -self.tippe_radius - self.quarter_sphere_groove_radius - self.grip_groove
        )
        groove_end_next = inch_to_mm(-1.05)

        return (
            cq.Workplane("ZX")
            .radiusArc(
                endPoint=(
                    self.quarter_sphere_groove_radius,
                    self.ball_end,
                ),
                radius=self.tippe_radius,
            )
            .lineTo(self.quarter_sphere_groove_radius, groove_end)
            .lineTo(self.tippe_radius, groove_end)
            .lineTo(self.tippe_radius, groove_end_next)
            .line(-self.grip_groove, 0)
            .line(0, -self.grip_groove)
            .line(self.grip_groove, 0)
            .lineTo(self.tippe_radius, -self.tippe_radius * 3)
            .radiusArc(
                endPoint=(0, -self.tippe_radius * 2),
                radius=-self.tippe_radius,
            )
            .lineTo(0, self.part_off_tool_end)
            .lineTo(self.partoff_placeholder_radius, self.part_off_tool_end)
            .lineTo(self.partoff_placeholder_radius, self.tippe_body_top)
            .lineTo(0, self.tippe_body_top)
            .close()
            .revolve(angleDegrees=360, axisStart=(0, 0, 0), axisEnd=(0, 1, 0))
        )

    def collet_collet(
        self,
        thickness=2.4,
        collet_radius=inch_to_mm(0.5),
        center_radius=inch_to_mm(0.375),
        depth=inch_to_mm(1),
        width=inch_to_mm(0.625),
    ):
        """
        A ball is awkward to hold in a standard 5C collet. There are blanks
        available for custom machined workholding called "emergency collets"
        but before we commit to cutting one up we can prototype with a 3D-
        printed collet that sits in a standard 5C collet.
        """
        revolve = (
            cq.Workplane("ZX")
            .radiusArc(
                endPoint=(
                    self.quarter_sphere_groove_radius,
                    self.ball_end,
                ),
                radius=self.tippe_radius,
            )
            .line(thickness, 0)
            .radiusArc(
                endPoint=(self.tippe_radius + thickness, -self.tippe_radius),
                radius=-self.tippe_radius,
            )
            .lineTo(self.tippe_radius + thickness, -thickness)
            .radiusArc(endPoint=(collet_radius, 0), radius=-thickness)
            .lineTo(collet_radius, depth - collet_radius * 0.25)
            .radiusArc(
                endPoint=(collet_radius * 0.75, depth), radius=-collet_radius / 4
            )
            .lineTo(0, depth)
            .close()
            .revolve(
                angleDegrees=360,
                axisStart=cq.Vector(0, 0, 0),
                axisEnd=cq.Vector(0, 1, 0),
            )
        )

        center = (
            cq.Workplane("YZ").circle(radius=center_radius).extrude(depth - thickness)
        ) + (
            cq.Workplane("YZ").circle(radius=center_radius).extrude(-self.tippe_radius)
        )

        fastener = (
            cq.Workplane("YZ")
            .transformed(offset=(-center_radius / 2, 0))
            .circle(radius=3.2 / 2)
            .extrude(depth + 1)
        )

        radians120 = math.radians(120)
        sin120 = math.sin(radians120)
        cos120 = math.cos(radians120)
        intersect_outer_y = -self.tippe_radius - thickness - 1
        intersect_half = (
            cq.Workplane("YZ")
            .lineTo(width * cos120 / 2, width * sin120 / 2)
            .lineTo(intersect_outer_y, width * sin120 / 2)
            .lineTo(intersect_outer_y, 0)
            .close()
            .extrude(depth + 1, both=True)
        )
        intersect = intersect_half + intersect_half.mirror("XY")

        leaf = (revolve - center - fastener).intersect(intersect)

        disc = (
            (
                cq.Workplane("YZ")
                .transformed(offset=(0, 0, depth - thickness))
                .circle(radius=center_radius - 0.2)
                .extrude(-thickness)
            )
            - fastener
            - fastener.rotate(
                axisStartPoint=(0, 0, 0), axisEndPoint=(1, 0, 0), angleDegrees=120
            )
            - fastener.rotate(
                axisStartPoint=(0, 0, 0), axisEndPoint=(1, 0, 0), angleDegrees=240
            )
        )

        return (leaf, disc)


ttj = tippe_top_jigs()

show_object(
    ttj.tippe_body_round_exterior_lathe(), options={"color": "green", "alpha": 0.5}
)

(leaf, disc) = ttj.collet_collet()
show_object(leaf, options={"color": "red", "alpha": 0.5})
show_object(disc, options={"color": "pink", "alpha": 0.5})
