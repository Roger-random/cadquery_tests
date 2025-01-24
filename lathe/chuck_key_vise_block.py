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
3D-printed block to hold a cylindrical chuck key candidate in a vise so a
mill can square off the end.
"""
import cadquery as cq

mm_per_inch = 25.4

# Mill has a 6" wide vise installed
block_width = 6 * mm_per_inch
block_height = 30
block_edge_fillet = 5
cylinder_diameter = 9

# Narrow slot in the middle intended to compress under vise pressure
slot_gap = 1

# No slot on the side opposite the piece intended to balance out forces
# against the edge of the piece
slotless_width = 20

block = (
    cq.Workplane("XZ")
    .rect(block_width, block_height)
    .extrude(-block_height/2)
    )

slot = (
    cq.Workplane("XZ")
    .transformed(offset=cq.Vector(slotless_width/2,0,0))
    .rect(block_width-slotless_width, block_height)
    .extrude(-slot_gap/2)
    )

cylinder = (
    cq.Workplane("YZ")
    .circle(cylinder_diameter/2)
    .extrude(block_width, both=True)
    )

block = block - slot

block = block.edges("|Y").fillet(block_edge_fillet)

block = block - cylinder

block2 = block.mirror("XZ")

show_object(block , options={"color":"red", "alpha":0.5})
show_object(block2 , options={"color":"blue", "alpha":0.5})