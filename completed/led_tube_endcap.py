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


class led_tube_endcap:
    """
    Reusing components of a LED light that has the form factor of a fluorescent
    tube. The LED PCB strip is inside a plastic tube acting as diffuser, and
    now it needs 3D printed endcaps to cover either end of the tube and also
    provide mounting screw locations.
    """

    def __init__(self):
        self.radius_inner = 13.8
        self.ring_thickness = 1.6
        self.radius_outer = self.radius_inner + self.ring_thickness
        self.flat_truncation = 3
        self.ring_thickness = 2.4
        self.ring_length = 10
        self.plate_thickness = 0.6
        self.mount_width_half = 30
        self.fastener_radius = 2
        self.slot_center_x = 1.5
        self.slot_height = 6

    def cap(self, wire_slot: bool):
        ring = (
            cq.Workplane("YZ")
            .circle(radius=self.radius_outer)
            .circle(radius=self.radius_inner)
            .extrude(self.ring_length)
        )
        plate = (
            cq.Workplane("YZ")
            .circle(radius=self.radius_outer)
            .extrude(self.plate_thickness)
        )
        mount = (
            cq.Workplane("YZ")
            .lineTo(
                self.mount_width_half,
                self.radius_inner - self.flat_truncation,
                forConstruction=True,
            )
            .lineTo(self.mount_width_half, self.radius_outer)
            .lineTo(-self.mount_width_half, self.radius_outer)
            .lineTo(-self.mount_width_half, self.radius_inner - self.flat_truncation)
            .close()
            .extrude(self.ring_length)
        )
        fastener_subtract = (
            cq.Workplane("XY")
            .transformed(
                offset=(
                    self.ring_length / 2,
                    self.mount_width_half - self.ring_length / 2,
                    self.radius_inner - self.flat_truncation / 2,
                )
            )
            .circle(self.fastener_radius)
            .extrude(self.radius_inner, both=True)
        )

        cap = ring + plate + mount - fastener_subtract - fastener_subtract.mirror("XZ")

        if wire_slot:
            slot_subtract = (
                cq.Workplane("YZ")
                .lineTo(
                    -self.slot_center_x,
                    self.radius_inner - self.flat_truncation - self.slot_height,
                    forConstruction=True,
                )
                .line(self.slot_center_x * 4, 0)
                .line(0, self.radius_outer)
                .line(-self.slot_center_x * 4, 0)
                .close()
                .extrude(self.ring_length * 1.1, both=True)
            )
            cap = cap - slot_subtract

        cap = cap.edges("|X").fillet(2).faces("<X or >X").chamfer(0.5)

        return cap


tl = led_tube_endcap()
show_object(
    tl.cap(wire_slot=True),
    options={"color": "green", "alpha": 0.5},
)
