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

"""
3D-printed bits that function as washer/wingnut for 1/4-20 bolts and nuts
"""

import cadquery as cq

def washer_wingnut(
    fastener_hex_width = 11.25,
    fastener_hex_thickness = 5.7,
    fastener_major_diameter_clear = 6.6,
    washer_chamfer = 1,
    washer_diameter = 20,
    washer_thickness = 2,
    wing_width = 5,
    wing_height = 10,
    wing_fillet = 2,
    ):

    overall_height = washer_thickness + fastener_hex_thickness + wing_height

    washer = (
        cq.Workplane("XY")
        .circle(washer_diameter/2)
        .extrude(overall_height)
    ).faces(">Z").fillet(wing_fillet).faces("<Z").chamfer(washer_chamfer)

    wing_removal = (
        cq.Workplane("XZ")
        .transformed(offset = cq.Vector(wing_width/2, overall_height-wing_height,0))
        .rect(30,30,centered = False)
        .extrude(washer_diameter, both = True)
    )
    washer = washer - wing_removal - wing_removal.mirror("YZ")

    washer = washer.faces(">Z[1]").edges("%Line").fillet(wing_fillet)

    hex = (
        cq.Workplane("XY")
        .transformed(offset = cq.Vector(0, 0, washer_thickness))
        .polygon(6, fastener_hex_width, circumscribed=True)
        .extrude(overall_height)
    )

    shaft = (
        cq.Workplane("XY")
        .circle(fastener_major_diameter_clear/2)
        .extrude(overall_height)
    )

    washer_wingnut = washer - hex - shaft

    washer_wingnut = washer_wingnut

    return washer_wingnut

if show_object:
    show_object(washer_wingnut(), options={"color":"blue", "alpha":0.5})
