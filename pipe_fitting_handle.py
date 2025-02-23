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
3D-printed handle to get a grip on a pipe fitting.

Tried thread code from https://github.com/CadQuery/cadquery-contrib/blob/master/examples/Thread.py
but it failed at height beyond 7mm and I needed more than that.

So this just prints a cylinder and I'll cut my pipe thread with a tap.
"""

import cadquery as cq
from cadquery import *
from math import *


"""
From https://github.com/CadQuery/cadquery-contrib/blob/master/examples/Thread.py

def helix(r0,r_eps,p,h,d=0,frac=1e-1):

    def func(t):

        if t>frac and t<1-frac:
            z = h*t + d
            r = r0+r_eps
        elif t<=frac:
            z = h*t + d*sin(pi/2 *t/frac)
            r = r0 + r_eps*sin(pi/2 *t/frac)
        else:
            z = h*t - d*sin(2*pi - pi/2*(1-t)/frac)
            r = r0 - r_eps*sin(2*pi - pi/2*(1-t)/frac)

        x = r*sin(-2*pi/(p/h)*t)
        y = r*cos(2*pi/(p/h)*t)

        return x,y,z

    return func

def thread(radius, pitch, height, d, radius_eps, aspect= 10):

    e1_bottom = (cq.Workplane("XY")
        .parametricCurve(helix(radius,0,pitch,height,-d)).val()
    )
    e1_top = (cq.Workplane("XY")
        .parametricCurve(helix(radius,0,pitch,height,d)).val()
    )

    e2_bottom = (cq.Workplane("XY")
        .parametricCurve(helix(radius,radius_eps,pitch,height,-d/aspect)).val()
    )
    e2_top = (cq.Workplane("XY")
        .parametricCurve(helix(radius,radius_eps,pitch,height,d/aspect)).val()
    )

    f1 = Face.makeRuledSurface(e1_bottom, e1_top)
    f2 = Face.makeRuledSurface(e2_bottom, e2_top)
    f3 = Face.makeRuledSurface(e1_bottom, e2_bottom)
    f4 = Face.makeRuledSurface(e1_top, e2_top)

    sh = Shell.makeShell([f1,f2,f3,f4])
    rv = Solid.makeSolid(sh)

    return rv

radius = 4
pitch = 2
height = 12
d = pitch/4
radius_eps = 0.5
eps=1e-3

core = cq.Workplane("XY",origin=(0,0,-d)).circle(4).circle(3).extrude(height+1.75*d)
th1 = thread(radius-eps,pitch,height,d,radius_eps)
th2  =thread(radius-1+eps,pitch,height,d,-radius_eps)

res = core.union(Compound.makeCompound([th1,th2]))

show_object(res)
"""

def pipe_fitting_handle(
    length_half = 50,
    width_half = 15,
    height = 15,
    hole_diameter = 12.8,
    corner_fillet = 10,
    face_chamfer = 1,
    ):

    quarter = (
        cq.Workplane("XY")
        .lineTo(0,length_half)
        .lineTo(width_half,0)
        .close()
        .extrude(height)
    )

    handle = quarter + quarter.mirror("YZ")
    handle = handle + handle.mirror("XZ")
    handle = handle.edges("|Z").fillet(corner_fillet)

    handle = (
        handle.faces("<Z").workplane()
        .circle(hole_diameter/2)
        .extrude(-height, combine='cut')
    )

    handle = handle.faces("<Z").chamfer(face_chamfer)
    handle = handle.faces(">Z").chamfer(face_chamfer)

    return handle

if 'show_object' in globals():
    show_object(pipe_fitting_handle(), options={"color":"blue", "alpha":0.5})
