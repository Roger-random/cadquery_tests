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

import cadquery as cq
import cadquery.selectors as sel

class water_nozzle:
    """
    3D-printed experiment to see whether 3D-printed shapes can be used to
    control flow of water. Original motivation is wondering if 3D-printed
    shape can create and control laminar flow or if print layer lines would
    add turbulence and spoil laminar flow.
    """

    def __init__(
            self,
            base_diameter = 45,
            inner_diameter = 15,
            lip_size = 4
            ):
        """
        Configure parameters required for all pieces to interlock.

        base_diameter is the outermost diameter for the interlocking section.
        inner_diameter is the water pipe's inner diameter
        lip_size is the base unit for creating cutout for interlocking lip
        """
        self.base_diameter = base_diameter
        self.inner_diameter = inner_diameter
        self.lip_size = lip_size

    def base(
            self,
            length = 95,
            flare_diameter = 70,
            threaded_interior_diameter = 20.75,
            threaded_length = 20,
            shell_thickness = 1.6,
            ):
        """
        Base piece to be tapped and threaded onto the end of a water pipe. The
        flared end rests against the tile wall, the other end has the
        interlocking lip mechanism
        """
        threaded_end = (
            cq.Workplane("YZ")
            .circle(self.base_diameter/2)
            .circle(threaded_interior_diameter/2)
            .extrude(-threaded_length)
        )

        flared_end = (
            cq.Workplane("XZ")
            .lineTo(-threaded_length, self.base_diameter/2, forConstruction=True)
            .bezier(
                (
                    (-threaded_length, self.base_diameter/2),
                    (-threaded_length*3, self.base_diameter/2),
                    (-length+5, flare_diameter/2 - 5),
                    (-length, flare_diameter/2)
                )
            )
            .lineTo(-length, flare_diameter/2 - shell_thickness)
            .bezier(
                (
                    (-length, flare_diameter/2 - shell_thickness),
                    (-length+ 5, flare_diameter/2 - 5 - shell_thickness),
                    (-threaded_length*3, self.base_diameter/2 - shell_thickness),
                    (-threaded_length, self.base_diameter/2 - shell_thickness),
                    (-threaded_length, threaded_interior_diameter/2)
                )
            )
            .close()
            .revolve(360, (0,0,0),(1,0,0))
        )

        lip_cutout = (
            cq.Workplane("XZ")
            .lineTo(-self.lip_size*2, self.base_diameter/2 - self.lip_size*2, forConstruction=True)
            .line(0,self.lip_size)
            .line(self.lip_size*2, 0)
            .line(0,self.lip_size*2)
            .line(-self.lip_size*6,0)
            .line(self.lip_size*3, -self.lip_size*3)
            .close()
            .revolve(360, (0,0,0),(1,0,0))
        )

        base = threaded_end + flared_end - lip_cutout

        base = base.faces(">X").chamfer(0.5)
        base = base.faces(">X[1]").chamfer(0.5)

        return base

    def filler_ring(self):
        """
        Interlock geometry of the base is a little compromised in order to
        print without supports. This ring fills in the worse cosmetic wedge.
        """
        return (
            cq.Workplane("XZ")
            .lineTo(-self.lip_size*4, self.base_diameter/2, forConstruction=True)
            .line(-self.lip_size,0)
            .line(self.lip_size, -self.lip_size)
            .close()
            .revolve(360, (0,0,0),(1,0,0))
        )

    def mounting_clip(self):
        """
        Each interchangeable interlocking nozzle may have different geometries
        to explore different ideas, but they will all have the same mount to
        attach to the base.
        """
        clip_full = (
            cq.Workplane("XZ")
            .lineTo(0, self.base_diameter/2 - self.lip_size, forConstruction=True)
            .line(0, self.lip_size)
            .line(-self.lip_size*4,0)
            .line(0,-self.lip_size)
            .line(self.lip_size, -self.lip_size)
            .line(self.lip_size, 0)
            .line(0, self.lip_size)
            .close()
            .revolve(360, (0,0,0),(1,0,0))
        )

        clip_cut_half = (
            cq.Workplane("XY")
            .line(0, self.base_diameter/2-self.lip_size)
            .line(-self.lip_size*2, 0)
            .line(0, -self.lip_size)
            .line(-self.lip_size, 0)
            .line(-self.lip_size, self.lip_size)
            .lineTo(-self.lip_size*4, 0)
            .close()
            .extrude(-self.base_diameter)
        )

        clip_cut = clip_cut_half + clip_cut_half.mirror("XZ")

        clip = clip_full - clip_cut

        return clip

    def simple_elbow(
            self,
            angle = 75,
            ):
        """
        Simple elbow that most closely approximates the original store bought
        nozzle design. Not exciting, just a starting point to make sure I have
        the basics working.
        """
        elbow = (
            cq.Workplane("YZ")
            .circle(self.base_diameter/2)
            .circle(self.inner_diameter/2)
            .revolve(angle, (0, -self.base_diameter*0.51, 0), (1, -self.base_diameter*0.51, 0))
        )

        elbow = elbow.edges(sel.NearestToPointSelector((0, self.inner_diameter/2,0))).fillet(2)

        return self.mounting_clip()+elbow

    def flattened_oval(
            self,
            ):
        """
        Nozzle that changes from a pipe's circular shape to a very flattened
        oval. Results in a nearly but not completely flat triangular fan of
        water. More water than expected exited at the edges, resulting in
        a "frame" around the flat sheet in the middle.
        """
        outer = (
            cq.Workplane("YZ")
            .circle(self.base_diameter/2)
            .workplane()
            .transformed(
                offset=cq.Vector(0,-12,20),
                rotate=cq.Vector(40,0,0))
            .ellipse(self.base_diameter/1.5, self.base_diameter/2.5)
            .workplane()
            .transformed(
                offset=cq.Vector(0,-20,30),
                rotate=cq.Vector(40,0,0))
            .ellipse(self.base_diameter, self.base_diameter/8)
            .loft()
        )

        inner = (
            cq.Workplane("YZ")
            .circle(self.inner_diameter/2)
            .workplane()
            .transformed(
                offset=cq.Vector(0,-12,20),
                rotate=cq.Vector(40,0,0))
            .ellipse(self.inner_diameter*1.6, self.inner_diameter/2.5)
            .workplane()
            .transformed(
                offset=cq.Vector(0,-21,31),
                rotate=cq.Vector(40,0,0))
            .ellipse(self.base_diameter-2, self.base_diameter/8-2)
            .loft()
        )

        nozzle = outer - inner

        return self.mounting_clip()+nozzle

if 'show_object' in globals():
    nozzle = water_nozzle()
    show_object(nozzle.base(), options={"color":"blue", "alpha":0.5})
    show_object(nozzle.filler_ring(), options={"color":"green", "alpha":0.5})
    #show_object(nozzle.simple_elbow(), options={"color":"red", "alpha":0.5})
    show_object(nozzle.flattened_oval(), options={"color":"red", "alpha":0.5})
