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

        # Don't need to emulate Jacobs taper yet, so a placeholder cylinder
        # should suffice. Using tang length as something in the neighborhood
        # and would be a function of arbor size.
        shaft_volume = (
            shaft_volume.faces("<Z")
            .workplane()
            .circle(bottom_radius)
            .extrude(self.tang_length)
        )

        tang_revolve_subtract = (
            cq.Workplane("XZ")
            .lineTo(
                self.tang_width / 2, -(self.tang_width / 2) * math.sin(math.radians(8))
            )
            .lineTo(self.tang_width / 2, -self.tang_length * 0.5)
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

    def __init__(self):
        pass


class jacobs_chuck_stand:
    """
    A 3D-printed stand for holding a Jacobs chuck, many dimension parameters
    pulled from placeholder classes for chuck and arbor.
    """

    def __init__(self):
        pass


arbor = arbor_morse_taper_placeholder.preset_2mt()

placeholder = arbor.with_tang()

show_object(placeholder, options={"color": "green", "alpha": 0.5})

test_box = arbor.test_box(padding_size=5).edges("|Z").fillet(2.5) - placeholder

show_object(test_box)
