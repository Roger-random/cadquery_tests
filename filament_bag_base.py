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

# When not running in CQ-Editor, turn log into print
if "log" not in globals():

    def log(*args):
        print(args)


class bearing:
    """
    Placeholder for a bearing for the purpose of design layout and
    visualization. No need to print this - use real bearings!
    """

    @staticmethod
    def preset_608():
        """
        Create an instance with dimensions of generic 608 bearings
        """
        return bearing(
            diameter_outer=22,
            diameter_inner=8,
            width=7,
        )

    def __init__(
        self,
        diameter_outer,
        diameter_inner,
        width,
    ):
        self.diameter_outer = diameter_outer
        self.diameter_inner = diameter_inner
        self.width = width

    def placeholder(self):
        return (
            cq.Workplane("YZ")
            .circle(self.diameter_outer / 2)
            .circle(self.diameter_inner / 2)
            .extrude(self.width)
            .translate((-self.width / 2, 0, 0))
        )


class spool:
    """
    Placeholder for a filament spool for the purpose of design layout and
    visualization. No need to print this - use real spools!
    """

    @staticmethod
    def preset_jesse():
        """
        Create an instance with dimensions of Printed Solid Jesse
        """
        return spool(
            diameter_outer=200,
            diameter_inner=55,
            width=72.5,
            side_thickness=5,
        )

    @staticmethod
    def preset_mhbuild():
        """
        Create an instance with dimensions of MatterhHackers Build
        """
        return spool(
            diameter_outer=200,
            diameter_inner=55,
            width=67.5,
            side_thickness=5,
        )

    @staticmethod
    def preset_esun3kg():
        """
        Create an instance with dimensions of eSun 3kg
        """
        return spool(
            diameter_outer=270,
            diameter_inner=52.5,
            width=100,
            side_thickness=7,
        )

    def __init__(
        self,
        diameter_outer,
        diameter_inner,
        width,
        side_thickness,
    ):
        self.diameter_outer = diameter_outer
        self.width = width
        self.side_thickness = side_thickness
        self.diameter_inner = diameter_inner

    def placeholder(self):
        """
        Generate a shape centered around origin that is a visual representation
        (not intended for printing) of a filament spool.
        """
        center = (
            cq.Workplane("YZ")
            .circle(self.diameter_inner / 2 + self.side_thickness)
            .circle(self.diameter_inner / 2)
            .extrude(self.width / 2)
        )

        side = (
            cq.Workplane("YZ")
            .transformed(offset=cq.Vector(0, 0, self.width / 2))
            .circle(self.diameter_outer / 2)
            .circle(self.diameter_inner / 2 + self.side_thickness)
            .extrude(-self.side_thickness)
        )

        half = center + side

        spool = half + half.mirror("YZ")

        return spool


class filament_bag_base:
    """
    A 3D printed base that serves as a filament dispensing container and can
    become a dry box in conjunction with the bag that the filament came in.
    Put some dessicant on the bottom, put the bag on top, then packing tape
    around the sides to create an airtight(-ish) seal between the bag and the
    base. Assuming the bag is not already torn, becase if it was then the
    filament is starting on the wrong foot for staying dry.
    """

    def __init__(
        self,
        spool: spool,
        bearing: bearing,
        bearing_separation_angle=30,
    ):
        # Given parameters
        self.spool = spool
        self.bearing = bearing
        self.bearing_separation_angle = bearing_separation_angle

        # Values calculated from given parameters
        self.spool_offset_z = self.spool.diameter_outer / 2
        self.spool_offset = (0, 0, self.spool_offset_z)
        self.bearing_distance = (
            self.spool.diameter_outer / 2 + self.bearing.diameter_outer / 2
        )
        self.bearing_offset_x = self.spool.width / 2 - self.spool.side_thickness / 2
        self.bearing_offset_y = (
            math.sin(math.radians(self.bearing_separation_angle))
            * self.bearing_distance
        )
        self.bearing_offset_z = self.spool_offset_z - (
            math.cos(math.radians(self.bearing_separation_angle))
            * self.bearing_distance
        )
        self.bearing_offset = (
            self.bearing_offset_x,
            self.bearing_offset_y,
            self.bearing_offset_z,
        )

    def show_placeholders(
        self,
        show_object_options={"color": "gray", "alpha": 0.8},
    ):
        """
        If running in CQ-Editor, where show_object() is defined in global
        namespace, show all placeholder objects at their appropriate locations
        with the given options. (Default of mostly transparent gray.)

        When not running in CQ-Editor, does nothing and returns to caller.
        """
        if "show_object" in globals():

            show_object(
                self.spool.placeholder().translate(self.spool_offset),
                options=show_object_options,
            )

            positioned_bearing = self.bearing.placeholder().translate(
                self.bearing_offset
            )
            show_object(
                positioned_bearing,
                options=show_object_options,
            )
            show_object(
                positioned_bearing.mirror("XZ"),
                options=show_object_options,
            )
            show_object(
                positioned_bearing.mirror("YZ"),
                options=show_object_options,
            )
            show_object(
                positioned_bearing.mirror("XZ").mirror("YZ"),
                options=show_object_options,
            )


if "show_object" in globals():
    fbb = filament_bag_base(spool.preset_esun3kg(), bearing.preset_608())
    fbb.show_placeholders()
