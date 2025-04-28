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

import sys

sys.path.append("../../storage_grid/")  # Fragile, depends on directory structure
import dovetailstoragegrid


# When not running in CQ-Editor, turn log into print
if "log" not in globals():

    def log(*args):
        print(args)


# When not running in CQ-Editor, turn show_object into no-op
if "show_object" not in globals():

    def show_object(*args):
        pass


class endmill_storage_grid:
    """
    Uses the dovetail storage grid system to organize endmills of various
    diameters and lengths into a consistent grid.
    """

    def __init__(
        self,
        drawer_height=4 * 25.4,
        exposed_height=10,
        cell_size=15,
        cavity_clearance=0.2,
        funnel_lip=2,
        funnel_depth=2,
    ):
        self.cell_size = cell_size
        self.drawer_height = drawer_height
        self.exposed_height = exposed_height
        self.cavity_clearance = cavity_clearance
        self.funnel_lip = funnel_lip
        self.funnel_depth = funnel_depth

        self.tray_height = drawer_height - exposed_height
        self.generator = dovetailstoragegrid.DovetailStorageGrid(
            x=cell_size, y=cell_size, z=self.tray_height
        )

    def cylinders(self, diameters, lengths):
        assert len(diameters) == len(lengths)

        grid_units_y = math.ceil(
            (
                max(diameters)
                + self.cavity_clearance * 2
                + self.generator.dovetail_protrusion * 2
            )
            / self.cell_size
        )

        grid_units_x = math.ceil(
            (
                sum(diameters)
                + self.cavity_clearance * (len(diameters) + 1)
                + self.generator.dovetail_protrusion * 2
                + self.funnel_lip * 2
            )
            / self.cell_size
        )
        spacing_x = ((grid_units_x * self.cell_size) - sum(diameters)) / (
            len(diameters) + 1
        )

        translate_x = spacing_x

        volume = self.generator.label_tray(grid_units_x, grid_units_y, wall_thickness=0)

        for i in range(len(diameters)):
            radius = diameters[i] / 2
            cavity_depth = lengths[i] - self.exposed_height

            subtract = (
                cq.Workplane("XY")
                .circle(radius + self.funnel_lip)
                .workplane(offset=-self.funnel_depth)
                .circle(radius + self.cavity_clearance)
                .loft()
                .faces("<Z")
                .workplane()
                .circle(radius + self.cavity_clearance)
                .extrude(cavity_depth - self.funnel_depth)
                .translate(
                    (
                        translate_x + radius,
                        grid_units_y * self.cell_size / 2,
                        self.tray_height,
                    )
                )
            )

            volume = volume - subtract

            translate_x += diameters[i] + spacing_x

        return volume

    def chamfer_endmills(self):
        """
        Two chamfer endmills from Chuck's shop clearance. Both 7/16 diameter
        shank but with different lengths. (And different cutting angles, but
        that doesn't matter here.)
        """
        inch_7_16 = 25.4 * (7 / 16)
        return self.cylinders(diameters=(inch_7_16, inch_7_16), lengths=(63.5, 53))

    def corner_rounding_endmills(self):
        """
        Two corner rounding endmills from Chuck's shop clearance. Challenge
        the generator with two different diameters and lengths! (And different
        fillet radii but again that doesn't matter here.)
        """
        return self.cylinders(diameters=(15.9, 11.2), lengths=(76, 64))

    def dovetail_endmills(self):
        """
        Two identical dovetail cutting endmills from Chuck's shop clearance.
        """
        return self.cylinders(diameters=(19, 19), lengths=(54, 54))

    def standard_and_roughing_1_2(self):
        """
        Two 1/2" diameter 4-flute endmills bought from Chuck's shop clearance
        The shorter one is a roughing endmill and I hope it doesn't matter here.
        """
        inch_1_2 = 25.4 * (1 / 2)
        return self.cylinders(diameters=(inch_1_2, inch_1_2), lengths=(67, 83))


esg = endmill_storage_grid()
show_object(esg.standard_and_roughing_1_2())
