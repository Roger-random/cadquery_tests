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
Generate a small block intended to work as support for 3DPrintMill as
Creality Slicer doesn't seem to be capable of generating supports at 45 degrees.
"""
import math
import cadquery as cq

width = 40
height_diag = 40

height = height_diag/math.sqrt(2)
brim_height = 0.2
brim_width = 2
bridged_thickness = 1.6*math.sqrt(2)
side_thickness = 1.6
support_air_gap = 0.4
support_air_gap_diag = support_air_gap * math.sqrt(2)

support = (
    cq.Workplane("YZ")
    .lineTo(height/2+brim_width, 0)
    .lineTo(height/2+brim_width, brim_height)
    .lineTo(height/2           , brim_height)
    .lineTo(height             , height)
    .lineTo(brim_height        , brim_height)
    .lineTo(-support_air_gap_diag , brim_height)
    .lineTo(-support_air_gap_diag , 0)
    .close()
    .extrude(width/2, both=True)
    )

support_hollow = (
    cq.Workplane("YZ")
    .lineTo(bridged_thickness+brim_height, brim_height, forConstruction = True)
    .lineTo(height, height-bridged_thickness)
    .lineTo(height, brim_height)
    .close()
    .extrude((width/2)-side_thickness, both=True)
    )

#show_object(support_hollow, options = {"alpha":0.5, "color":"red"})

support = support - support_hollow

#show_object(support, options = {"alpha":0.5, "color":"yellow"})

object_x = 40
object_y = 40
object_z = 5
object_fillet = 3
object_chamfer = 1

test_object = (
    cq.Workplane("XY")
    .box(object_x, object_y, object_z)
    .faces(">Z").workplane()
    .hole(object_x/2)
    .edges("|Z").fillet(object_fillet)
    .faces().chamfer(object_chamfer)
    )
test_object = test_object.translate((0,object_y/2-object_chamfer-support_air_gap,object_z/2+support_air_gap))
test_object = test_object.rotate((0,0,0),(1,0,0),45)
show_object(test_object)

assembly = support + test_object

show_object(assembly)