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


class fork_spool_stand:
    """
    Bench testing motor salvaged from a dead Xiaomi scooter, this holds the
    front fork vertical using an expended eSun 3kg filament spool as base.
    """

    def __init__(
        self,
        fork_external_diameter: float,
        fork_height: float,
        spool_internal_diameter: float,
        spool_height: float,
        top_wall_thickness: float = 2.4,
        chamfer: float = 0.6,
        seam_invitation_size: float = 0.25,
    ):
        self.fork_external_diameter = fork_external_diameter
        self.fork_height = fork_height
        self.spool_internal_diameter = spool_internal_diameter
        self.spool_height = spool_height
        self.top_wall_thickness = top_wall_thickness
        self.chamfer = chamfer
        self.seam_invitation_size = seam_invitation_size

    def adapter(self):
        exterior_volume = (
            cq.Workplane("XY")
            .circle(self.spool_internal_diameter / 2)
            .extrude(self.spool_height)
            .faces(">Z")
            .workplane()
            .circle(self.spool_internal_diameter / 2)
            .workplane(offset=self.fork_height - self.spool_height)
            .circle(self.fork_external_diameter / 2 + self.top_wall_thickness)
            .loft()
        )

        interior_space = (
            cq.Workplane("XY")
            .circle(self.fork_external_diameter / 2)
            .extrude(self.fork_height)
        )

        adapter = exterior_volume - interior_space

        adapter = adapter.faces("<Z or >Z").chamfer(self.chamfer)

        return adapter


stand = fork_spool_stand(
    fork_external_diameter=30,
    fork_height=200,
    spool_internal_diameter=52,
    spool_height=100,
)

show_object(
    stand.adapter(),
    options={"color": "green", "alpha": 0.5},
)
