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

"""
3D-printed handle to be mounted on the 9mm metal shaft of a 7mm chuck key
"""

import cadquery as cq

# Handle is deliberately large so it's hard to forget and left on the lathe
handle_diameter = 30
handle_length = 150
handle_fillet = 10

# Metal shaft dimensions
shaft_diameter = 9
shaft_square_side = 7
shaft_flat_mismatch = 7.5 # Cover up amateur machinist mistake

# Fastener dimensions
fastener_shaft_center_offset = 10
fastener_shaft_diameter = 3.4
fastener_head_diameter = 6
fastener_square_nut_side = 5.5

# Handle exterior volume
handle = (
    cq.Workplane("XZ")
    .circle(handle_diameter/2)
    .extrude(handle_length/2,both=True)
    .fillet(handle_fillet)
    )

# Subtract square profile of metal shaft
handle = handle - (
    cq.Workplane("YZ")
    .rect(shaft_square_side, shaft_square_side)
    .extrude(handle_diameter, both=True)
    ).intersect(
    cq.Workplane("YZ")
    .circle(shaft_diameter/2)
    .extrude(handle_diameter, both=True)
    )

# Subtract round profile of metal shaft
handle = handle - (
    cq.Workplane("YZ")
    .transformed(offset=cq.Vector(0,0,handle_diameter/2 - shaft_flat_mismatch))
    .circle(shaft_diameter/2)
    .extrude(handle_diameter)
    )

# Subtract volume for two fasteners
# Start with cylinder to clear fastener shaft
fastener = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(0,fastener_shaft_center_offset,0))
    .circle(fastener_shaft_diameter/2)
    .extrude(handle_diameter,both=True)
    )

# Add cylinder to clear fastener head
fastener = fastener + (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(0,fastener_shaft_center_offset,handle_diameter/2-4))
    .circle(fastener_head_diameter/2)
    .extrude(handle_diameter)
    )

# Add volume for square nut
fastener = fastener + (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(0,fastener_shaft_center_offset,-handle_diameter/2+4))
    .rect(fastener_square_nut_side, fastener_square_nut_side)
    .extrude(-handle_diameter)
    )

# Subtract symmetric pair of fasteners
handle = handle - fastener
handle = handle - fastener.rotate((0,0,0),(1,0,0),180)

# Keep just the top half.
# TODO: figure out how to do this right with .split()
#   handle.split(keepTop=True) splits on XZ plane instead of XY plane as expected.
handle = handle - (
    cq.Workplane("XY")
    .rect(handle_length*2, handle_length*2)
    .extrude(-handle_diameter)
    )
# Split the shape in half
show_object(handle, options={"color":"blue", "alpha":0.5})