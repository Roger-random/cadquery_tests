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


class logan_955_helpers:
    """
    A collection of 3D-printed designs associated with a Logan 955 lathe.
    Some are tools, some are quality of life improvements, some are just ideas
    that didnt' work out.
    """

    def __init__(self):
        pass

    def apron_lock_handle(self, square_side=(3 / 8) * 25.4 + 0.2, handle_length=50):
        """
        Handle for a square nut, intended for Z-axis apron axis lock
        """
        handle_width = square_side * 2.25
        handle_height = square_side
        handle_end = (
            cq.Workplane("XY")
            .circle(handle_width / 2)
            .extrude(handle_height / 2, both=True)
        )

        handle_bar = (
            cq.Workplane("XZ").rect(handle_width, handle_height).extrude(-handle_length)
        )

        nut_subtract = (
            cq.Workplane("XY")
            .rect(square_side, square_side)
            .extrude(handle_height, both=True)
        )

        label = (
            cq.Workplane("XY")
            .transformed(rotate=cq.Vector(0, 0, 90))
            .transformed(
                offset=cq.Vector(
                    handle_length / 2 + square_side * 0.75, 0, handle_height / 2 + 0.1
                )
            )
            .text("Z LOCK", 13, -0.6, kind="bold")
        )

        handle = (
            handle_end
            + handle_bar
            + handle_end.translate((0, handle_length, 0))
            - nut_subtract
        ).faces(">Z or <Z").chamfer(0.6) - label

        return handle

    def cross_feed_shim(self):
        """
        3D-print a shim to take up some Logan cross-feed backlash. Due to
        coarse granularity of 3D printer layers, this won't be an exact fit
        but should take up majority of backlash.
        """
        washer = cq.Workplane("XY").circle(radius=31 / 2).circle(radius=5).extrude(0.8)

        slot = cq.Workplane("XY").box(
            length=9, width=30, height=2, centered=(True, False, False)
        )

        return washer - slot


helpers = logan_955_helpers()

show_object(helpers.cross_feed_shim(), options={"color": "green", "alpha": 0.5})
