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
            bearing_diameter_outer=22,
            bearing_diameter_inner=8,
            bearing_length=7,
        )

    def __init__(
        self,
        bearing_diameter_outer,
        bearing_diameter_inner,
        bearing_length,
    ):
        self.bearing_diameter_outer = bearing_diameter_outer
        self.bearing_diameter_inner = bearing_diameter_inner
        self.bearing_length = bearing_length

    def placeholder(self):
        return (
            cq.Workplane("YZ")
            .circle(self.bearing_diameter_outer / 2)
            .circle(self.bearing_diameter_inner / 2)
            .extrude(self.bearing_length)
            .translate((-self.bearing_length / 2, 0, 0))
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
            spool_diameter=200,
            spool_width=72.5,
            spool_side_thickness=5,
            center_diameter=55,
        )

    @staticmethod
    def preset_mhbuild():
        """
        Create an instance with dimensions of MatterhHackers Build
        """
        return spool(
            spool_diameter=200,
            spool_width=67.5,
            spool_side_thickness=5,
            center_diameter=55,
        )

    def __init__(
        self,
        spool_diameter,
        spool_width,
        spool_side_thickness,
        center_diameter,
    ):
        self.spool_diameter = spool_diameter
        self.spool_width = spool_width
        self.spool_side_thickness = spool_side_thickness
        self.center_diameter = center_diameter

    def placeholder(self):
        """
        Generate a shape centered around origin that is a visual representation
        (not intended for printing) of a filament spool.
        """
        center = (
            cq.Workplane("YZ")
            .circle(self.center_diameter / 2 + self.spool_side_thickness)
            .circle(self.center_diameter / 2)
            .extrude(self.spool_width / 2)
        )

        side = (
            cq.Workplane("YZ")
            .transformed(offset=cq.Vector(0, 0, self.spool_width / 2))
            .circle(self.spool_diameter / 2)
            .circle(self.center_diameter / 2 + self.spool_side_thickness)
            .extrude(-self.spool_side_thickness)
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

    def __init__(self):
        pass


if "show_object" in globals():
    show_object(bearing.preset_608().placeholder())
