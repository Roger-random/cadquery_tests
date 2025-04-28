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

    def cylinderical(self, tool_diameter, tool_length):
        """
        Generate a tray sufficient to accommodate a cylindrical tool of the
        given diameter. Depth of cylindrical cavity is the given tool length
        minus the exposed length as specified in constructor.
        """
        grid_units = math.ceil(
            (
                tool_diameter
                + self.cavity_clearance * 2
                + self.generator.dovetail_protrusion * 2
            )
            / self.cell_size
        )

        volume = self.generator.label_tray(grid_units, grid_units, wall_thickness=0)

        radius = tool_diameter / 2
        cavity_depth = tool_length - self.exposed_height

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
                    grid_units * self.cell_size / 2,
                    grid_units * self.cell_size / 2,
                    self.tray_height,
                )
            )
        )

        return volume - subtract

    def chamfer_endmill_120deg_7_16(self):
        """
        7/16" diameter shank 2-flute endmill with 120 degree tip
        """
        return self.cylinderical(25.4 * (7 / 16), 53)

    def endmill_4_flute_1_2(self):
        """
        1/2" diameter 4-flute endmill bought from Chuck's shop clearance
        """
        return self.cylinderical(25.4 * 0.5, 83.3)


esg = endmill_storage_grid()
show_object(esg.chamfer_endmill_120deg_7_16())
