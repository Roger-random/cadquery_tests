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
Experiment in 3D-printing a frame around a piece of acrylic
"""

import cadquery as cq

def acrylic_frame(
    acrylic_length = 56,
    acrylic_width = 29,
    acrylic_thickness = 3.2,
    frame_thickness = 1.2
    ):
    af = (
        # Outer frame
        cq.Workplane("XY")
        .box(
            acrylic_length + frame_thickness*2,
            acrylic_width + frame_thickness*2,
            acrylic_thickness + frame_thickness*2)
        .edges("|Z").fillet(frame_thickness)
    ) - (
        # Inner void
        cq.Workplane("XY")
        .box(
            acrylic_length - frame_thickness*2,
            acrylic_width - frame_thickness*2,
            acrylic_thickness + frame_thickness*2
        )
    ) - (
        # Acrylic slot
        cq.Workplane("XY")
        .box(
            acrylic_length,
            acrylic_width,
            acrylic_thickness
        )
    )

    return af

if 'show_object' in globals():
    show_object(acrylic_frame(), options={"color":"blue", "alpha":0.5})
