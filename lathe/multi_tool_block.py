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
    relative_offset: float


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
        shank_height: float = inch_to_mm(0.85),
        shank_depth: float = inch_to_mm(0.65),
        setscrew_diameter: float = inch_to_mm(5 / 16),
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
        self.shank_height = shank_height
        self.shank_depth = shank_depth
        self.setscrew_diameter = setscrew_diameter

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
        block_width = self.tool_height * 2 * len(tools)
        return self.shank(length=block_width)


mtb = multi_tool_block()

tool_list = list()

rod = tool_dimension(
    diameter=inch_to_mm(0.196),
    length=67,
    setscrew_position=inch_to_mm(0.25),
    relative_offset=0,
)

tool_list.append(rod)
tool_list.append(rod)

show_object(
    mtb.block(tool_list),
    options={"color": "green", "alpha": 0.5},
)
