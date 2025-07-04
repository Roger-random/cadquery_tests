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


class sb_disassembly_jigs:
    """
    A collection of simple shapes used to help disassemble a lathe for
    rebuild: a South Bend Model A Catalog No. 955Y from 1942
    """

    def __init__(self):
        pass

    def traverse_gear_support(self):
        """
        Stepped ring to support the traverse gear while I tap out its center
        pin. A cylindrical volume of 1.2" diameter to surround the gear and
        keep this support in the correct place, and a cylindrival volume of
        0.65" diameter to allow the pin to exit.
        """
        outer_radius = inch_to_mm(1.4) / 2
        gear_surround = (
            cq.Workplane("XY")
            .circle(radius=outer_radius)
            .circle(radius=inch_to_mm(1.2) / 2)
            .extrude(inch_to_mm(0.5))
        )

        pin_clear = (
            cq.Workplane("XY")
            .circle(radius=outer_radius)
            .circle(radius=inch_to_mm(0.65) / 2)
            .extrude(-inch_to_mm(1.3))
        )
        return gear_surround + pin_clear


jigs = sb_disassembly_jigs()

show_object(jigs.traverse_gear_support(), options={"color": "green", "alpha": 0.5})
