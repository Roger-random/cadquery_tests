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
3D-printed piece to be tapped and threaded onto the end of a water pipe to
redirect flow. An experiment to see whether 3D-printed shapes can be used to
obtain fine control. Original motivation is wondering if 3D-printed shape can
create and control laminar flow or if print layer lines would add turbulence
and spoil the effect.
"""

import cadquery as cq

def water_nozzle_base(
    length = 95,
    diameter = 70,
    threaded_exterior_size = 40,
    threaded_interior_diameter = 20.75,
    threaded_length = 20,
    unthreaded_interior_diameter = 22.5,
    lip_depth = 4,
    lip_length = 4,
    ):
    threaded_end = (
        cq.Workplane("YZ")
        .circle(threaded_exterior_size/2)
        .circle(threaded_interior_diameter/2)
        .extrude(threaded_length)
    )

    thread_transition_length = unthreaded_interior_diameter - threaded_interior_diameter
    lip_section_length = lip_length*2 + lip_depth
    lip_section = (
        cq.Workplane("YZ")
        .circle(threaded_exterior_size/2 - lip_depth)
        .extrude(-lip_length)
        .faces("<X").workplane()
        .circle(threaded_exterior_size/2 - lip_depth)
        .workplane(offset=lip_depth)
        .circle(threaded_exterior_size/2)
        .loft()
        .faces("<X").workplane()
        .circle(threaded_exterior_size/2)
        .extrude(lip_length)
    )

    base = threaded_end + lip_section

    return base

if 'show_object' in globals():
    show_object(water_nozzle_base(), options={"color":"blue", "alpha":0.5})
