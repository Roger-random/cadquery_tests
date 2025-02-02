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
Minimal cover over a HalloWing M0 screen. Not really for protection  but to
hold it together. The screen is only held together by double-sided tape and
that tape has started failing due to age and the screen falling apart.
"""
import cadquery as cq

mm_per_inch = 25.4

fastener_distance_x = 0.7 * mm_per_inch
fastener_distance_y = 1.8 * mm_per_inch
fastener_border = 8
fastener_length = 5
nut_depth = 2.5

screen_outer_x = 30.5
screen_outer_y = 35 # Don't fit tightly to this dimension: FPC on top
screen_outer_z = 4.5

screen_visible_x = 26
screen_visible_y = 26
screen_visible_offset_x = 0
screen_visible_offset_y = -1

screen_center_offset_x = 0
screen_center_offset_y = -0.5
screen_border = 1.6
screen_opening_tolerance = 1

fastener_frame = (
    cq.Workplane("XY")
    .box(fastener_distance_x + fastener_border,
         fastener_distance_y + fastener_border,
         fastener_length
         )
    )

# Exterior of screen frame
screen_frame = (
    cq.Workplane("XY")
    .box(screen_outer_x + screen_opening_tolerance + screen_border,
         screen_outer_y + screen_opening_tolerance + screen_border,
         fastener_length
         )
    .translate((screen_center_offset_x, screen_center_offset_y, 0))
    )

# Combine exterior of frames
fastener_frame = fastener_frame + screen_frame

# Smooth out corners
fastener_frame = fastener_frame.edges("|Z").fillet(1)

# Holes for M2.5 fasteners
fastener_frame = (
    fastener_frame.faces("<Z")
    .workplane()
    .rect(fastener_distance_x, fastener_distance_y, forConstruction=True)
    .vertices()
    .circle(2.7/2)
    .extrude(-(fastener_length - nut_depth - 0.2),combine='cut')
    )

# Capture M2.5 nuts
fastener_frame = (
    fastener_frame.faces(">Z")
    .workplane()
    .rect(fastener_distance_x, fastener_distance_y, forConstruction=True)
    .vertices()
    .polygon(6, 6.0)
    .extrude(-nut_depth, combine='cut')
    )

# Cut out space for screen
fastener_frame = (
    fastener_frame.faces("<Z").workplane()
    .transformed(offset=cq.Vector(
        screen_center_offset_x,
        -screen_center_offset_y, # Is Y coordinates reversed because of <Z face?
        0))
    .rect(
        screen_outer_x + screen_opening_tolerance,
        screen_outer_y + screen_opening_tolerance,
        )
    .extrude(-screen_outer_z, combine='cut')
    )

# Cut screen opening
fastener_frame = (
    fastener_frame.faces(">Z").workplane()
    .transformed(offset=cq.Vector(
        screen_visible_offset_x,
        screen_visible_offset_y,
        0))
    .rect(
        screen_visible_x + screen_opening_tolerance,
        screen_visible_y + screen_opening_tolerance
        )
    .extrude(-fastener_length, combine='cut')
    )

# Flip over for printing
fastener_frame = fastener_frame.rotate((0,0,0),(0,1,0),180)

show_object(fastener_frame)
