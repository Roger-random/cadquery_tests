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
3D-printed jig to hold a 1/2" pipe fitting vertically in a machine vise
"""

import cadquery as cq

def pipe_fitting_jig(
    diameter = 13,
    block_side = 23,
    slit = 2
    ):
    block = (
        cq.Workplane("XY")
        .rect(block_side, block_side)
        .circle(diameter/2)
        .extrude(block_side)
    )

    slit = (
        cq.Workplane("XY")
        .rect(slit, block_side)
        .extrude(block_side)
    )

    keep_half = (
        cq.Workplane("YZ")
        .rect(block_side*2, block_side*2)
        .extrude(block_side*2)
    )

    return (block - slit).intersect(keep_half)

if 'show_object' in globals():
    show_object(pipe_fitting_jig(), options={"color":"blue", "alpha":0.5})
