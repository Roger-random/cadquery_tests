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

class filament_dry_box:
    """
    3D-printed filaments tend to pick up moisture to varying degrees (depending
    on chemical formulation) and that moisture interferes with the process of
    printing. Sometimes the interference is negligible and can be safely
    ignored but not always. There are lots of solutions floating around the
    internet for keeping filament dry. Here is my take building something
    tailored to my personal preferences.
    """
    def __init__(
            self,
            spool_diameter = 200,
            spool_diameter_margin = 3,
            spool_width = 40,
            spool_width_margin = 3,
            shell_thickness = 1.6,
            shell_bottom_radius = 10,
            bottom_extra_height = 20,
            ):
        self.spool_diameter = spool_diameter
        self.spool_volume_radius = spool_diameter/2 + spool_diameter_margin
        self.spool_width = spool_width
        self.spool_volume_width = spool_width/2 + spool_width_margin
        self.shell_thickness = shell_thickness
        self.shell_bottom_radius = shell_bottom_radius
        self.bottom_extra_height = bottom_extra_height

    def spool_placeholder(
            self,
            spool_side_thickness = 5):
        """
        Generate a shape centered around origin that is a visual representation
        (not intended for printing) of the filament spool we want to enclose.
        """
        center = (
            cq.Workplane("YZ")
            .circle(self.spool_diameter/4)
            .circle(self.spool_diameter/4 - spool_side_thickness)
            .extrude(self.spool_width/2)
        )

        side = (
            cq.Workplane("YZ")
            .transformed(offset=cq.Vector(0,0,self.spool_width/2))
            .circle(self.spool_diameter/2)
            .circle(self.spool_diameter/4 - spool_side_thickness)
            .extrude(-spool_side_thickness)
        )

        half = center + side

        spool = half + half.mirror("YZ")

        return spool

    def box_perimeter_path(self):
        """
        Path describing the shape of enclosed volume. Used to sweep the outer
        perimeter as well as generating the flat side panels.
        """
        return (
            cq.Workplane("YZ")
            .lineTo(
                0,
                self.spool_volume_radius,
                forConstruction=True )
            .radiusArc((self.spool_volume_radius,0), self.spool_volume_radius)
            .line(0, self.shell_bottom_radius-self.spool_volume_radius-self.bottom_extra_height)
            .radiusArc((
                self.spool_volume_radius - self.shell_bottom_radius,
                -self.spool_volume_radius - self.bottom_extra_height
                ), self.shell_bottom_radius)
            .line(-self.spool_volume_radius+self.shell_bottom_radius, 0)
        )

    def box_side(
            self,
            ):
        """
        Use perimeter path to generate a simple flat side panel.
        """
        return (
            self.box_perimeter_path()
            .close()
            .extrude(self.shell_thickness)
        ).translate((self.spool_volume_width,0,0))

    def box_perimeter(
            self,
            ):
        """
        Draw profile of perimeter all around the box, then sweep it along pereimeter path.
        """
        profile = (
            cq.Workplane("XZ")
            .lineTo(self.spool_volume_width,
                self.spool_volume_radius,
                forConstruction=True )
            .line(-self.spool_volume_width, 0)
            .line(0, self.shell_thickness)
            .line(self.spool_volume_width, 0)
            .line(self.shell_thickness, -self.shell_thickness)
            .close()
        )

        return profile.sweep(self.box_perimeter_path())

if 'show_object' in globals():
    box = filament_dry_box()
    show_object(box.spool_placeholder(), options={"color":"black", "alpha":0.75})
    tray = box.box_perimeter()+box.box_side()
    tray = tray + tray.mirror("XZ")
    tray = tray - (
        cq.Workplane("YZ")
        .circle(box.spool_volume_radius - 10)
        .extrude(box.spool_volume_radius)
    )
    show_object(tray, options={"color":"blue", "alpha":0.5})
    #show_object(box.box_side(), options={"color":"red", "alpha":0.5})
