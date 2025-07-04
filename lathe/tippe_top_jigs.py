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


def tippe_revolve():
    """
    Visualizing the entire cross section of a Tippe Top body as it would sit
    on a CNC collet cut from bar stock.
    """
    return (
        cq.Workplane("ZX")
        .radiusArc(endPoint=(1 / 2, -0.5), radius=0.5)
        .radiusArc(endPoint=(0.7071 / 2, -0.85355), radius=0.5)
        .lineTo(1.0 / 2, -1.0)
        .lineTo(0.8 / 2, -1.1)
        .lineTo(1.0 / 2, -1.2)
        .lineTo(1.0 / 2, -1.5)
        .radiusArc(endPoint=(0, -1.0), radius=-0.5)
        .lineTo(0, -0.95355)
        .lineTo(0.25, -0.95355)
        .lineTo(0.25, -0.85355)
        .lineTo(0, -0.85355)
        .close()
        .revolve(angleDegrees=360, axisStart=(0, 0, 0), axisEnd=(0, 1, 0))
    )


show_object(tippe_revolve(), options={"color": "green", "alpha": 0.5})
