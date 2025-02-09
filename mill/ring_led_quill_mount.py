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
Attach a ring LED circuit board (external diameter 120mm) to the quill of a
Bridgeport knee mill (external diameter 3.375" or 85.725mm)
"""

import math
import cadquery as cq

def ring_led_quill_mount(
        lip_depth = 1,
        lip_height = 0.4
        ):
    ring_led_thickness = 1.62
    ring_led_radius = 120/2
    ring_clip_thickness = 1.6
    quill_radius = 85.725/2
    quill_clamp_height = 5
    quill_clamp_thickness = 3.2

    radius_diff = ring_led_radius - quill_radius

    tab_length = 10

    cone_height = lip_height + ring_led_thickness + radius_diff + quill_clamp_height

    cone = (
        cq.Workplane("YZ")
        .lineTo( ring_led_radius-lip_depth, 0, forConstruction = True)
        .lineTo( ring_led_radius-lip_depth, lip_height)
        .lineTo( ring_led_radius          , lip_height)
        .lineTo( ring_led_radius          , lip_height + ring_led_thickness)
        .lineTo( quill_radius             , cone_height - quill_clamp_height)
        .lineTo( quill_radius             , cone_height)
        .lineTo( quill_radius + quill_clamp_thickness, cone_height)
        .lineTo( quill_radius + quill_clamp_thickness, cone_height - quill_clamp_height)
        .lineTo( ring_led_radius + ring_clip_thickness, lip_height + ring_led_thickness)
        .lineTo( ring_led_radius + ring_clip_thickness, 0)
        .close()
        .revolve(360, (0,0,0), (0,1,0))
    )

    tab_wedge = (
        cq.Workplane("YZ")
        .lineTo( ring_led_radius          , lip_height + ring_led_thickness, forConstruction = True)
        .lineTo( quill_radius             , cone_height - quill_clamp_height)
        .lineTo( quill_radius             , cone_height)
        .lineTo( quill_radius + tab_length, cone_height)
        .lineTo( quill_radius + tab_length, cone_height - quill_clamp_height)
        .lineTo( ring_led_radius + ring_clip_thickness, lip_height + ring_led_thickness)
        .close()
        .revolve(180, (0,0,0), (0,1,0))
    )

    slot_size = 4
    tab_thickness = slot_size + 8
    tab_intersect = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector((-ring_led_radius, 0, 0)))
        .rect(ring_led_radius*2, tab_thickness)
        .extrude(cone_height)
    )
    tab_fastener = (
        cq.Workplane("XZ")
        .transformed(offset=cq.Vector((3 -quill_radius - tab_length, cone_height - 3, 0)))
        .circle(3.5/2)
        .extrude(tab_thickness, both=True)
    )
    tab = tab_wedge.intersect(tab_intersect) - tab_fastener

    slot = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector((-ring_led_radius, 0, 0)))
        .rect(ring_led_radius*2, slot_size)
        .extrude(cone_height)
    )

    mount = cone + tab - slot

    return mount

if show_object:
    show_object(ring_led_quill_mount(), options={"color":"blue", "alpha":0.5})
