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
Generate a small block with an array of holes with increasing diameters.
Designed for testing dimensional accuracy of specific 3D printers.
"""
import cadquery as cq

starting_diameter = 3.0
diameter_increment = 0.05

cell_size_x = 13
cell_size_y = 13

cell_count_x = 5
cell_count_y = 4

cell_thickness = 10
block_edge_bevel = 0.5
block_corner_fillet = 3

block_size_x = cell_size_x * cell_count_x
block_size_y = cell_size_y * cell_count_y
block_size_z = cell_thickness

block = (
    cq.Workplane("XY")
    .box(block_size_x,block_size_y,block_size_z)
    )
block = block.edges("|Z").fillet(block_corner_fillet)

hole_diameter = starting_diameter

text = (
    cq.Workplane("XZ")
    .transformed(
        offset = cq.Vector(0,0,block_size_y/2)
        )
    .text("{:.2f} step {:.2f}".format(starting_diameter, diameter_increment), fontsize=8,distance=0.2, combine=False)
    )

for cell_y in range(cell_count_y):
    for cell_x in range(cell_count_x):
        center_x = cell_size_x/2 - block_size_x/2 + cell_x * cell_size_x
        center_y = cell_size_y/2 - block_size_y/2 + cell_y * cell_size_y
        block = (
            block.faces(">Z").workplane(origin = (center_x, center_y+hole_diameter*(2/3)))
            .hole(hole_diameter)
        )
        text = text + (
            cq.Workplane("XY")
            .transformed(
                offset = cq.Vector(
                    center_x,
                    center_y-(cell_size_y/2)+(block_edge_bevel*2),
                    block_size_z/2)
                )
            .text("{:.2f}".format(hole_diameter), 
                  fontsize=5, kind="bold",
                  valign="bottom", distance=0.2, combine=False)
        )
        hole_diameter = hole_diameter + diameter_increment

block = block.faces().chamfer(block_edge_bevel)

#show_object(block, options = {"alpha":0.5, "color":"red"})
#show_object(text, options = {"alpha":0.5, "color":"green"})

assembly = block + text
show_object(assembly)

"""
# Tilted print on 3DPrintMill
raft_air_gap = 0.3
brim_height = 0.5
assembly = assembly.translate((
    0,
    block_size_y/2 - block_edge_bevel - raft_air_gap,
    block_size_z/2 + raft_air_gap)).rotate(
        (0,0,0),
        (1,0,0),
        45
    )

import math
support = (
    cq.Workplane("YZ")
    .lineTo(-raft_air_gap*math.sqrt(2), 0)
    .lineTo(-raft_air_gap*math.sqrt(2), brim_height)
    .lineTo(brim_height, brim_height)
    .lineTo(40,40)
    .lineTo(40,0)
    .close()
    .extrude(35, both=True)
    )
show_object(assembly+support)
"""
