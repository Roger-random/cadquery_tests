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

# When not running in CQ-Editor, turn log into print
if "log" not in globals():

    def log(*args):
        print(args)


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
        drill_area_diameter=60,
        drill_bit_diameter=25.4 * (21 / 64),  # A less-used bit from the set
        drill_hole_padding=3,
        base_diameter=80,
        base_central_height=10,
        base_surround_height=10,
        guide_diameter=90,
        guide_interface_chamfer=1,
    ):
        self.lid_interior_diameter = lid_interior_diameter
        self.lid_raised_diameter = lid_raised_diameter
        self.lid_raised_height = lid_raised_height
        self.drill_area_diameter = drill_area_diameter
        self.drill_bit_diameter = drill_bit_diameter
        self.drill_hole_padding = drill_hole_padding
        self.base_diameter = base_diameter
        self.base_central_height = base_central_height
        self.base_surround_height = base_surround_height
        self.base_overall_height = (
            base_surround_height + base_central_height + lid_raised_height
        )
        self.guide_diameter = guide_diameter
        self.guide_interface_chamfer = guide_interface_chamfer

    def drill_locations(
        self,
    ):
        drill = (
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(0, 0, self.base_overall_height / 2))
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

    def base(
        self,
        lid_top_fillet=1,
        base_surround_fillet=15,
    ):
        """
        Lid sits on top of this base object
        """
        base_surround = (
            cq.Workplane("XY")
            .polygon(8, self.base_diameter, circumscribed=True)
            .extrude(self.base_surround_height)
            .edges("|Z")
            .fillet(base_surround_fillet)
            .faces(">Z")
            .chamfer(self.guide_interface_chamfer)
        )

        base_center = (
            base_surround.faces(">Z")
            .workplane()
            .circle(self.lid_interior_diameter / 2)
            .extrude(self.base_central_height)
            .faces(">Z")
            .fillet(lid_top_fillet)
            .faces(">Z")
            .workplane()
            .circle(self.lid_raised_diameter / 2)
            .extrude(self.lid_raised_height)
        )

        return base_center

    def guide(
        self,
        guide_thickness=2.4,
        guide_surround_fillet=15,
        finger_hole_diameter=20,
    ):
        """
        Once the lid is installed on base, put this guide over them.
        """
        guide = (
            cq.Workplane("XY")
            .polygon(8, self.guide_diameter, circumscribed=True)
            .polygon(8, self.base_diameter, circumscribed=True)
            .extrude(self.base_overall_height)
            .faces(">Z")
            .polygon(8, self.guide_diameter, circumscribed=True)
            .extrude(guide_thickness)
            .edges("|Z")
            .fillet(guide_surround_fillet)
            .faces("<Z or >Z")
            .chamfer(self.guide_interface_chamfer)
        )

        # Cut holes for my finger to get in there and remove the base
        # after drilling. No of course I had this before I printed it
        # and discovered I couldn't get the base out. Don't be silly.
        finger_hole_subtract = (
            cq.Workplane("XZ")
            .circle(finger_hole_diameter / 2)
            .extrude(self.guide_diameter, both=True)
        )

        for rotation_step in range(4):
            guide = guide - finger_hole_subtract.rotate(
                (0, 0, 0), (0, 0, 1), rotation_step * 45
            )

        return guide


if "show_object" in globals():
    jig = dessicant_container_lid_drill_jig()
    locations = jig.drill_locations()
    show_object(jig.base() - locations, options={"color": "blue", "alpha": 0.5})
    show_object(jig.guide() - locations, options={"color": "green", "alpha": 0.5})
