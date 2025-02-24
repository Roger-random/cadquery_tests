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

def water_nozzle(
    threaded_exterior_size = 30,
    threaded_interior_diameter = 20.5,
    threaded_length = 20,
    ):
    nozzle = (
        cq.Workplane("XZ")
        .rect(threaded_exterior_size, threaded_exterior_size)
        .circle(threaded_interior_diameter/2)
        .extrude(threaded_length)
    )

    elbow = (
        cq.Workplane("XZ")
        .rect(threaded_exterior_size, threaded_exterior_size)
        .circle(threaded_interior_diameter/2)
        .revolve(90,
                 (threaded_exterior_size, -threaded_exterior_size * 0.6, 0),
                 (-threaded_exterior_size, -threaded_exterior_size * 0.6, 0))
    )

    nozzle = nozzle + elbow

    return nozzle + elbow

if 'show_object' in globals():
    show_object(water_nozzle(), options={"color":"blue", "alpha":0.5})
