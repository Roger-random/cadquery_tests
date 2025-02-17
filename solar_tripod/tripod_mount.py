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
3D-printed mount to fit on the dovetail of a Monoprice tripod
"""

import cadquery as cq

def tripod_dovetail(
    dovetail_height = 6.25,
    dovetail_length = 42.4,
    dovetail_bottom_fillet = 2.5,
    dovetail_bottom_width = 38.7,
    dovetail_top_width = 32.15,
    top_lip_height = 1.8,
    top_lip_length = 50,
    top_lip_width = 45,
    ):
    dovetail_half = (
        cq.Workplane("XZ")
        .lineTo(dovetail_top_width/2, 0)
        .lineTo(dovetail_bottom_width/2, -dovetail_height)
        .lineTo(0, -dovetail_height)
        .close()
        .extrude(dovetail_length/2, both=True)
    ).edges(">X").fillet(dovetail_bottom_fillet)

    top_lip_half = (
        cq.Workplane("XZ")
        .lineTo(top_lip_width/2, 0)
        .line(0, top_lip_height)
        .line(-top_lip_width/2, 0)
        .close()
        .extrude(top_lip_length/2, both=True)
    )

    dovetail_half = dovetail_half + top_lip_half

    dovetail = dovetail_half + dovetail_half.mirror("YZ")

    dovetail = dovetail.edges("|Z").fillet(5)

    return dovetail


if show_object:
    show_object(tripod_dovetail(), options={"color":"blue", "alpha":0.5})
