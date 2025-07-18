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


class knurling_tool_post:
    """
    3D-printable shape to illustrate plan for a knurling tool post that sits
    directly on saddle where compound would normally sit.
    The final product will be cut out of steel for strength because 3D-printed
    plastic will not be rigid enough.
    """

    def __init__(
        self,
        stock_diameter=inch_to_mm(4),
        width_saddle=inch_to_mm(3.5),
        height_saddle_to_tool=inch_to_mm(2),
        height_tool=inch_to_mm(1.25),
        width_tool=inch_to_mm(0.5),
        tool_setback=inch_to_mm(0.5),
        tool_setback_height=inch_to_mm(1.75),
        fastener_diameter=inch_to_mm(0.25),
        cone_diameter_top=inch_to_mm(1.5),
        cone_diameter_bottom=inch_to_mm(2),
        cone_bottom_lip=inch_to_mm(0.05),
        cone_top_gap=inch_to_mm(0.05),
        cone_height=inch_to_mm(0.25),
    ):
        self.stock_diameter = stock_diameter
        self.width_saddle = width_saddle
        self.height_saddle_to_tool = height_saddle_to_tool
        self.height_tool = height_tool
        self.width_tool = width_tool
        self.tool_setback = tool_setback
        self.tool_setback_height = tool_setback_height
        self.fastener_diameter = fastener_diameter
        self.cone_diameter_top = cone_diameter_top
        self.cone_diameter_bottom = cone_diameter_bottom
        self.cone_bottom_lip = cone_bottom_lip
        self.cone_top_gap = cone_top_gap
        self.cone_height = cone_height

        self.height_above_saddle = (
            self.height_saddle_to_tool + height_tool + inch_to_mm(0.5)
        )

    def post(self):
        cone = (
            cq.Workplane("XY")
            .circle(radius=self.cone_diameter_top / 2)
            .extrude(-self.cone_top_gap)
            .faces("<Z")
            .workplane()
            .circle(radius=self.cone_diameter_top / 2)
            .workplane(offset=self.cone_height)
            .circle(radius=self.cone_diameter_bottom / 2)
            .loft()
            .faces("<Z")
            .workplane()
            .circle(radius=self.cone_diameter_bottom / 2)
            .extrude(self.cone_bottom_lip)
        )

        base = (
            cq.Workplane("XY")
            .circle(radius=self.stock_diameter / 2)
            .extrude(self.height_above_saddle)
        )

        saddle_volume = cq.Workplane("XY").box(
            length=self.width_saddle,
            width=self.stock_diameter,
            height=self.height_above_saddle,
            centered=(True, True, False),
        )

        setback_volume = (
            cq.Workplane("XY")
            .transformed(
                offset=(
                    0,
                    self.stock_diameter / 2 - self.tool_setback,
                    self.tool_setback_height,
                )
            )
            .box(
                length=self.stock_diameter,
                width=self.stock_diameter,
                height=self.stock_diameter,
                centered=(True, False, False),
            )
        )

        tool_install_volume = (
            cq.Workplane("XY")
            .transformed(
                offset=(
                    self.width_tool / 2,
                    0,
                    self.height_saddle_to_tool,
                )
            )
            .box(
                length=self.stock_diameter,
                width=self.stock_diameter,
                height=self.stock_diameter,
                centered=(False, True, False),
            )
        )

        tool_volume = (
            cq.Workplane("XY")
            .transformed(
                offset=(
                    self.width_tool / 2,
                    0,
                    self.height_saddle_to_tool,
                )
            )
            .box(
                length=self.width_tool * 2,
                width=self.stock_diameter,
                height=self.height_tool,
                centered=(True, True, False),
            )
        )

        fastener_span = self.stock_diameter - self.tool_setback
        fastener_spacing = fastener_span / 3
        fastener_center = self.tool_setback / 2
        fastener = (
            cq.Workplane("XY")
            .transformed(offset=(0, -fastener_center, self.height_saddle_to_tool))
            .circle(radius=self.fastener_diameter / 2)
            .extrude(self.stock_diameter)
        )

        post = (
            cone
            + base.intersect(saddle_volume)
            - setback_volume
            - tool_install_volume
            - tool_volume
            - fastener
            - fastener.translate((0, -fastener_spacing, 0))
            - fastener.translate((0, fastener_spacing, 0))
        )

        return post


ktp = knurling_tool_post()

show_object(ktp.post(), options={"color": "gray", "alpha": 0.5})
