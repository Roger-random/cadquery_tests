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
3D-printed work holding tool to grasp a cylindrical lathe-turned aluminum
heat sink in a machining vise so I could drill and tap 1/4"-20 threaded
mounting hole.
"""

def led_heat_sink_vise_jaws():
    heat_sink_diameter = 24.5
    heat_sink_length = 25
    jaw_side = 35
    jaw_gap = 2
    jaws = (
        cq.Workplane("YZ")
        .rect(jaw_side, jaw_side)
        .extrude(heat_sink_length/2, both=True)
        .faces(">X").workplane()
        .rect(jaw_gap, jaw_side)
        .cutThruAll()
    )

    heat_sink = (
        cq.Workplane("YZ")
        .circle(heat_sink_diameter/2)
        .extrude(heat_sink_length/2, both=True)
    ).translate((0,0,jaw_side/2 - heat_sink_diameter*0.55))

    tap_hole_offset_from_center = 2.25

    center_hint_hole = (
        cq.Workplane("XY")
        .circle(1.5)
        .extrude(jaw_side)
    ).translate((tap_hole_offset_from_center,0,0))

    center_hint_groove_size = 0.5
    center_hint_groove = (
        cq.Workplane("XZ")
        .lineTo(0,jaw_side/2 - center_hint_groove_size, forConstruction = True)
        .lineTo( center_hint_groove_size, jaw_side/2)
        .lineTo(-center_hint_groove_size, jaw_side/2)
        .close()
        .extrude(jaw_side/2, both=True)
    ).translate((tap_hole_offset_from_center,0,0))

    return jaws - heat_sink - center_hint_hole - center_hint_groove

if show_object:
    show_object(led_heat_sink_vise_jaws(), options={"color":"blue", "alpha":0.5})
