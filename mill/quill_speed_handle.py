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


def mm_to_inch(dimension_mm: float):
    return dimension_mm / 25.4


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
        self.slot_diameter = inch_to_mm(0.91)
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


extra_gap = 0.25


class quill_speed_handle:
    def __init__(
        self,
        quill: bridgeport_quill_placeholder,
        cylinder_diameter: float = inch_to_mm(2),
        cylinder_length: float = inch_to_mm(1.5),
        cylinder_hub_gap: float = inch_to_mm(0.125),
        slot_width: float = inch_to_mm(0.5),
        hinge_pin_diameter: float = inch_to_mm(0.26) + extra_gap,
        lock_pin_diameter: float = inch_to_mm(0.2) + extra_gap,
        lock_pin_protrusion: float = inch_to_mm(0.2),
        pin_spring_hole_diameter: float = inch_to_mm(0.3) + extra_gap * 2,
        pin_spring_hole_depth: float = inch_to_mm(0.4),
        pin_spring_length: float = inch_to_mm(0.425),
        pin_spring_range: float = inch_to_mm(0.3),
        handle_rotation_degree: float = 15,  # For display purposes
    ):
        self.quill = quill
        self.cylinder_radius = cylinder_diameter / 2
        self.cylinder_length = cylinder_length
        self.slot_width = slot_width
        self.cylinder_hub_gap = cylinder_hub_gap
        self.hinge_pin_diameter = hinge_pin_diameter
        self.lock_pin_diameter = lock_pin_diameter
        self.lock_pin_protrusion = lock_pin_protrusion
        self.pin_spring_hole_diameter = pin_spring_hole_diameter
        self.pin_spring_hole_depth = pin_spring_hole_depth
        self.pin_spring_length = pin_spring_length
        self.pin_spring_range = pin_spring_range
        self.handle_rotation_degree = handle_rotation_degree

    def display_rotation(self, object):
        return object.rotate(
            (
                self.quill.quill_pinion_hub_thickness
                + self.cylinder_hub_gap
                + self.slot_width / 2,
                self.quill.pin_hole_circle_diameter / 2,
                0,
            ),
            (
                self.quill.quill_pinion_hub_thickness
                + self.cylinder_hub_gap
                + self.slot_width / 2,
                self.quill.pin_hole_circle_diameter / 2,
                1,
            ),
            self.handle_rotation_degree,
        )

    def cylinder(self):
        volume = (
            cq.Workplane("YZ")
            .circle(self.cylinder_radius)
            .circle(extra_gap + self.quill.quill_pinion_hub_diameter / 2)
            .extrude(self.cylinder_length)
        )

        slot_subtract = (
            cq.Workplane("XZ")
            .lineTo(
                self.quill.quill_pinion_hub_thickness + self.cylinder_hub_gap,
                self.slot_width / 2,
                forConstruction=True,
            )
            .line(self.cylinder_length, 0)
            .line(0, -self.slot_width)
            .line(-self.cylinder_length, 0)
            .close()
            .extrude(self.cylinder_radius * 2, both=True)
        )

        slot_subtract_rotated = self.display_rotation(slot_subtract)

        spring_pin_subtract = (
            cq.Workplane("YZ")
            .transformed(
                offset=cq.Vector(
                    -self.quill.pin_hole_circle_diameter / 2,
                    0,
                    self.quill.quill_pinion_hub_thickness,
                )
            )
            .circle(self.pin_spring_hole_diameter / 2)
            .extrude(self.pin_spring_hole_depth, both=True)
        )

        lock_pin_subtract = (
            cq.Workplane("YZ")
            .transformed(
                offset=cq.Vector(-self.quill.pin_hole_circle_diameter / 2, 0, 0)
            )
            .circle(self.lock_pin_diameter / 2)
            .extrude(self.cylinder_length, both=True)
        )

        locator_subtract = (
            cq.Workplane("XZ")
            .transformed(
                offset=cq.Vector(
                    self.quill.base_to_slot_1
                    + self.quill.slot_1
                    + self.quill.slot_1_to_slot_2
                    + self.quill.slot_2 / 2,
                    self.quill.slot_diameter / 2,
                    0,
                )
            )
            .circle(self.quill.slot_2 * 0.75)
            .extrude(self.cylinder_radius, both=True)
        )

        cylinder = (
            volume
            - slot_subtract
            - slot_subtract_rotated
            - self.hinge_pin(length=self.cylinder_radius * 2)
            - spring_pin_subtract
            - lock_pin_subtract
            - locator_subtract
            - locator_subtract.mirror("XY")
        )

        return cylinder

    def lock_pin(self):
        shoulder_height = (
            self.quill.quill_pinion_hub_thickness
            + self.cylinder_hub_gap
            - self.pin_spring_length
            + self.pin_spring_range
        )
        log(
            f"Diameter {mm_to_inch(self.lock_pin_diameter)} to shoulder height {mm_to_inch(shoulder_height)} then {mm_to_inch(self.pin_spring_hole_diameter)} for spring length {mm_to_inch(self.pin_spring_length)}"
        )
        return (
            cq.Workplane("YZ")
            .transformed(
                offset=cq.Vector(-self.quill.pin_hole_circle_diameter / 2, 0, 0)
            )
            .circle(self.lock_pin_diameter / 2)
            .extrude(shoulder_height)
            .faces(">X")
            .workplane()
            .circle(self.pin_spring_hole_diameter / 2)
            .extrude(self.pin_spring_length)
        )

    def hinge_pin(self, length: float):
        return (
            cq.Workplane("XY")
            .transformed(
                offset=cq.Vector(
                    self.quill.quill_pinion_hub_thickness
                    + self.cylinder_hub_gap
                    + self.slot_width / 2,
                    self.quill.pin_hole_circle_diameter / 2,
                    0,
                )
            )
            .circle(self.hinge_pin_diameter / 2)
            .extrude(length / 2, both=True)
        )

    def handle(self, length: float, gap: float = inch_to_mm(0.01)):

        handle_side = self.slot_width - gap
        return (
            cq.Workplane("XZ")
            .transformed(
                offset=cq.Vector(
                    self.quill.quill_pinion_hub_thickness + self.cylinder_hub_gap,
                    handle_side / 2,
                    -self.cylinder_radius,
                )
            )
            .line(handle_side, 0)
            .line(0, -handle_side)
            .line(-handle_side, 0)
            .close()
            .extrude(length)
            .edges("|Z")
            .fillet(handle_side * 0.2)
        ) - self.hinge_pin(handle_side * 25)


quill = bridgeport_quill_placeholder()
handle = quill_speed_handle(quill=quill)

show_object(
    quill.placeholder(),
    options={"color": "gray", "alpha": 0.75},
)

show_object(
    handle.cylinder(),
    options={"color": "blue", "alpha": 0.25},
)

show_object(
    handle.lock_pin(),
    options={"color": "red", "alpha": 0.5},
)

show_object(
    handle.hinge_pin(50),
    options={"color": "red", "alpha": 0.5},
)

show_object(
    handle.display_rotation(handle.handle(75)),
    options={"color": "green", "alpha": 0.5},
)
