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


class arbor_morse_taper_placeholder:
    """
    A 3D reprsentation of a chuck arbor with a Morse taper. The arbor is
    defined vertically along the Z axis, with the wider end at Z=0 and narrows
    as it goes up (+Z direction).

    Dimensions from http://www.jacobschuck.com/tech-support/
    """

    def __init__(
        self,
        taper,
        basic_diameter,
        basic_diameter_z,
        taper_length,
        tapered_diameter,
        length_overall,
        tang_width,
        tang_length,
        tang_thickness,
        tang_base_radius,
    ):
        self.taper = taper
        self.basic_diameter = basic_diameter
        self.basic_diameter_z = basic_diameter_z
        self.taper_length = taper_length
        self.tapered_diameter = tapered_diameter
        self.length_overall = length_overall
        self.tang_width = tang_width
        self.tang_length = tang_length
        self.tang_thickness = tang_thickness
        self.tang_base_radius = tang_base_radius

        self.basic_radius = self.basic_diameter / 2
        self.calculated_slope = (
            self.basic_diameter / 2 - self.tapered_diameter / 2
        ) / self.taper_length

    def radius_at_z(self, z):
        return self.basic_radius + (self.basic_diameter_z - z) * self.calculated_slope

    def with_tang(self):
        bottom_radius = self.radius_at_z(0)
        top_radius = self.radius_at_z(self.length_overall)

        shaft_volume = (
            cq.Workplane("XY")
            .circle(bottom_radius)
            .workplane(offset=self.length_overall)
            .circle(top_radius)
            .loft()
        )

        # Don't need to emulate Jacobs taper yet, so a placeholder taper
        # continuation should suffice. Using tang length as something in the
        # neighborhood and would be a function of arbor size.
        shaft_volume = (
            shaft_volume.faces("<Z")
            .workplane()
            .circle(bottom_radius)
            .workplane(offset=self.tang_length)
            .circle(self.radius_at_z(-self.tang_length))
            .loft()
        )

        tang_revolve_subtract = (
            cq.Workplane("XZ")
            .lineTo(
                self.tang_width / 2, -(self.tang_width / 2) * math.sin(math.radians(8))
            )
            .lineTo(self.tang_width / 2, -self.tang_length)
            .line(self.basic_diameter, 0)
            .line(0, self.tang_length * 2)
            .lineTo(0, self.tang_length * 2)
            .close()
            .revolve(angleDegrees=360, axisStart=(0, 0, 0), axisEnd=(0, 1, 0))
            .translate((0, 0, self.length_overall))
        )

        tang_base_subtract = (
            cq.Workplane("XZ")
            .lineTo(self.tang_base_radius, 0, forConstruction=True)
            .lineTo(self.tang_base_radius, self.tang_length)
            .lineTo(-self.tang_base_radius, self.tang_length)
            .lineTo(-self.tang_base_radius, 0)
            .tangentArcPoint((self.tang_base_radius, 0), relative=False)
            .close()
            .extrude(self.basic_diameter, both=True)
        )

        tang_subtract_translate_x = self.tang_thickness / 2 + self.tang_base_radius
        tang_subtract_translate_z = self.length_overall - self.tang_length

        shaft = (
            shaft_volume
            - tang_revolve_subtract
            - tang_base_subtract.translate(
                (tang_subtract_translate_x, 0, tang_subtract_translate_z)
            )
            - tang_base_subtract.translate(
                (-tang_subtract_translate_x, 0, tang_subtract_translate_z)
            )
        )

        return shaft

    def test_box(self, padding_size):
        size = self.radius_at_z(0) + padding_size
        box_half = (
            cq.Workplane("XY")
            .lineTo(size, 0)
            .lineTo(size, size)
            .lineTo(0, size)
            .close()
            .extrude(self.length_overall + padding_size)
        )

        return box_half + box_half.mirror("YZ")

    @staticmethod
    def preset_2mt():
        return arbor_morse_taper_placeholder(
            taper=0.04995,
            basic_diameter=17.78,
            basic_diameter_z=5,
            taper_length=67,
            tapered_diameter=14.9,
            length_overall=80,
            tang_width=13.5,
            tang_length=16,
            tang_thickness=6.3,
            tang_base_radius=6,
        )


class jacobs_chuck_placeholder:
    """
    A simplified representation of a Jacobs chuck intended to help visualize
    how components of the stand would interact, and also serve to encapsulate
    relevant dimensions for use in constructing a stand. Defined vertically
    along the Z axis, with the back face at Z=0 and chuck opening facing down
    (-Z direction.)

    Part nomenclature from http://www.jacobschuck.com/tech-support/
    """

    def __init__(
        self,
        back_diameter_narrow,
        back_diameter_wide,
        back_taper_height,
        back_to_sleeve_height,
        sleeve_diameter_back_narrow,
        sleeve_diameter_back_wide,
        sleeve_diameter_back_taper_height,
        sleeve_diameter_center,
        sleeve_diameter_center_height,
        sleeve_diameter_front_wide,
        sleeve_diameter_front_narrow,
        sleeve_diameter_front_taper_height,
        sleeve_length,
        body_nose_diameter,
        body_nose_diameter_narrow,
        body_nose_diameter_taper_height,
        body_open_length,
        body_closed_length,
        jaws_diameter_wide,
        jaws_diameter_narrow,
    ):
        self.back_diameter_narrow = back_diameter_narrow
        self.back_diameter_wide = back_diameter_wide
        self.back_taper_height = back_taper_height
        self.back_to_sleeve_height = back_to_sleeve_height
        self.sleeve_diameter_back_narrow = sleeve_diameter_back_narrow
        self.sleeve_diameter_back_wide = sleeve_diameter_back_wide
        self.sleeve_diameter_back_taper_height = sleeve_diameter_back_taper_height
        self.sleeve_diameter_center = sleeve_diameter_center
        self.sleeve_diameter_center_height = sleeve_diameter_center_height
        self.sleeve_diameter_front_wide = sleeve_diameter_front_wide
        self.sleeve_diameter_front_narrow = sleeve_diameter_front_narrow
        self.sleeve_diameter_front_taper_height = sleeve_diameter_front_taper_height
        self.sleeve_length = sleeve_length
        self.body_nose_diameter = body_nose_diameter
        self.body_nose_diameter_narrow = body_nose_diameter_narrow
        self.body_nose_diameter_taper_height = body_nose_diameter_taper_height
        self.body_open_length = body_open_length
        self.body_closed_length = body_closed_length
        self.jaws_diameter_wide = jaws_diameter_wide
        self.jaws_diameter_narrow = jaws_diameter_narrow

        self.sleeve_start_height = back_taper_height + back_to_sleeve_height
        self.sleeve_diameter_gear_taper_height = (
            sleeve_length
            - sleeve_diameter_back_taper_height
            - sleeve_diameter_center_height
            - sleeve_diameter_front_taper_height
        )

    @staticmethod
    def preset_6a():
        return jacobs_chuck_placeholder(
            back_diameter_narrow=38.8,
            back_diameter_wide=42.6,
            back_taper_height=1.3,
            back_to_sleeve_height=1,
            sleeve_diameter_back_narrow=47.4,
            sleeve_diameter_back_wide=49,
            sleeve_diameter_back_taper_height=1.2,
            sleeve_diameter_center=49,
            sleeve_diameter_center_height=32.6,
            sleeve_diameter_front_wide=47.5,
            sleeve_diameter_front_narrow=47.3,
            sleeve_diameter_front_taper_height=6.1,
            sleeve_length=40.5,
            body_nose_diameter=36.31,
            body_nose_diameter_narrow=28.3,
            body_nose_diameter_taper_height=6.8,
            body_open_length=64.02,
            body_closed_length=84,
            jaws_diameter_wide=21,
            jaws_diameter_narrow=11.6,
        )

    def body(self):
        return (
            cq.Workplane("XY")
            .circle(self.back_diameter_narrow / 2)
            .workplane(-self.back_taper_height)
            .circle(self.back_diameter_wide / 2)
            .loft()
            .faces("<Z")
            .workplane()
            .circle(self.back_diameter_wide / 2)
            .extrude(
                self.back_to_sleeve_height
                + self.sleeve_length
                - self.back_taper_height
                - self.sleeve_diameter_front_taper_height
                - self.sleeve_diameter_gear_taper_height
            )
            .faces("<Z")
            .workplane()
            .circle(self.back_diameter_wide / 2)
            .workplane(
                offset=self.sleeve_diameter_gear_taper_height
                + self.sleeve_diameter_front_taper_height
            )
            .circle(self.body_nose_diameter / 2)
            .loft()
            .faces("<Z")
            .workplane()
            .circle(self.body_nose_diameter / 2)
            .extrude(
                self.body_open_length
                - self.body_nose_diameter_taper_height
                - self.sleeve_length
                - self.back_to_sleeve_height
            )
            .faces("<Z")
            .workplane()
            .circle(self.body_nose_diameter / 2)
            .workplane(offset=self.body_nose_diameter_taper_height)
            .circle(self.body_nose_diameter_narrow / 2)
            .loft()
        )

    def sleeve(self):
        return (
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(0, 0, -self.sleeve_start_height))
            .circle(self.sleeve_diameter_back_narrow / 2)
            .workplane(offset=-self.sleeve_diameter_back_taper_height)
            .circle(self.sleeve_diameter_back_wide / 2)
            .loft()
            .faces("<Z")
            .workplane()
            .circle(self.sleeve_diameter_center / 2)
            .extrude(self.sleeve_diameter_center_height)
            .faces("<Z")
            .workplane()
            .circle(self.sleeve_diameter_front_wide / 2)
            .workplane(offset=self.sleeve_diameter_front_taper_height)
            .circle(self.sleeve_diameter_front_narrow / 2)
            .loft()
            .faces("<Z")
            .workplane()
            .circle(self.sleeve_diameter_front_narrow / 2)
            .workplane(offset=self.sleeve_diameter_gear_taper_height)
            .circle(self.body_nose_diameter / 2)
            .loft()
        )

    def jaws(self):
        return (
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(0, 0, -self.body_open_length))
            .circle(self.jaws_diameter_wide / 2)
            .workplane(offset=self.body_open_length - self.body_closed_length)
            .circle(self.jaws_diameter_narrow / 2)
            .loft()
        )

    def placeholder(self):

        return self.body() + self.sleeve() + self.jaws()


class jacobs_chuck_stand:
    """
    A 3D-printed stand for holding a Jacobs chuck, many dimension parameters
    pulled from placeholder classes for chuck and arbor.
    """

    def __init__(self):
        pass


arbor = arbor_morse_taper_placeholder.preset_2mt()

placeholder = arbor.with_tang().translate((0, 0, 6))


# test_box = arbor.test_box(padding_size=5).edges("|Z").fillet(2.5) - placeholder
# show_object(test_box)

chuck = jacobs_chuck_placeholder.preset_6a()

placeholder += chuck.placeholder()

show_object(placeholder, options={"color": "green", "alpha": 0.5})

test_box = (
    cq.Workplane("XZ")
    .rect(
        chuck.sleeve_diameter_center + 10,
        chuck.body_closed_length + arbor.length_overall + 10,
    )
    .extrude(2)
    .edges("|Y")
    .fillet(20)
)

show_object(test_box - placeholder)
