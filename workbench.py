"""
MIT License

Copyright (c) 2026 Roger Cheng

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


class workbench:
    """
    Small 3D-printed parts to help manage work bench miscellany
    """

    def __init__(self):
        # Adjust as needed for 3D printer precision
        self.print_margin = 0.2

    def light_panel_bracket(self):
        """
        L-shaped rails to help hold the LED light panel against the top of
        my soldering area. A mechanical solution after adhesive pads let go
        during a heat wave and the panel fell.
        """
        panel_thickness = 10
        claw_depth = 14
        claw_thickness = 5
        bracket_length = 100
        bracket_width = 15
        hole_radius = 5 / 2
        hole_distance_center = 0.75 * bracket_length / 2
        claw_fillet = 2
        corner_fillet = 5

        rail = (
            cq.Workplane("XZ")
            .line(claw_depth, 0)
            .line(0, claw_thickness)
            .line(-claw_depth, 0)
            .line(0, panel_thickness)
            .line(-bracket_width, 0)
            .line(0, -panel_thickness - claw_thickness)
            .close()
            .extrude(bracket_length / 2, both=True)
            .edges("|Z")
            .fillet(corner_fillet)
            .edges(sel.NearestToPointSelector((0, 0, claw_thickness)))
            .fillet(claw_fillet)
        )

        hole_subtract = (
            cq.Workplane("XY")
            .circle(radius=hole_radius)
            .extrude(panel_thickness + claw_thickness)
            .translate((-bracket_width / 2, 0, 0))
        )

        bracket = (
            rail
            - hole_subtract.translate((0, hole_distance_center))
            - hole_subtract.translate((0, -hole_distance_center))
        )

        return bracket


wb = workbench()
show_object(wb.light_panel_bracket())
