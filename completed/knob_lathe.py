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
Visual aid for discussing a possible sequence of operations to create a knob
(with indents for fingers) on a lathe
"""


import cadquery as cq

step_offset = 80

stock = cq.Workplane("YZ").circle(40).extrude(30)

show_object(stock, options={"color": "red", "alpha": 0.5})

drill = (
    cq.Workplane("YZ").transformed(offset=cq.Vector(0, 32, -2)).circle(5).extrude(35)
)

drilled = stock
for d in range(8):
    drilled = drilled - drill.rotate((0, 0, 0), (1, 0, 0), (360 / 8) * d)
drilled = drilled.translate((step_offset, 0, 0))

show_object(drilled, options={"color": "orange", "alpha": 0.5})

centered = drilled.faces("<X").workplane().circle(10).extrude(-20, combine="cut")
centered = centered.translate((step_offset, 0, 0))

show_object(centered, options={"color": "yellow", "alpha": 0.5})

stemmed = (
    centered.faces("<X")
    .workplane()
    .circle(40)
    .circle(20)
    .extrude(-15, combine="cut")
    .translate((step_offset * 0.8, 0, 0))
)

show_object(stemmed, options={"color": "green", "alpha": 0.5})


indented = (
    stemmed.faces(">X")
    .workplane()
    .circle(50)
    .circle(30)
    .extrude(-40, combine="cut")
    .translate((step_offset * 0.8, 0, 0))
)

show_object(indented, options={"color": "blue", "alpha": 0.5})
