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
Collection of CadQuery classes shared across multiple projects
"""
import cadquery as cq


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
            width_inner=72.5,  # Need measurement
            side_thickness=5,
        )

    @staticmethod
    def preset_mhbuild():
        """
        Create an instance with dimensions of MatterhHackers Build
        """
        return spool(
            diameter_outer=200,
            diameter_inner=54.5,
            width=67.5,
            width_inner=60.5,
            side_thickness=4,
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
            width_inner=98.5,
            side_thickness=7,
        )

    def __init__(
        self,
        diameter_outer,
        diameter_inner,
        width,
        width_inner,
        side_thickness,
    ):
        self.diameter_outer = diameter_outer
        self.width = width
        self.width_inner = width_inner
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
