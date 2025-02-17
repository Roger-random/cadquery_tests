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
3D-printed mount to fit on the dovetail of a Monoprice tripod
"""

import cadquery as cq
import cadquery.selectors as sel

def tripod_dovetail(
    dovetail_height = 6.25,
    dovetail_length = 42.4,
    dovetail_bottom_fillet = 2.5,
    dovetail_bottom_width = 38.7,
    dovetail_top_width = 32.15,
    ):
    dovetail_half = (
        cq.Workplane("XZ")
        .lineTo(dovetail_top_width/2, 0)
        .lineTo(dovetail_bottom_width/2, -dovetail_height)
        .lineTo(0, -dovetail_height)
        .close()
        .extrude(dovetail_length/2, both=True)
    ).edges(">X").fillet(dovetail_bottom_fillet)

    dovetail = dovetail_half + dovetail_half.mirror("YZ")

    return dovetail

def tripod_dovetail_test_block(
    top_lip_height = 1.8,
    top_lip_length = 50,
    top_lip_width = 45,
    ):
    top_lip_half = (
        cq.Workplane("XZ")
        .lineTo(top_lip_width/2, 0)
        .line(0, top_lip_height)
        .line(-top_lip_width/2, 0)
        .close()
        .extrude(top_lip_length/2, both=True)
    )

    top_lip_half = top_lip_half + top_lip_half.mirror("YZ")

    top_lip_half = top_lip_half.edges("|Z").fillet(5)

    return top_lip_half + tripod_dovetail()

def tripod_mount(
    dovetail_lip_length = 50,
    dovetail_lip_width = 45,
    wedge_angle = 45,
    wedge_height = 50,
    wedge_width = 95,
    wedge_length = 120,
    fastener_distance = 30,
    fastener_distance_step = 20,
    fastener_major_diameter_clear = 6.6,
    brace_corner_fillet = 2,
    brace_thickness = 5,
    brace_leg_length = 40,
    brace_leg_width = 140,
    ):

    wedge_block = (
        cq.Workplane("XY")
        .rect(dovetail_lip_width, dovetail_lip_length)
        .workplane(offset=wedge_height)
        .transformed(rotate=cq.Vector(wedge_angle,0,0))
        .rect(wedge_width, wedge_length)
        .loft()
    )

    # There might be a more elegant way to select the wedge edges I need to
    # fillet but they are not parallel to any axis so the string-based
    # ("<Y", "|Y") selectors don't work.
    wedge_block = (
        wedge_block
        .edges(sel.NearestToPointSelector((
             dovetail_lip_width,  dovetail_lip_length,wedge_height*0.1))).fillet(5)
        .edges(sel.NearestToPointSelector((
            -dovetail_lip_width,  dovetail_lip_length,wedge_height*0.1))).fillet(5)
        .edges(sel.NearestToPointSelector((
             dovetail_lip_width, -dovetail_lip_length,wedge_height*0.1))).fillet(5)
        .edges(sel.NearestToPointSelector((
            -dovetail_lip_width, -dovetail_lip_length,wedge_height*0.1))).fillet(5)
    )

    wedge_rail = (
        cq.Workplane("YZ")
        .lineTo(wedge_length/2, 0, forConstruction=True)
        .line(-brace_leg_length,0)
        .line(0,-brace_thickness)
        .line(brace_leg_length - brace_thickness, 0)
        .line(0, brace_thickness - brace_leg_length)
        .line(brace_thickness, 0)
        .close()
        .extrude(brace_leg_width/2, both=True)
    ).edges("|Z").fillet(brace_thickness*0.4)

    wedge_rail = (
        wedge_rail
        .rotate((0,0,0),(1,0,0),wedge_angle)
        .translate((0,0,wedge_height))
    )

    tripod_mount = (
        wedge_block
        + wedge_rail
        + tripod_dovetail()
    )

    return tripod_mount

if 'show_object' in globals():
    show_object(tripod_mount(), options={"color":"blue", "alpha":0.5})
