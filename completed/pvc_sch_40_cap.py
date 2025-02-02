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
Vase-mode print for a minimalist cap over ends of Schedule 40 PVC pipe with
~1.315" or 33.4mm external diameter.
"""
import cadquery as cq

nozzle_diameter = 0.4

circular_radius = nozzle_diameter + 33.5/2

polygon_diameter = 33 + nozzle_diameter * 2

polygon_sides = 18

cap = (
    cq.Workplane("XY")
    .circle(circular_radius)
    .extrude(5)
    .faces("<Z").chamfer(0.5)
    .faces(">Z").workplane()
    .circle(circular_radius)
    .workplane(offset=10)
    .polygon(polygon_sides, polygon_diameter, circumscribed=True)
    .loft()
    .faces(">Z").workplane()
    .polygon(polygon_sides, polygon_diameter, circumscribed=True)
    .extrude(10)
    .faces(">Z").workplane()
    .polygon(polygon_sides, polygon_diameter, circumscribed=True)
    .workplane(offset=3)
    .circle(circular_radius+0.5)
    .loft()
    )