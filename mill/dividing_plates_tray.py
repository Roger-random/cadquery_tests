"""
MIT License

Copyright (c) 2026 Roger Cheng

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

# When not running in CQ-Editor, turn log into print
if "log" not in globals():

    def log(*args):
        print(args)


# When not running in CQ-Editor, turn show_object into no-op
if "show_object" not in globals():

    def show_object(*args, **kwargs):
        pass


class dividing_plates_tray:
    def __init__(self):
        self.print_margin = 0.2

        self.plate_thickness = 7.8
        self.plate_diameter = 158

        # Extra room to make it easy to slide plates in and out
        self.plate_margin = 1

        # Amount of room between plates (include plate_margin)
        self.plate_spacing = 10

        # Depth of lip holding plate
        self.plate_lip_depth = 5

    def plate_placeholder(self):
        placeholder_half = (
            cq.Workplane("XZ")
            .circle(
                radius=self.plate_diameter / 2 + self.plate_margin + self.print_margin
            )
            .extrude(self.plate_thickness / 2 + self.print_margin + self.plate_margin)
            .faces("<Y")
            .workplane()
            .circle(radius=self.plate_diameter / 2 - self.plate_lip_depth)
            .workplane(self.plate_spacing)
            .circle(
                radius=self.plate_diameter / 2
                - self.plate_lip_depth
                - self.plate_spacing
            )
            .loft()
        )

        placeholder_slot = (
            cq.Workplane("XY")
            .rect(
                xLen=self.plate_diameter * 0.3,
                yLen=self.plate_thickness
                + self.plate_margin * 2
                + self.print_margin * 2,
            )
            .extrude(-self.plate_diameter)
            .edges("|Z")
            .fillet(self.plate_thickness / 2)
        )

        placeholder = (
            placeholder_half + placeholder_half.mirror("XZ") + placeholder_slot
        )

        return placeholder

    def single_tray(self):
        single_plate = self.plate_placeholder()

        tray_base = (
            cq.Workplane("XY")
            .transformed(offset=(0, 0, -self.plate_spacing * 2))
            .rect(
                xLen=self.plate_diameter + self.plate_spacing,
                yLen=self.plate_spacing * 2 + self.plate_thickness,
            )
            .extrude(-self.plate_diameter / 2 + self.plate_spacing * 1.5)
            .edges("|Z")
            .fillet(self.plate_spacing)
        )

        single = tray_base - single_plate

        single = single.faces(">Z").chamfer(self.plate_margin)

        return single

    def six_pack_tray(self):
        single_plate = self.plate_placeholder()

        tray_base = (
            cq.Workplane("XY")
            .transformed(offset=(0, 0, -self.plate_spacing * 2))
            .rect(
                xLen=self.plate_diameter + self.plate_spacing,
                yLen=self.plate_spacing * 6 + self.plate_thickness * 6,
            )
            .extrude(-self.plate_diameter / 2 + self.plate_spacing * 1.5)
            .edges("|Z")
            .fillet(self.plate_spacing)
        ).translate((0, self.plate_thickness * 2.5 + self.plate_spacing * 2.5, 0))

        for i in range(6):
            tray_base = tray_base - single_plate.translate(
                (0, (self.plate_spacing + self.plate_thickness) * i)
            )

        tray_base = tray_base.faces(">Z").chamfer(self.plate_margin)

        return tray_base


dpt = dividing_plates_tray()

show_object(dpt.six_pack_tray(), options={"color": "green", "alpha": 0.5})
