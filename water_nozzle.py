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
import cadquery.selectors as sel

def water_nozzle_base(
    length = 95,
    diameter = 70,
    threaded_exterior_size = 45,
    threaded_interior_diameter = 20.75,
    threaded_length = 20,
    shell_thickness = 1.6,
    lip_size = 4,
    ):
    threaded_end = (
        cq.Workplane("YZ")
        .circle(threaded_exterior_size/2)
        .circle(threaded_interior_diameter/2)
        .extrude(-threaded_length)
    )

    flared_end = (
        cq.Workplane("XZ")
        .lineTo(-threaded_length, threaded_exterior_size/2, forConstruction=True)
        .bezier(
            (
                (-threaded_length, threaded_exterior_size/2),
                (-threaded_length*3, threaded_exterior_size/2),
                (-length+5, diameter/2 - 5),
                (-length, diameter/2)
            )
        )
        .lineTo(-length, diameter/2 - shell_thickness)
        .bezier(
            (
                (-length, diameter/2 - shell_thickness),
                (-length+ 5, diameter/2 - 5 - shell_thickness),
                (-threaded_length*3, threaded_exterior_size/2 - shell_thickness),
                (-threaded_length, threaded_exterior_size/2 - shell_thickness),
                (-threaded_length, threaded_interior_diameter/2)
            )
        )
        .close()
        .revolve(360, (0,0,0),(1,0,0))
    )

    lip_cutout = (
        cq.Workplane("XZ")
        .lineTo(-lip_size*2, threaded_exterior_size/2 - lip_size*2, forConstruction=True)
        .line(0,lip_size)
        .line(lip_size*2, 0)
        .line(0,lip_size*2)
        .line(-lip_size*6,0)
        .line(lip_size*3, -lip_size*3)
        .close()
        .revolve(360, (0,0,0),(1,0,0))
    )

    base = threaded_end + flared_end - lip_cutout

    base = base.faces(">X").chamfer(0.5)
    base = base.faces(">X[1]").chamfer(0.5)

    return base

def mounting_clip(
    base_diameter = 45,
    lip_size = 4,
    ):
    clip_full = (
        cq.Workplane("XZ")
        .lineTo(0, base_diameter/2 - lip_size, forConstruction=True)
        .line(0, lip_size)
        .line(-lip_size*4,0)
        .line(0,-lip_size)
        .line(lip_size, -lip_size)
        .line(lip_size, 0)
        .line(0, lip_size)
        .close()
        .revolve(360, (0,0,0),(1,0,0))
    )

    clip_cut_half = (
        cq.Workplane("XY")
        .line(0, base_diameter/2-lip_size)
        .line(-lip_size*2, 0)
        .line(0, -lip_size)
        .line(-lip_size, 0)
        .line(-lip_size, lip_size)
        .lineTo(-lip_size*4, 0)
        .close()
        .extrude(-base_diameter)
    )

    clip_cut = clip_cut_half + clip_cut_half.mirror("XZ")

    clip = clip_full - clip_cut

    clip = clip.edges("<Z").fillet(2)

    return clip

def filler_ring(
    base_diameter = 45,
    lip_size = 4,
    ):
    return (
        cq.Workplane("XZ")
        .lineTo(-lip_size*4, base_diameter/2, forConstruction=True)
        .line(-lip_size,0)
        .line(lip_size, -lip_size)
        .close()
        .revolve(360, (0,0,0),(1,0,0))
    )

def simple_elbow(
    base_diameter = 45,
    inner_diameter = 15,
    angle = 75,
    ):

    elbow = (
        cq.Workplane("YZ")
        .circle(base_diameter/2)
        .circle(inner_diameter/2)
        .revolve(angle, (0, -base_diameter*0.51, 0), (1, -base_diameter*0.51, 0))
    )

    elbow = elbow.edges(sel.NearestToPointSelector((0, inner_diameter/2,0))).fillet(2)

    return mounting_clip()+elbow

if 'show_object' in globals():
    show_object(water_nozzle_base(), options={"color":"blue", "alpha":0.5})
    show_object(filler_ring(), options={"color":"green", "alpha":0.5})
    show_object(simple_elbow(), options={"color":"red", "alpha":0.5})
