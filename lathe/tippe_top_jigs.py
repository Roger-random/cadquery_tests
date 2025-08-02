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
        thickness=inch_to_mm(0.2),
        collet_radius=inch_to_mm(0.5),
        center_radius=inch_to_mm(0.375),
        inner_fillet=inch_to_mm(0.1),
        depth=inch_to_mm(1),
        width=inch_to_mm(0.625),
        holding_ring_depth=inch_to_mm(0.2),
        holding_ring_thickness=3,
        holding_ring_chamfer=1,
        clearance=0.2,
    ):
        """
        A ball is awkward to hold in a standard 5C collet. There are blanks
        available for custom machined workholding called "emergency collets"
        but before we commit to cutting one up we can prototype with a 3D-
        printed collet that sits in a standard 5C collet.
        """
        clearance_radius = collet_radius - clearance
        holding_ring_start = (
            depth - inner_fillet - holding_ring_depth - holding_ring_chamfer * 2
        )
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
            .radiusArc(endPoint=(clearance_radius, 0), radius=-thickness)
            .lineTo(clearance_radius, holding_ring_start)
            .line(-holding_ring_chamfer, holding_ring_chamfer)
            .line(holding_ring_chamfer - holding_ring_thickness, 0)
            .line(0, holding_ring_depth)
            .line(holding_ring_thickness - holding_ring_chamfer, 0)
            .lineTo(clearance_radius, depth - inner_fillet)
            .radiusArc(
                endPoint=(clearance_radius - inner_fillet, depth), radius=-inner_fillet
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
            cq.Workplane("YZ")
            .circle(radius=center_radius)
            .extrude(holding_ring_start - holding_ring_depth)
            .faces(">X")
            .fillet(thickness)
        ) + (
            cq.Workplane("YZ").circle(radius=center_radius).extrude(-self.tippe_radius)
        )

        radians120 = math.radians(120)
        sin120 = math.sin(radians120)
        cos120 = math.cos(radians120)
        intersect_outer_y = -self.tippe_radius - thickness - 1
        intersect_half = (
            cq.Workplane("YZ")
            .lineTo(-clearance, 0, forConstruction=True)
            .lineTo(width * cos120 / 2 - clearance, width * sin120 / 2)
            .lineTo(intersect_outer_y, width * sin120 / 2)
            .lineTo(intersect_outer_y, 0)
            .close()
            .extrude(depth + 1, both=True)
        )
        intersect = intersect_half + intersect_half.mirror("XY")

        leaf = (revolve - center).intersect(intersect)

        ring = (
            cq.Workplane("YZ")
            .transformed(offset=(0, 0, holding_ring_start + holding_ring_chamfer))
            .circle(radius=clearance_radius)
            .circle(radius=clearance_radius - holding_ring_thickness)
            .extrude(holding_ring_depth)
            .faces(">X")
            .chamfer(holding_ring_chamfer)
        ) - (
            cq.Workplane("XY").box(
                length=depth,
                width=depth,
                height=clearance,
                centered=(False, False, True),
            )
        )

        return (leaf, ring)

    def collet_cap(self):
        """
        A piece of 3D-printed plastic that helps place a turned tippe top body
        into a 1" 5C collet
        """
        subtract = (
            cq.Workplane("YZ")
            .transformed(offset=(0, 0, self.tippe_body_top))
            .circle(radius=12.5)
            .extrude(-self.tippe_body_top)
        )

        plate_radius = self.tippe_radius + 5
        plate_hole_radius = 2
        plate_well_depth = inch_to_mm(0.2)
        plate_thickness = 2.4
        plate = (
            cq.Workplane("YZ")
            .transformed(offset=(0, 0, self.tippe_body_top + plate_well_depth))
            .circle(radius=plate_radius)
            .circle(radius=plate_hole_radius)
            .extrude(-plate_well_depth - plate_thickness)
        )

        return plate - subtract


ttj = tippe_top_jigs()

show_object(ttj.collet_cap(), options={"color": "green", "alpha": 0.5})
