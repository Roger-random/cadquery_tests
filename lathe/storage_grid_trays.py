"""
MIT License

Copyright (c) 2025 Roger Cheng

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

    def show_object(*args, **kwargs):
        pass


def inch_to_mm(length_inch: float):
    return length_inch * 25.4


class storage_grid_trays:
    """
    Various trays using the storage grid system
    """

    def __init__(
        self,
        cell_size=15,
        dovetail_gap=0.2,
    ):
        self.cell_size = cell_size

        # Measured from a 5C collet and not specification dimensions
        self.stem_diameter = inch_to_mm(1.25)
        self.stem_length = inch_to_mm(2.7)

        # Extra diameter clearance for easy collet removal
        self.stem_diameter_clearance = 1

        # Extra padding at bottom of tray
        self.bottom_padding = 3

        # Calculated dimensions
        self.height = self.stem_length + self.bottom_padding
        self.cell_count = math.ceil(self.stem_diameter / cell_size)
        self.unit_size = self.cell_count * cell_size

        # Create instance of tray generator
        self.generator = dovetailstoragegrid.DovetailStorageGrid(
            x=cell_size, y=cell_size, z=self.height, dovetail_gap=dovetail_gap
        )

    def single_5c(self):
        center = self.cell_size * self.cell_count / 2
        exterior = self.generator.basic_tray(
            self.cell_count, self.cell_count, wall_thickness=0
        )

        cavity = (
            cq.Workplane("XY")
            .transformed(offset=(center, center, self.bottom_padding))
            .circle(radius=(self.stem_diameter + self.stem_diameter_clearance) / 2)
            .extrude(self.stem_length)
        )

        return exterior - cavity

    def nine_5c(self):
        packed_cell_count = math.ceil(self.stem_diameter * 3.6 / self.cell_size)

        log(
            f"Packing {self.stem_diameter} in {packed_cell_count} versus {self.cell_count}"
        )

        step_offset = (packed_cell_count * self.cell_size) / 3
        center_offset = step_offset / 2

        exterior = self.generator.basic_tray(
            packed_cell_count, packed_cell_count, wall_thickness=0
        )

        for x in range(3):
            for y in range(3):
                cavity = (
                    cq.Workplane("XY")
                    .transformed(
                        offset=(
                            center_offset + x * step_offset,
                            center_offset + y * step_offset,
                            self.bottom_padding,
                        )
                    )
                    .circle(
                        radius=(self.stem_diameter + self.stem_diameter_clearance) / 2
                    )
                    .extrude(self.stem_length)
                )
                exterior = exterior - cavity

        return exterior

    def pin_punch_set(self):
        """
        Tray for Harbor Freight 93424 32959 56348
        Pittsburgh 8-piece pin punch set
        """
        exterior = self.generator.basic_tray(4, 2, wall_thickness=0)
        step_offset = 14
        center_offset = 6

        exterior = exterior - (
            cq.Workplane("XY")
            .transformed(offset=(center_offset, center_offset, self.bottom_padding))
            .circle(radius=8 / 2)
            .extrude(self.height)
        )
        exterior = exterior - (
            cq.Workplane("XY")
            .transformed(
                offset=(center_offset + step_offset, center_offset, self.bottom_padding)
            )
            .circle(radius=8 / 2)
            .extrude(self.height)
        )
        exterior = exterior - (
            cq.Workplane("XY")
            .transformed(
                offset=(
                    center_offset + step_offset * 2,
                    center_offset,
                    self.bottom_padding,
                )
            )
            .circle(radius=9 / 2)
            .extrude(self.height)
        )
        exterior = exterior - (
            cq.Workplane("XY")
            .transformed(
                offset=(
                    center_offset + step_offset * 3,
                    center_offset,
                    self.bottom_padding,
                )
            )
            .circle(radius=9 / 2)
            .extrude(self.height)
        )
        exterior = exterior - (
            cq.Workplane("XY")
            .transformed(
                offset=(
                    center_offset,
                    center_offset + step_offset,
                    self.bottom_padding,
                )
            )
            .circle(radius=9 / 2)
            .extrude(self.height)
        )
        exterior = exterior - (
            cq.Workplane("XY")
            .transformed(
                offset=(
                    center_offset + step_offset,
                    center_offset + step_offset,
                    self.bottom_padding,
                )
            )
            .circle(radius=9 / 2)
            .extrude(self.height)
        )
        exterior = exterior - (
            cq.Workplane("XY")
            .transformed(
                offset=(
                    center_offset + step_offset * 2,
                    center_offset + step_offset,
                    self.bottom_padding,
                )
            )
            .circle(radius=11 / 2)
            .extrude(self.height)
        )
        exterior = exterior - (
            cq.Workplane("XY")
            .transformed(
                offset=(
                    center_offset + step_offset * 3,
                    center_offset + step_offset,
                    self.bottom_padding,
                )
            )
            .circle(radius=13 / 2)
            .extrude(self.height)
        )
        return exterior


trays = storage_grid_trays()

show_object(trays.pin_punch_set(), options={"color": "green", "alpha": 0.5})
