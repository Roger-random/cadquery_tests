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
Misplaced my tap handle. Don't need a lot of strength today so 3D print a
quick and small piece that's better than just using fingers.
"""

import cadquery as cq

def pipe_tap_handle(
    length_half = 150,
    width_half = 20,
    height = 20,
    corner_fillet = 5,
    face_fillet = 3,
    tap_square_side = 14,
    ):

    quarter = (
        cq.Workplane("XY")
        .lineTo(0,length_half)
        .lineTo(width_half,0)
        .close()
        .extrude(height)
    )

    handle = quarter + quarter.mirror("YZ")
    handle = handle + handle.mirror("XZ")
    handle = handle.edges("|Z").fillet(corner_fillet)

    handle = (
        handle.faces("<Z").workplane()
        .rect(tap_square_side, tap_square_side)
        .extrude(-height, combine='cut')
    )

    handle = handle.faces("<Z").fillet(face_fillet)
    handle = handle.faces(">Z").fillet(face_fillet)

    return handle

if 'show_object' in globals():
    show_object(pipe_tap_handle(), options={"color":"blue", "alpha":0.5})
