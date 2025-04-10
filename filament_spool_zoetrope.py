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

import math
import cadquery as cq
import cadquery.selectors as sel
from cadquery import exporters
from placeholders import bearing, spool

# When not running in CQ-Editor, turn log into print
if "log" not in globals():

    def log(*args):
        print(args)


# When not running in CQ-Editor, turn show_object into no-op
if "show_object" not in globals():

    def show_object(*args):
        pass


class zoetrope:
    """
    A set of 3D printed objects that turn a spent spool of 3D printing filament
    into the core of a zoetrope for showing short animation.
    """

    def __init__(
        self,
        spool=spool.preset_mhbuild(),
        bearing=bearing.preset_608(),
        spool_spindle_thickness=1.2,
        spool_spindle_lip_depth=2.4,
    ):
        self.spool = spool
        self.bearing = bearing
        self.spool_spindle_thickness = spool_spindle_thickness
        self.spool_spindle_lip_depth = spool_spindle_lip_depth

    def bearing_offset(self):
        """
        Returns a tuple of 3 numbers representing the X/Y/Z offset for calling
        bearing.placeholder().translate()
        """
        return (
            self.spool.width_inner / 2
            - self.bearing.width / 2
            + self.spool_spindle_thickness,
            0,
            0,
        )

    def spool_spindle(self):
        """
        Returns a CadQuery object that fits in the center of a spent spool and
        supports a bearing.
        """
        lip = (
            cq.Workplane("YZ")
            .circle(self.spool.diameter_inner / 2 + self.spool_spindle_lip_depth)
            .extrude(self.spool_spindle_thickness)
        )

        body = (
            cq.Workplane("YZ")
            .circle(self.spool.diameter_inner / 2)
            .extrude(-self.spool_spindle_thickness)
        )

        bearing_support = (
            cq.Workplane("YZ")
            .circle(self.bearing.diameter_outer / 2 + self.spool_spindle_lip_depth)
            .extrude(-self.bearing.width)
        )

        bearing_cutout = (
            cq.Workplane("YZ")
            .transformed(offset=cq.Vector(0, 0, self.spool_spindle_thickness + 1))
            .circle(self.bearing.diameter_outer / 2)
            .extrude(-self.bearing.width - 1)
            .faces("<X")
            .workplane()
            .circle(self.bearing.diameter_outer / 2)
            .workplane(offset=self.spool_spindle_thickness)
            .circle(self.bearing.diameter_outer / 2 - self.spool_spindle_thickness)
            .loft()
        )

        return (lip + body + bearing_support - bearing_cutout).translate(
            (self.spool.width_inner / 2, 0, 0)
        )

    def bearing_shim(self):
        """
        Small cylinder that shims between the center of 608 bearings (8mm) and
        a 1/4"-20 threaded rod (Just under 6mm)
        """
        return (
            cq.Workplane("YZ")
            .circle(self.bearing.diameter_inner / 2)
            .circle(3.1)
            .extrude(self.bearing.width / 2, both=True)
        )

    def spool_center_spacer(self):
        """
        Cylinder that blocks out space between two bearings. Necessary to prevent
        bearings from seizing up when we tighten the fastening nuts.
        """
        return (
            cq.Workplane("YZ")
            .circle(self.bearing.diameter_inner / 2 + self.spool_spindle_lip_depth)
            .circle(3.1)
            .extrude(
                self.spool.width_inner / 2
                - self.bearing.width
                + self.spool_spindle_thickness,
                both=True,
            )
        )

    def handle_static(self):
        """
        3D object representing the larger handle which stays still relative
        to the spinning motion.
        """
        handle_volume = (
            cq.Workplane("YZ")
            .circle(50)
            .extrude(-5)
            .faces("<X")
            .workplane()
            .circle(50)
            .workplane(offset=10)
            .circle(20)
            .loft()
            .faces("<X")
            .workplane()
            .circle(20)
            .extrude(85)
        )

        handle_intersect = (
            cq.Workplane("YZ").rect(100, 20 / math.sin(math.radians(60))).extrude(-200)
        )

        threaded_rod = cq.Workplane("YZ").circle(3.1).extrude(-200)

        handle = handle_volume.intersect(handle_intersect) - threaded_rod

        handle = handle.translate((-self.spool.width / 2 - self.bearing.width, 0, 0))

        return handle

    def spool_perimeter(
        self,
        panels=16,
    ):
        """
        A cylinder that wraps the outside perimeter of the spool, divided
        into the given number of panels.
        """
        nozzle_diameter = 0.4
        polygon_diameter = self.spool.diameter_outer + nozzle_diameter * 4
        flat_lip = (
            cq.Workplane("YZ")
            .polygon(
                nSides=panels,
                diameter=polygon_diameter,
                circumscribed=True,
            )
            .circle(self.spool.diameter_outer / 2 - self.spool_spindle_lip_depth)
            .extrude(self.spool_spindle_thickness)
        )
        spool_clamp = (
            cq.Workplane("YZ")
            .polygon(
                nSides=panels,
                diameter=polygon_diameter,
                circumscribed=True,
            )
            .circle(self.spool.diameter_outer / 2)
            .extrude(self.spool.side_thickness)
        )
        bevel_lip_outer = (
            cq.Workplane("YZ")
            .polygon(
                nSides=panels,
                diameter=polygon_diameter,
                circumscribed=True,
            )
            .extrude(self.spool_spindle_lip_depth)
        )
        bevel_lip_cutout = (
            cq.Workplane("YZ")
            .circle(self.spool.diameter_outer / 2 - self.spool_spindle_lip_depth)
            .workplane(offset=self.spool_spindle_lip_depth)
            .circle(self.spool.diameter_outer / 2)
            .loft()
        )

        bevel = bevel_lip_outer - bevel_lip_cutout

        perimeter_middle = (
            cq.Workplane("YZ")
            .polygon(
                nSides=panels,
                diameter=polygon_diameter,
                circumscribed=True,
            )
            .polygon(
                nSides=panels,
                diameter=polygon_diameter - nozzle_diameter * 2,
                circumscribed=True,
            )
            .extrude(
                self.spool.width / 2
                - self.spool.side_thickness
                - self.spool_spindle_lip_depth,
                both=True,
            )
        )

        bevel_upper_lip_loft = (
            cq.Workplane("YZ")
            .circle(self.spool.diameter_outer / 2 - self.spool_spindle_lip_depth)
            .workplane(offset=self.spool_spindle_lip_depth * 2)
            .polygon(
                nSides=panels,
                diameter=polygon_diameter - nozzle_diameter * 2,
                circumscribed=True,
            )
            .loft()
        )

        bevel_upper = (
            bevel_lip_outer
            + bevel_lip_outer.translate((self.spool_spindle_lip_depth, 0, 0))
            - bevel_upper_lip_loft
        )

        interrupter_ring = (
            cq.Workplane("YZ")
            .circle(
                self.spool.diameter_outer / 2
                - self.spool_spindle_lip_depth
                + nozzle_diameter
            )
            .circle(self.spool.diameter_outer / 2 - self.spool_spindle_lip_depth)
            .extrude(-8)
        )

        perimeter = (
            flat_lip.translate((self.spool.width / 2, 0, 0))
            + spool_clamp.translate(
                (self.spool.width / 2 - self.spool.side_thickness, 0, 0)
            )
            + bevel.translate(
                (
                    self.spool.width / 2
                    - self.spool.side_thickness
                    - self.spool_spindle_lip_depth,
                    0,
                    0,
                )
            )
            + perimeter_middle
            + bevel_upper.translate(
                (
                    -self.spool.width / 2 + self.spool.side_thickness,
                    0,
                    0,
                )
            )
            + spool_clamp.translate((-self.spool.width / 2, 0, 0))
            + bevel.translate(
                (
                    -self.spool.width / 2 - self.spool_spindle_lip_depth,
                    0,
                    0,
                )
            )
            + interrupter_ring.translate(
                (-self.spool.width / 2 - self.spool_spindle_lip_depth, 0, 0)
            )
        )

        perimeter = perimeter.rotate((0, 0, 0), (1, 0, 0), 180 / panels)

        slitter = (
            cq.Workplane("YZ")
            .line(self.spool.diameter_outer, 0)
            .line(0, 0.1)
            .line(-self.spool.diameter_outer, 0)
            .close()
            .extrude(self.spool.width, both=True)
        )

        perimeter = perimeter - slitter

        perimeter = perimeter.rotate((0, 0, 0), (1, 0, 0), -180 / panels)

        return perimeter


if "show_object" in globals():
    z = zoetrope()

    show_object(
        z.spool.placeholder(),
        options={"color": "white", "alpha": 0.2},
    )
    show_object(
        z.bearing.placeholder().translate(z.bearing_offset()),
        options={"color": "white", "alpha": 0.2},
    )
    show_object(
        z.bearing.placeholder().translate(z.bearing_offset()).mirror("YZ"),
        options={"color": "white", "alpha": 0.2},
    )
    show_object(
        z.spool_spindle(),
        options={"color": "blue", "alpha": 0.5},
    )
    show_object(
        z.spool_spindle().mirror("YZ"),
        options={"color": "blue", "alpha": 0.5},
    )
    show_object(
        z.bearing_shim().translate(z.bearing_offset()),
        options={"color": "green", "alpha": 0.5},
    )
    show_object(
        z.bearing_shim().translate(z.bearing_offset()).mirror("YZ"),
        options={"color": "green", "alpha": 0.5},
    )
    show_object(
        z.spool_center_spacer(),
        options={"color": "red", "alpha": 0.5},
    )
    show_object(
        z.handle_static(),
        options={"color": "purple", "alpha": 0.5},
    )
    show_object(
        z.spool_perimeter(),
        options={"color": "#ABC", "alpha": 0.5},
    )
