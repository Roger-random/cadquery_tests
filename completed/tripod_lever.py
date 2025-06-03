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


class tripod_lever:
    """
    Replacement retention lever for Monoprice 10262 tripod. (Long discontinued)
    There is a fundamental design flaw in the original, where the plastic lever
    is constrained between its fastener in the middle and the spring within its
    base. Leaving only a small volume for structural plastic in between and that
    is where it fails.

    A direct 3D-printed plastic replacement will inevitaably fail in the exact
    same way, so this replacement design gives up the spring in exchange for
    strength. It is no longer spring-loaded and held only by friction.
    """

    def __init__(self):
        self.fastener_shaft_radius = 6.5 / 2
        self.fastener_head_radius = 8 / 2
        self.fastener_shaft_height = 4.7
        self.height = 6.2
        self.wedge_radius_bottom = 7.3
        self.wedge_radius_top = 11.5
        self.wedge_stop_radius = 7.3
        self.handle_rear_radius = 10.2
        self.handle_length = 26
        self.handle_wedge_fillet = 6

    def fastener_volume_subtract(self):
        return (
            cq.Workplane("XY")
            .circle(radius=self.fastener_shaft_radius)
            .extrude(self.fastener_shaft_height)
            .faces(">Z")
            .workplane()
            .circle(radius=self.fastener_head_radius)
            .extrude(self.height - self.fastener_shaft_height)
        )

    def lever(self):
        wedge_disc = (
            cq.Workplane("XY")
            .circle(radius=self.wedge_radius_bottom)
            .workplane(offset=self.height)
            .circle(radius=self.wedge_radius_top)
            .loft()
        )
        wedge_volume_intersect = (
            cq.Workplane("XY")
            .lineTo(0, -self.wedge_stop_radius, forConstruction=True)
            .lineTo(-self.wedge_radius_top, -self.wedge_stop_radius)
            .lineTo(-self.wedge_radius_top, self.handle_length)
            .lineTo(self.handle_rear_radius, self.handle_length)
            .lineTo(self.handle_rear_radius, -self.wedge_stop_radius)
            .close()
            .extrude(self.height)
        )
        handle = (
            cq.Workplane("XY")
            .lineTo(0, self.handle_length)
            .tangentArcPoint(
                endpoint=(self.handle_rear_radius, self.handle_length), relative=False
            )
            .lineTo(self.handle_rear_radius, -self.wedge_stop_radius)
            .lineTo(0, -self.wedge_stop_radius)
            .close()
            .extrude(self.height)
        )
        wedge = wedge_disc.intersect(wedge_volume_intersect)
        lever = wedge + handle - self.fastener_volume_subtract()

        # Round off the stress riser edge where wedge meets handle
        lever = lever.edges(
            sel.NearestToPointSelector(
                pnt=(
                    0,
                    (self.wedge_radius_top + self.wedge_radius_bottom) / 2,
                    self.height / 2,
                )
            )
        ).fillet(self.handle_wedge_fillet)

        # Round off the edge diagonally opposite the above, just for aesthetics
        lever = lever.edges(
            sel.NearestToPointSelector(
                pnt=(
                    self.handle_rear_radius,
                    -self.wedge_stop_radius,
                    self.height / 2,
                )
            )
        ).fillet(self.handle_wedge_fillet)

        return lever


tl = tripod_lever()
show_object(
    tl.lever(),
    options={"color": "green", "alpha": 0.5},
)
