"""
MIT License

Copyright (c) 2024 Roger Cheng

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
from placeholders import bearing, spool

# When not running in CQ-Editor, turn log into print
if "log" not in globals():

    def log(*args):
        print(args)


# When not running in CQ-Editor, turn show_object into no-op
if "show_object" not in globals():

    def show_object(*args):
        pass


class file_handle:
    """
    3D printed handle for a Nicholson file
    """

    def __init__(self):
        pass

    def handle(self):
        handle_volume = (
            cq.Workplane("YZ")
            .lineTo(0, 13)
            .bezier(
                (
                    (8, 20),
                    (17, 0),
                    (30, 11),
                    (45, 13),
                    (73, 15),
                    (100, 11),
                    (105, 8),
                ),
                includeCurrent=True,
            )
            .radiusArc((110, 0), radius=8)
            .close()
            .revolve(360, (0, 0, 0), (1, 0, 0))
        )

        hook_subtract = (
            cq.Workplane("YZ")
            .transformed(offset=cq.Vector(98, 0, 0))
            .circle(3)
            .extrude(30, both=True)
        )

        side_intersect = cq.Workplane("XZ").rect(17.5, 40).extrude(-120)

        tine_subtract = (
            cq.Workplane("XZ").rect(4.7, 15).workplane(offset=-58).rect(2.7, 7).loft()
        )
        handle = (handle_volume - hook_subtract - tine_subtract).intersect(
            side_intersect
        )

        return handle


fh = file_handle()
show_object(fh.handle(), options={"color": "white", "alpha": 0.5})
