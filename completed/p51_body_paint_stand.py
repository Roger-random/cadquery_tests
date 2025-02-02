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
Adapts an eSun 3KG filament spool to the body engine mount of 3DLabPrint
P-51 Mustang for purpose of holding the body vertical for spray painting.
"""
import cadquery as cq

engine_mount_radius = 35
intermediate_radius = 38
spool_center_radius = 26.25

end_chamfer = 1

paint_stand = (
    cq.Workplane("XY")
    .circle(engine_mount_radius)
    .extrude(60)
    .faces(">Z").workplane()
    .circle(engine_mount_radius)
    .workplane(offset=intermediate_radius-engine_mount_radius)
    .circle(intermediate_radius)
    .loft()
    .faces(">Z").workplane()
    .circle(intermediate_radius)
    .extrude(15)
    .faces(">Z").workplane()
    .circle(intermediate_radius)
    .workplane(offset=intermediate_radius-spool_center_radius)
    .circle(spool_center_radius)
    .loft()
    .faces(">Z").workplane()
    .circle(spool_center_radius)
    .extrude(80)
    .faces(">Z")
    .chamfer(end_chamfer)
    .faces("<Z")
    .chamfer(end_chamfer)
    )

show_object(paint_stand)