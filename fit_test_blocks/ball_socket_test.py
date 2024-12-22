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
Generate a small block with an array of ball-and-socket assemblies with
increasing gaps between ball and socket.
Designed for testing dimensional accuracy of specific 3D printers.
"""
import cadquery as cq

ball_radius = 4
fastener_diameter = 3.5

starting_gap = 0
gap_increment = 0.01

cell_size_x = 15
cell_size_y = 15

cell_count_x = 5
cell_count_y = 4

cell_thickness = 4
block_edge_bevel = 0.5
block_corner_fillet = 3

print_text_labels = True

block_size_x = cell_size_x * cell_count_x
block_size_y = cell_size_y * cell_count_y
block_size_z = cell_thickness

block = (
    cq.Workplane("XY")
    .box(block_size_x,block_size_y,block_size_z)
    )
block = block.edges("|Z").fillet(block_corner_fillet)

if print_text_labels:
    texts = list()

ball = (
    cq.Workplane("XY")
    .sphere(ball_radius)
    )
ball_slice = (
    cq.Workplane("XY")
    .box(cell_size_x, cell_size_y, cell_thickness)
    .faces(">Z")
    .workplane()
    .hole(fastener_diameter)
    .faces().chamfer(block_edge_bevel)
    )
ball = ball.intersect(ball_slice)
#show_object(ball)

ball_list = list()

current_gap = starting_gap
for cell_y in range(cell_count_y):
    for cell_x in range(cell_count_x):
        center_x = cell_size_x/2 - block_size_x/2 + cell_x * cell_size_x
        center_y = cell_size_y/2 - block_size_y/2 + cell_y * cell_size_y
        ball_list.append(
            ball.translate((center_x, center_y+ball_radius/2,0))
            )
        block = block - (
            cq.Workplane("XY")
            .transformed(offset = cq.Vector(center_x, center_y+ball_radius/2))
            .sphere(ball_radius + current_gap)
            )
        if print_text_labels:
            texts.append(
                cq.Workplane("XY")
                .transformed(
                    offset = cq.Vector(
                        center_x,
                        center_y-(cell_size_y/2)+block_edge_bevel*2,
                        block_size_z/2)
                    )
                .text("{:.2f}".format(current_gap),
                      fontsize=4, kind="bold",
                      valign="bottom", distance=0.2, combine=False)
            )

        current_gap = current_gap + gap_increment

block = block.faces().chamfer(block_edge_bevel)

ball_array = None
for ball in ball_list:
    if ball_array is None:
        ball_array = ball
    else:
        ball_array = ball_array + ball

show_object(ball_array, options = {"alpha":0.5, "color":"green"})

assembly = block

if print_text_labels:
    for text in texts:
        assembly = assembly + text

show_object(assembly, options = {"alpha":0.5, "color":"red"})
