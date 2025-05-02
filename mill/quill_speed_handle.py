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

# When not running in CQ-Editor, turn log into print
if "log" not in globals():

    def log(*args):
        print(args)


# When not running in CQ-Editor, turn show_object into no-op
if "show_object" not in globals():

    def show_object(*args):
        pass


def inch_to_mm(dimension_inch: float):
    return 25.4 * dimension_inch


class bridgeport_quill_placeholder:
    def __init__(self):
        self.spring_cover_diameter = inch_to_mm(2.75)
        self.spring_cover_thickness = inch_to_mm(0.175)
        self.quill_pinion_hub_base_diameter = inch_to_mm(1.75)
        self.quill_pinion_hub_base_thickness = inch_to_mm(0.2)
        self.quill_pinion_hub_diameter = inch_to_mm(1)
        self.quill_pinion_hub_thickness = inch_to_mm(0.85)
        self.base_to_slot_1 = inch_to_mm(0.25)
        self.slot_1 = inch_to_mm(0.1)
        self.slot_1_to_slot_2 = inch_to_mm(0.2)
        self.slot_2 = inch_to_mm(0.1)
        self.slot_diameter = inch_to_mm(0.8)  # Need to verify
        self.pin_hole_diameter = inch_to_mm(0.22)
        self.pin_hole_circle_diameter = inch_to_mm(1.375)

    def placeholder(self):
        base = (
            cq.Workplane("YZ")
            .circle(self.quill_pinion_hub_base_diameter / 2)
            .extrude(-self.quill_pinion_hub_base_thickness)
            .faces("<X")
            .workplane()
            .circle(self.spring_cover_diameter / 2)
            .extrude(self.spring_cover_thickness)
        )

        hub = (
            cq.Workplane("YZ")
            .circle(self.quill_pinion_hub_diameter / 2)
            .extrude(self.base_to_slot_1)
            .faces(">X")
            .workplane()
            .circle(self.slot_diameter / 2)
            .extrude(self.slot_1)
            .faces(">X")
            .workplane()
            .circle(self.quill_pinion_hub_diameter / 2)
            .extrude(self.slot_1_to_slot_2)
            .faces(">X")
            .workplane()
            .circle(self.slot_diameter / 2)
            .extrude(self.slot_2)
            .faces(">X")
            .workplane()
            .circle(self.quill_pinion_hub_diameter / 2)
            .extrude(
                self.quill_pinion_hub_thickness
                - self.base_to_slot_1
                - self.slot_1
                - self.slot_1_to_slot_2
                - self.slot_2
            )
        )

        placeholder = base + hub

        hole_subtract = (
            cq.Workplane("YZ")
            .transformed(offset=cq.Vector(0, self.pin_hole_circle_diameter / 2, 0))
            .circle(self.pin_hole_diameter / 2)
            .extrude(
                self.quill_pinion_hub_base_thickness + self.spring_cover_thickness,
                both=True,
            )
        )

        for angle_degrees in range(0, 360, int(360 / 12)):
            placeholder -= hole_subtract.rotate(
                (0, 0, 0), (1, 0, 0), angleDegrees=angle_degrees
            )

        return placeholder


class quill_speed_handle:
    def __init__(self):
        pass


show_object(
    bridgeport_quill_placeholder().placeholder(),
    options={"color": "gray", "alpha": 0.75},
)
