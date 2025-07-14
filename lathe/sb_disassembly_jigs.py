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

        Result: Succes!
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

    def cross_feed_drive_pin_support(self):
        """
        Tube to support the apron casting as I tap out the cross-feed drive
        gear axle pin. Tube width is smaller to clear drive select gear for
        the topmost 1/2" but then widens for more strength for its 2.3" length

        Result: Success!
        """
        cone = (
            cq.Workplane("XY")
            .circle(radius=inch_to_mm(1.25))
            .workplane(offset=inch_to_mm(2.3 - 0.5))
            .circle(radius=inch_to_mm(0.5))
            .loft()
            .faces(">Z")
            .workplane()
            .circle(radius=inch_to_mm(0.5))
            .extrude(inch_to_mm(0.5))
        )

        pin_clear = (
            cq.Workplane("XY")
            .circle(radius=inch_to_mm(0.65) / 2)
            .extrude(inch_to_mm(2.3))
        )

        support = cone - pin_clear

        return support

    def compound_collet_support(self):
        """
        After the compound collet was removed, the handcrank stayed attached
        via a stubborn retaining nut. This shape supports the hand crank
        collar so the retaining nut can be loosened with an impact driver

        Result: Success!
        """
        base = (
            cq.Workplane("XY").rect(xLen=60, yLen=40).extrude(50).edges("|Z").fillet(5)
        )
        channel = (
            cq.Workplane("XY")
            .transformed(offset=(0, 0, 35))
            .rect(xLen=60, yLen=16)
            .extrude(20)
        )
        thread_clear = cq.Workplane("XY").circle(radius=15 / 2).extrude(50)
        dial_clear = (
            cq.Workplane("XY")
            .transformed(offset=(0, 0, 20))
            .circle(radius=27 / 2)
            .extrude(30)
        )

        support = base - channel - thread_clear - dial_clear

        return support

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

        Results: Success!
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

    def worm_gear_hex_wrench_insert(
        self,
        length=inch_to_mm(1 / 4),
    ):
        """
        Apron worm gear is held in place by a collar that, once fastened, is
        kept from loosening with pin that worm_gear_pin_guide helps remove.
        Once pin is removed, the collar was supposed to turn, but it's hard
        to get a grip on the worm gear.

        This 3D-printed insert sits inside the worm gear. Its outer profile
        matches the leadscrew with key, and the inner profile is intended for
        a hex wrench. This allows us to turn the worm gear with a hex wrench
        to remove its collar.

        Results: Success!
        """
        # Half of 3D printer nozzle diameter, in mm, for clearance
        clearance = 0.2

        # Dimensions related to worm gear
        worm_gear_center_diameter = inch_to_mm(0.756)
        key_width = inch_to_mm(0.192)
        key_height = inch_to_mm(0.085)
        hex_wrench_hole_size = inch_to_mm(3 / 8) + clearance
        body_radius = (worm_gear_center_diameter - clearance) / 2

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

    def worm_gear_cleanup_arbor(self):
        """
        Worm gear hex wrench insert helped remove the collar, and now I have
        a worm gear to clean. Laziness dictates that I enlist machinery help,
        so this arbor is intended to help hold the worm gear and rotate it
        so I can clean its circumference. Has a small T shape on one end to
        help rubber band hold the hex wrench in place.

        Results: The rubber band idea did not work, I snapped off the T end
        and continued working with the remainder of the arbor.
        """
        center = self.worm_gear_hex_wrench_insert(length=inch_to_mm(2))

        hook_radius_outer = inch_to_mm(1)
        hook_radius_inner = inch_to_mm(0.2)
        hook_length = inch_to_mm(0.25)
        hook_width = inch_to_mm(0.25)
        hook_lip = inch_to_mm(0.25)

        hook = (
            cq.Workplane("XZ")
            .transformed(offset=(0, -inch_to_mm(2), 0))
            .lineTo(hook_radius_inner, 0, forConstruction=True)
            .lineTo(hook_radius_outer, 0)
            .line(0, hook_length + hook_lip)
            .line(-hook_lip, 0)
            .line(0, -hook_lip)
            .lineTo(hook_radius_inner, hook_length)
            .close()
            .extrude(hook_width, both=True)
            .faces(">X")
            .edges("|Z")
            .fillet(2)
        )

        arbor = center + hook + hook.mirror("YZ")

        return arbor

    def lead_screw_wrench(self):
        """
        The worm gear hex wrench insert lets me pretend to be the lead screw
        turning the worm gear. This is the inverse: a 3D printed part that
        lets me pretend to be the worm gear applying torque against the lead
        screw.

        Results: This did not work. Torque involved quickly sheared off the
        pretend key.
        """

        # Half of 3D printer nozzle diameter, in mm, for clearance
        clearance = 0.2

        # Dimensions related to worm gear
        worm_gear_center_diameter = inch_to_mm(0.756)
        key_width = inch_to_mm(0.192)
        key_height = inch_to_mm(0.085)
        body_radius = (worm_gear_center_diameter / 2) + clearance
        thickness_half = inch_to_mm(1 / 4)
        handle_length = inch_to_mm(4)
        wrench_radius = inch_to_mm(0.75)

        hole = (
            cq.Workplane("XY")
            .circle(radius=body_radius)
            .extrude(thickness_half, both=True)
        )
        key = (
            cq.Workplane("XY")
            .transformed(offset=(body_radius, 0, 0))
            .rect(xLen=key_height * 2 - clearance, yLen=key_width - clearance)
            .extrude(thickness_half, both=True)
        )

        body_end = (
            cq.Workplane("XY")
            .circle(radius=wrench_radius)
            .extrude(thickness_half, both=True)
        )
        body_center = cq.Workplane("XY").box(
            length=handle_length,
            width=wrench_radius * 2,
            height=thickness_half * 2,
            centered=(False, True, True),
        )

        body = body_end + body_center + body_end.translate((handle_length, 0, 0))

        wrench = body - hole + key

        return wrench

    def thin_crescent_wrench(self):
        """
        Quick change gearbox holds the leadscrew in place with two hex nuts
        jammed together. They are 7/8" nuts thinner than my 7/8" wrench so
        I couldn't grip the inner one. Let's see if a 3D printed thin wrench
        is strong enough for the job. If not, I'll have to go out and buy
        a cheap 7/8" wrench and grind it down.

        Results: This did not work, but I was able to remove the nuts one
        at a time: outer nut first, then inner nut, with my too-wide wrench.
        """
        clearance = 0.2
        thickness = inch_to_mm(1 / 4) - clearance
        fastener = inch_to_mm(7 / 8) - clearance
        length = inch_to_mm(3)
        width = fastener + inch_to_mm(3 / 4)

        end = (
            cq.Workplane("XY")
            .circle(radius=width / 2)
            .extrude(thickness / 2, both=True)
        )
        handle = (
            cq.Workplane("XY")
            .box(length=length, width=width, height=thickness)
            .translate((-length / 2, 0, 0))
        )

        nut = (
            cq.Workplane("XY")
            .polygon(nSides=6, diameter=fastener, circumscribed=True)
            .extrude(thickness / 2, both=True)
            .rotate((0, 0, 0), (0, 0, 1), 360 / 12)
        )

        entry_x = width * math.sin(math.radians(30))
        entry_y = width * math.cos(math.radians(30))
        entry = (
            cq.Workplane("XY")
            .lineTo(entry_x, entry_y)
            .lineTo(entry_x * 2, 0)
            .lineTo(entry_x, -entry_y)
            .close()
            .extrude(thickness / 2, both=True)
        )

        body = end + handle + end.translate((-length, 0, 0)) - nut - entry

        wrench = body.edges("|Z").fillet(2)

        return wrench


jigs = sb_disassembly_jigs()

show_object(jigs.thin_crescent_wrench(), options={"color": "green", "alpha": 0.5})
