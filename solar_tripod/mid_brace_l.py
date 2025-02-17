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
3D-printed L-shaped brace for middle of the span
"""

import cadquery as cq

def mid_brace_l(
    fastener_distance = 30,
    fastener_major_diameter_clear = 6.6,
    brace_corner_fillet = 2,
    brace_thickness = 5,
    brace_leg_length = 40,
    brace_leg_width = 100,
    ):
    mid_brace = (
        cq.Workplane("XY")
        .lineTo(brace_leg_length, 0)
        .lineTo(0, brace_leg_length)
        .close()
        .extrude(brace_leg_width)
    ).edges("|Z").fillet(brace_corner_fillet)

    mid_brace = mid_brace - mid_brace.translate((
        brace_thickness,
        brace_thickness,
        1.8
    ))

    fastener_hole =(
        cq.Workplane("XZ")
        .transformed(offset=cq.Vector(brace_leg_length/2, brace_leg_width/2 + fastener_distance/2, 0))
        .circle(fastener_major_diameter_clear/2)
        .extrude(-brace_thickness)
    )

    if False:
        # Visualize clearance for washer wingnut
        show_object(
            cq.Workplane("XZ")
            .transformed(offset=cq.Vector(brace_leg_length/2, brace_leg_width/2 - fastener_distance/2 - 20, 0))
            .circle(10)
            .extrude(-brace_thickness)
        )

    mid_brace = (
        mid_brace
        - fastener_hole
        - fastener_hole.translate((0, 0, -fastener_distance))
        - fastener_hole.rotate((0,0,0),(0,0,1), -90).mirror("XZ").translate((0, 0,  20))
        - fastener_hole.rotate((0,0,0),(0,0,1), -90).mirror("XZ").translate((0, 0, -fastener_distance-20))
    )

    return mid_brace

if show_object:
    show_object(mid_brace_l(), options={"color":"blue", "alpha":0.5})
