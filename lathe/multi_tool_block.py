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

from dataclasses import dataclass
from typing import List
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


@dataclass
class tool_dimension:
    """
    Data class for representing dimensions of a cutting tool and its relative
    positioning for purposes of calculating a multi tool block.
    """

    diameter: float
    length: float
    setscrew_position: float
    offset: float


class multi_tool_block:
    """
    Lathe turret tool post have multiple (typically four) sides, each designed
    to hold a single cutting tool. Sometimes that is not enough. A common
    method to add capacity is using a tool holder that occupies one station
    but hosts multiple cutting tools. Also called "gang tooling".

    Commercial solutions are modular allowing machine shops to rapidly
    reconfigure from one job to the next, but buying all components of such a
    modular system get expensive quickly.

    As a tradeoff of cost against time, it should be possible to cut tool
    blocks out of rectangular metal stock that is tailored to hold tools for
    a specific job. It'll be almost impossible to reconfigure for a different
    job, but cost only as much as the raw metal stock and relatively simple
    to machine on a vertical mill.

    This CadQuery script consumes a list of dimensions describing a set of lathe
    tools, and generates a 3D-printable mockup of a multi-tool block that can
    be used to check dimensions and tool clearance before the design is
    committing to metal.
    """

    def __init__(
        self,
        tool_height: float = inch_to_mm(0.75),
        tool_spacing: float = inch_to_mm(1.5),
        shank_height: float = inch_to_mm(0.85),
        shank_depth: float = inch_to_mm(0.65),
        setscrew_diameter: float = inch_to_mm(
            0.257
        ),  # 0.257" = size F drill for 5/16" threads
        print_margin: float = 0.1,
    ):
        """
        Creates a block generator configured for dimensions of a particular
        tool post.

        Defaults values from a Haas TL-2 (2007 vintage)

        tool_height: height of lathe cutting tool, more specifically height
        between bottom of tool post slot and lathe centerline. TL-2 = 0.75"

        shank_height: turret slot is bigger than tool_height, 0.89" on a TL-2.
        Since we're tailoring to the job (and the lathe) take advantage of
        that space for a bit of extra rigidity.

        shank_depth: turret slot has a certain depth, 0.628" on a TL-2.
        Make sure the shank is deeper than this value so we can index
        against inner wall of the tool slot.
        """
        self.tool_height = tool_height
        self.tool_spacing = tool_spacing
        self.shank_height = shank_height
        self.shank_depth = shank_depth
        self.setscrew_diameter = setscrew_diameter
        self.print_margin = print_margin

    def shank(self, length: float):
        return (
            cq.Workplane("YZ")
            .line(0, -self.tool_height)
            .line(self.shank_depth, 0)
            .line(0, self.shank_height)
            .line(-self.shank_depth, 0)
            .close()
            .extrude(length / 2, both=True)
        )

    def block(self, tools: List[tool_dimension]):
        if len(tools) < 1:
            raise ValueError("Must have at least one tool")
        block_width = self.tool_spacing * len(tools)

        # Establish the "offset=0" location based on length of all tools and
        # their offsets, and also look for the tool with the setscrew closest
        # to this point.
        max_tool_distance = 0
        setscrew_closest_to_edge = inch_to_mm(6)
        for tool in tools:
            tool_space_requirement = tool.length - tool.offset
            if tool_space_requirement > max_tool_distance:
                max_tool_distance = tool_space_requirement

            setscrew_from_tip = tool_space_requirement - tool.setscrew_position
            if setscrew_from_tip < setscrew_closest_to_edge:
                setscrew_closest_to_edge = setscrew_from_tip

        # Additional metal will add rigidity but no less than this.
        min_block_size = (
            max_tool_distance - setscrew_closest_to_edge + self.setscrew_diameter * 1.5
        )

        block_raw = (
            cq.Workplane("YZ")
            .line(0, -self.tool_height)
            .line(-min_block_size, 0)
            .line(0, self.tool_height * 2)
            .line(min_block_size, 0)
            .close()
            .extrude(block_width / 2, both=True)
        )

        self.tool_placeholder = None

        tool_start = (block_width / 2) - (self.tool_spacing / 2)
        for index, value in enumerate(tools):
            volume_r = self.print_margin + value.diameter / 2
            tool_volume = (
                cq.Workplane("XZ")
                .transformed(
                    offset=(
                        tool_start - (index * self.tool_spacing),
                        0,
                        max_tool_distance + value.offset,
                    ),
                    rotate=(0, 0, 45),
                )
                .line(volume_r, 0, forConstruction=True)
                .line(0, volume_r)
                .line(-volume_r, 0)
                .tangentArcPoint((volume_r, 0), relative=False)
                .close()
                .extrude(-value.length)
            )

            set_screw = (
                cq.Workplane("XY")
                .transformed(
                    offset=(
                        tool_start - (index * self.tool_spacing),
                        -max_tool_distance
                        - value.offset
                        + value.length
                        - value.setscrew_position,
                        0,
                    )
                )
                .circle(radius=self.setscrew_diameter / 2)
                .extrude(self.tool_height, both=True)
            )

            block_raw = block_raw - tool_volume - set_screw

            if self.tool_placeholder:
                self.tool_placeholder += tool_volume
            else:
                self.tool_placeholder = tool_volume

        block = block_raw

        # End of proper parametric logic and start of hard-coded experiment
        # section. Hope to turn into proper parametric logic after I figure
        # out how this is even going to work.
        drill025 = tools[1]
        drill025_end = max_tool_distance + drill025.offset - drill025.length
        ledge_perimeter_outer_x = self.tool_spacing / 4
        ledge_perimeter_outer = (
            cq.Workplane("XY")
            .transformed(offset=(0, 0, self.shank_height - self.tool_height))
            .line(-ledge_perimeter_outer_x, 0)
            .line(0, -drill025_end)
            .line(block_width, 0)
            .line(0, drill025_end)
            .close()
            .extrude(self.tool_height * 2)
        )
        ledge_perimeter_inner = (
            cq.Workplane("XY")
            .line(-ledge_perimeter_outer_x + self.shank_depth, 0, forConstruction=True)
            .line(0, -drill025_end + self.shank_depth)
            .line(block_width, 0)
            .line(0, drill025_end - self.shank_depth)
            .close()
            .extrude(self.tool_height, both=True)
        )
        boring_bar = tools[3]
        boring_bar_lip_alloance_y = (
            max_tool_distance + boring_bar.offset - boring_bar.length + 65
        )
        boring_bar_lip_allowancce = (
            cq.Workplane("XY")
            .line(self.tool_spacing, -boring_bar_lip_alloance_y, forConstruction=True)
            .line(-block_width, 0)
            .line(0, -max_tool_distance)
            .line(block_width, 0)
            .close()
            .extrude(self.tool_height, both=True)
        )

        block = (
            (block - boring_bar_lip_allowancce).edges("|Z").fillet(5)
            - ledge_perimeter_inner
            - ledge_perimeter_outer
        )

        block = (
            block.faces(">X")
            .edges("|Z and >Y")
            .fillet(5)
            .faces(">Y")
            .edges("|Z and >X")
            .fillet(5)
        )

        return block


mtb = multi_tool_block()

tool_list = list()

# #5 center drill
tool_list.append(
    tool_dimension(
        diameter=inch_to_mm(7 / 16),
        length=inch_to_mm(2 + 3 / 4),
        setscrew_position=inch_to_mm(1 + 3 / 8),
        offset=inch_to_mm(0.1),
    )
)

# 0.25" drill
tool_list.append(
    tool_dimension(
        diameter=inch_to_mm(0.25),
        length=inch_to_mm(4),
        setscrew_position=inch_to_mm(0.75),
        offset=inch_to_mm(0.75),
    )
)

# 0.5" drill
tool_list.append(
    tool_dimension(
        diameter=inch_to_mm(0.5),
        length=inch_to_mm(6),
        setscrew_position=inch_to_mm(1.5),
        offset=inch_to_mm(0.5),
    )
)

# Boring bar with 3/8" shank
tool_list.append(
    tool_dimension(
        diameter=inch_to_mm(3 / 8),
        length=inch_to_mm(4 + (7 / 8)),
        setscrew_position=inch_to_mm(0.5),
        offset=inch_to_mm(0.5),
    )
)

block = mtb.block(tool_list)

show_object(
    block,
    options={"color": "green", "alpha": 0.5},
)

show_object(mtb.tool_placeholder)
