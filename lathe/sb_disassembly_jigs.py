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

    def show_object(*args, **kwargs):
        pass


def inch_to_mm(length_inch: float):
    return length_inch * 25.4


class sb_disassembly_jigs:
    """
    A collection of simple shapes used to help disassemble a lathe for
    rebuild: a South Bend Model A Catalog No. 955Y from 1942
    """

    def __init__(self):
        pass

    def traverse_gear_support(self):
        """
        Stepped ring to support the traverse gear while I tap out its center
        pin. A cylindrical volume of 1.2" diameter to surround the gear and
        keep this support in the correct place, and a cylindrival volume of
        0.65" diameter to allow the pin to exit.
        """
        outer_radius = inch_to_mm(1.4) / 2
        gear_surround = (
            cq.Workplane("XY")
            .circle(radius=outer_radius)
            .circle(radius=inch_to_mm(1.2) / 2)
            .extrude(inch_to_mm(0.5))
        )

        pin_clear = (
            cq.Workplane("XY")
            .circle(radius=outer_radius)
            .circle(radius=inch_to_mm(0.65) / 2)
            .extrude(-inch_to_mm(1.3))
        )
        return gear_surround + pin_clear

    def reversing_gear_support(self):
        """
        Ring to support a reversing gear while I tap out its center pin,
        which should exit out the center hole.
        """
        # Measured dimensions of reversing gear and its pin
        gear_pitch_circle_diameter = inch_to_mm(1.578)
        pin_outer_diameter = inch_to_mm(0.752)
        height = inch_to_mm(0.9325)

        # Half of 3D printer nozzle diameter, in mm, for clearance
        clearance = 0.4

        # Calculated dimensions
        support_radius_outer = (gear_pitch_circle_diameter - clearance) / 2
        support_radius_inner = (pin_outer_diameter + clearance) / 2

        return (
            cq.Workplane("XY")
            .circle(radius=support_radius_outer)
            .circle(support_radius_inner)
            .extrude(height)
        )

    def worm_gear_pin_guide(self):
        """
        The apron worm gear is held by a collar, which is kept from rotating
        by a pin. The pin was supposed to "just tap out" and it did not. Now I
        will apply more force with a C-clamp.

        Worm gear collar exterior will have a smaller pin collar: inner hole
        to clear the pin with outer structure to support load between C-clamp
        and worm gear collar. Made of metal, turned on a lathe.

        Worm gear collar interior will have a push pin less than the worm gear
        collar pin of 0.125" diameter. This push pin transferring C-clamp force
        will also need to be metal for strength and turned on a lathe.

        Locating that inner push pin is this 3D-printed guide, which sits in
        the keyway to locate along one axis and flush against the collar end
        to locate along other axis.
        """

        # Measured dimensions, in decimal inches
        pin_diameter = 0.125
        pin_edge_to_collar_edge = 0.115
        keyway_width = 0.192
        keyway_depth = 0.065
        center_hole_diameter = 0.756

        # Half of 3D printer nozzle diameter, in mm, for clearance
        clearance = 0.2

        length_half = inch_to_mm(pin_edge_to_collar_edge + pin_diameter / 2)

        keyway = (
            cq.Workplane("YZ")
            .rect(
                xLen=inch_to_mm(keyway_width) - clearance,
                yLen=inch_to_mm(keyway_depth * 2),
            )
            .extrude(length_half, both=True)
        )

        lead_screw_hole = (
            cq.Workplane("YZ")
            .transformed(offset=(0, -inch_to_mm(center_hole_diameter / 2)))
            .circle(radius=(inch_to_mm(center_hole_diameter / 2)) - clearance)
            .extrude(length_half, both=True)
        )

        guide_intersect = (
            cq.Workplane("XY")
            .transformed(offset=(0, 0, -inch_to_mm(keyway_depth * 2)))
            .rect(xLen=length_half * 2, yLen=length_half * 2)
            .circle(radius=(inch_to_mm(pin_diameter) / 2) + clearance)
            .extrude(inch_to_mm(keyway_depth) * 3)
        )

        guide = (
            (keyway + lead_screw_hole).intersect(guide_intersect).edges("|Z").fillet(1)
        )

        return guide

    def worm_gear_hex_wrench_insert(self):
        """
        Apron worm gear is held in place by a collar that, once fastened, is
        kept from loosening with pin that worm_gear_pin_guide helps remove.
        Once pin is removed, the collar was supposed to turn, but it's hard
        to get a grip on the worm gear.

        This 3D-printed insert sits inside the worm gear. Its outer profile
        matches the leadscrew with key, and the inner profile is intended for
        a hex wrench. This allows us to turn the worm gear with a hex wrench
        to remove its collar.
        """
        # Half of 3D printer nozzle diameter, in mm, for clearance
        clearance = 0.2

        # Dimensions related to worm gear
        worm_gear_center_diameter = inch_to_mm(0.756)
        key_width = inch_to_mm(0.192)
        key_height = inch_to_mm(0.085)
        hex_wrench_hole_size = inch_to_mm(3 / 8) + clearance
        body_radius = (worm_gear_center_diameter - clearance) / 2

        # Desired size
        length = inch_to_mm(1 / 4)

        body = cq.Workplane("XY").circle(radius=body_radius).extrude(length, both=True)
        key = (
            cq.Workplane("XY")
            .transformed(offset=(body_radius, 0, 0))
            .rect(xLen=key_height * 2 - clearance, yLen=key_width - clearance)
            .extrude(length, both=True)
        )

        wrench = (
            cq.Workplane("XY")
            .polygon(nSides=6, diameter=hex_wrench_hole_size, circumscribed=True)
            .extrude(length, both=True)
        )

        insert = body + key - wrench

        return insert


jigs = sb_disassembly_jigs()

show_object(
    jigs.worm_gear_hex_wrench_insert(), options={"color": "green", "alpha": 0.5}
)
