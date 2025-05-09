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

import vise_jaws

# When not running in CQ-Editor, turn log into print
if "log" not in globals():

    def log(*args):
        print(args)


# When not running in CQ-Editor, turn show_object into no-op
if "show_object" not in globals():

    def show_object(*args, **kwargs):
        pass


class dessicant_container_lid_drill_jig:
    """
    Jig to hold the lid of a small stell container
    (Example: https://www.mcmaster.com/products/containers-with-lids/tins~/)
    for a drill press. Original intent is to turn these small metal containers
    into containers for loose dessicant pellets, with holes drilled in the lid
    for moisture to pass through. Once dessicant has saturated with moisture,
    the entire container can go into an oven to regenerate the dessicant.
    """

    def __init__(
        self,
        lid_interior_diameter=68.8,
        lid_raised_diameter=60,
        lid_raised_height=0.4,
        lid_top_fillet=1,
        lid_edge_clearance=3,
        drill_area_diameter=60,
        drill_bit_diameter=25.4 * (21 / 64),  # A less-used bit from the set
        drill_hole_padding=3,
        base_central_height=10,
        base_surround_height=8,
        vise_jaw_angle=20,
    ):
        self.lid_interior_diameter = lid_interior_diameter
        self.lid_raised_diameter = lid_raised_diameter
        self.lid_raised_height = lid_raised_height
        self.lid_top_fillet = lid_top_fillet
        self.lid_edge_clearance = lid_edge_clearance
        self.drill_area_diameter = drill_area_diameter
        self.drill_bit_diameter = drill_bit_diameter
        self.drill_hole_padding = drill_hole_padding
        self.base_central_height = base_central_height
        self.base_surround_height = base_surround_height
        self.base_overall_height = (
            base_central_height + lid_raised_height + base_surround_height
        )
        self.vise_jaw_angle = vise_jaw_angle

    def drill_locations(self):
        drill = (
            cq.Workplane("XY")
            .circle(self.drill_bit_diameter / 2)
            .extrude(self.base_overall_height, both=True)
        )

        drill_hole_spacing = self.drill_bit_diameter + self.drill_hole_padding

        locations = drill

        current_hole_radius = drill_hole_spacing
        while (current_hole_radius + (self.drill_bit_diameter / 2)) < (
            self.drill_area_diameter / 2
        ):
            drill_circumference = 2 * current_hole_radius * math.pi
            drill_count = math.floor(drill_circumference / drill_hole_spacing)
            assert drill_count > 0
            angle_spacing = 360 / drill_count
            for d in range(drill_count):
                locations = locations + (
                    drill.translate((current_hole_radius, 0, 0)).rotate(
                        (0, 0, 0), (0, 0, 1), angle_spacing * d
                    )
                )
            current_hole_radius += drill_hole_spacing

        return locations

    def guide(self):
        """
        A guide to sit on top of the lid (sitting up-side down) with holes
        indication drill locations, held in place by slope of custom vise jaws
        """
        size_half = self.lid_interior_diameter / 2 + self.lid_edge_clearance
        guide_top_half = (
            cq.Workplane("XZ")
            .line(0, self.base_surround_height)
            .line(size_half, 0)
            .line(
                self.base_surround_height * math.tan(math.radians(self.vise_jaw_angle)),
                -self.base_surround_height,
            )
            .close()
            .extrude(size_half, both=True)
        )

        guide_top = guide_top_half + guide_top_half.mirror("YZ")

        guide_top = guide_top.edges("not |X").edges("not |Y").fillet(5)

        guide_center = (
            guide_top.faces("<Z")
            .workplane()
            .circle(self.lid_interior_diameter / 2)
            .extrude(self.base_central_height)
            .faces("<Z")
            .fillet(self.lid_top_fillet)
            .faces("<Z")
            .workplane()
            .circle(self.lid_raised_diameter / 2)
            .extrude(self.lid_raised_height)
        )

        guide_top = guide_top + guide_center

        return guide_top

    def jaw(self, rotate_for_printing=False):
        vise = vise_jaws.hf_59111_central_machinery_4in_drill_press_vise()
        base = vise.jaw()

        wedge = (
            cq.Workplane("XZ")
            .lineTo(0, vise.height / 2)
            .lineTo(
                vise.height * math.tan(math.radians(self.vise_jaw_angle)),
                vise.height / 2,
            )
            .lineTo(0, -vise.height / 2)
            .close()
            .extrude(vise.width / 2, both=True)
        )

        jaw = vise.fastener_cut(base + wedge)

        jaw = jaw.edges("|X").fillet(2)

        if rotate_for_printing:
            jaw = jaw.rotate((0, 0, 0), (0, 1, 0), 90 - self.vise_jaw_angle)

        return jaw


if "show_object" in globals():
    jig = dessicant_container_lid_drill_jig(
        lid_interior_diameter=64.4,
        lid_raised_diameter=54,
        lid_raised_height=0.56,
        drill_area_diameter=54,
        drill_bit_diameter=25.4 * (17 / 64),  # Another less-used drill bit
        drill_hole_padding=4,
        base_central_height=12.5,
    )
    locations = jig.drill_locations()
    show_object(
        (jig.guide() - locations).faces(">Z").chamfer(1),
        options={"color": "green", "alpha": 0.5},
    )
    show_object(
        jig.jaw().translate((-jig.lid_interior_diameter / 2 - 12, 0, 0)),
        options={"color": "blue", "alpha": 0.5},
    )
