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
3D-printed U-shaped brace to keep a spine upright
"""

import cadquery as cq

def spine_brace_u(
    fastener_distance = 30,
    fastener_hex_width = 11.25,
    fastener_hex_thickness = 5.7,
    fastener_major_diameter_clear = 6.6,
    spine_width = 8,
    spine_height = 40,
    brace_fillet = 2,
    brace_length = 25,
    brace_thickness = 2.4,
    brace_width = 45,
    ):

    brace_half = (
        # Overall volume
        cq.Workplane("XY")
        .lineTo(spine_width/2, 0, forConstruction=True)
        .lineTo(brace_width/2, 0)
        .line(0, spine_height)
        .radiusArc((0,spine_height+brace_width/2),-brace_width/2)
        .line(0, spine_width/2-brace_width/2)
        .radiusArc((spine_width/2, spine_height), spine_width/2)
        .close()
        .extrude(brace_length)
    ) - (
        # Internal void volume
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(0,0,brace_thickness))
        .lineTo(spine_width/2 + brace_thickness, brace_thickness+fastener_hex_thickness, forConstruction=True)
        .lineTo(brace_width/2, brace_thickness+fastener_hex_thickness)
        .line(0, spine_height - brace_thickness-fastener_hex_thickness)
        .radiusArc((0,spine_height+brace_width/2),-brace_width/2)
        .line(0, brace_thickness+spine_width/2-brace_width/2)
        .radiusArc((spine_width/2+brace_thickness, spine_height), spine_width/2+brace_thickness)
        .close()
        .extrude(brace_length)
    )

    brace_half = brace_half.faces("<Y[0]").edges("|Z").fillet(brace_fillet)
    brace_half = brace_half.faces("<Y[1]").edges("|Z").fillet(brace_fillet)
    brace_half = brace_half.faces(">Z[1]").edges("<Y").fillet(brace_fillet)

    fastener_clearance = (
        cq.Workplane("XZ")
        .transformed(offset=cq.Vector(fastener_distance/2, brace_length/2, 0))
        .circle(fastener_major_diameter_clear/2)
        .extrude(-brace_thickness)
    )
    brace_half = brace_half-fastener_clearance

    hex_clearance = (
        cq.Workplane("XZ")
        .transformed(offset=cq.Vector(fastener_distance/2, brace_length/2, -brace_thickness))
        .polygon(6, fastener_hex_width, circumscribed=True)
        .extrude(-fastener_hex_thickness)
    )
    brace_half = brace_half - hex_clearance

    brace = brace_half + brace_half.mirror("YZ")

    brace = brace.faces("<Z").chamfer(brace_thickness*0.3)
    brace = brace.faces(">Z").chamfer(brace_thickness*0.3)

    return brace

if show_object:
    show_object(spine_brace_u(), options={"color":"blue", "alpha":0.5})
