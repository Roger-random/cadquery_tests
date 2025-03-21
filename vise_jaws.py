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

import cadquery as cq
import cadquery.selectors as sel

# When not running in CQ-Editor, turn log into print
if "log" not in globals():

    def log(*args):
        print(args)


class hf_59111_central_machinery_4in_drill_press_vise:
    """
    Geometry to 3D-print soft jaws for:

    Harbor Freight #59111
    Central Machinery 4" Drill Press Vise
    https://www.harborfreight.com/4-in-drill-press-vise-59111.html

    This is the basic shape and I expect future projects to add the features
    necessary for various objectives.
    """

    def __init__(self):
        self.width = 100
        self.height = 20
        self.depth = 4
        self.fastener_distance_half = 30
        self.fastener_shaft_radius = 3.5
        self.fastener_shaft_depth = 1.5
        self.fastener_taper_depth = 1.7
        self.fastener_head_radius = 5.5

    def jaw(self):
        """
        Generates the base jaw facing the YZ plane, with all required parts
        extending along -X axis. Project-specific features can be added
        starting at X=0 and extending into positive X axis, then pass the
        results into fastener_cut() to cut holes for fasteners.
        """
        return cq.Workplane("YZ").rect(self.width, self.height).extrude(-self.depth)

    def fastener_cut(self, jaw, distance=100):
        """
        Given a shape that is the result of jaw() plus project-specific needs,
        cut the two holes for fasteners.
        """
        extra = 1  # Because sometimes CadQuery gets confused with exact match.
        fastener_cut = (
            cq.Workplane("YZ")
            .transformed(offset=(self.fastener_distance_half, 0, -self.depth - extra))
            .circle(self.fastener_shaft_radius)
            .extrude(self.fastener_shaft_depth + extra)
            .faces(">X")
            .workplane()
            .circle(self.fastener_shaft_radius)
            .workplane(offset=self.fastener_taper_depth)
            .circle(self.fastener_head_radius)
            .loft()
            .faces(">X")
            .workplane()
            .circle(self.fastener_head_radius)
            .extrude(distance)
        )

        return jaw - fastener_cut - fastener_cut.mirror("XZ")


if "show_object" in globals():
    vise = hf_59111_central_machinery_4in_drill_press_vise()
    show_object(
        vise.fastener_cut(vise.jaw())
        .edges("|X")
        .fillet(2)
        .rotate((0, 0, 0), (0, 1, 0), -90),
        options={"color": "green", "alpha": 0.5},
    )
