"""
MIT License

Copyright (c) 2024 Roger Cheng

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


class tool_hook:
    """
    3D printed hook to hold a tool over the edge of the work table for a
    Logan 555 lathe
    """

    def __init__(self, channel_size=2):
        nozzle_diameter = 0.4
        self.channel_size = channel_size
        self.inside_slope_degrees = 23
        self.inside_slope_radians = math.radians(self.inside_slope_degrees)
        self.hook_thickness = nozzle_diameter * 8
        self.tray_lip_radius_inner = 10
        self.tray_lip_radius_outer = self.tray_lip_radius_inner + self.hook_thickness
        self.threaded_rod_diameter_clear = 6.5
        self.hook_top = (
            self.tray_lip_radius_outer
            + self.threaded_rod_diameter_clear
            + self.hook_thickness
        )
        pass

    def hook(
        self,
        width=5,
        inside_leg=30,
        outside_leg=30,
        channel_right=True,
        rib_left=True,
    ):
        blend_length = 10
        blend_x = blend_length * math.cos(self.inside_slope_radians)
        blend_y = blend_length * math.sin(self.inside_slope_radians)
        hook_top = (
            cq.Workplane("XZ")
            .line(self.tray_lip_radius_inner, 0, forConstruction=True)
            .line(self.hook_thickness, 0)
            .line(0, self.hook_top)
            .line(-self.hook_thickness, 0)
            .bezier(
                [
                    (self.tray_lip_radius_inner, self.hook_top),
                    (0, self.hook_top),
                    (
                        -self.tray_lip_radius_outer
                        * math.cos(self.inside_slope_radians)
                        + blend_y,
                        self.tray_lip_radius_outer * math.sin(self.inside_slope_radians)
                        + blend_x,
                    ),
                    (
                        -self.tray_lip_radius_outer
                        * math.cos(self.inside_slope_radians),
                        self.tray_lip_radius_outer
                        * math.sin(self.inside_slope_radians),
                    ),
                ]
            )
            .lineTo(
                -self.tray_lip_radius_inner * math.cos(self.inside_slope_radians),
                self.tray_lip_radius_inner * math.sin(self.inside_slope_radians),
            )
            .radiusArc(
                (self.tray_lip_radius_inner, 0),
                self.tray_lip_radius_inner,
            )
            .close()
            .extrude(width)
        )

        hook_inner = (
            cq.Workplane("XZ")
            .transformed(rotate=cq.Vector(0, 0, -self.inside_slope_degrees))
            .line(-self.tray_lip_radius_inner, 0)
            .line(0, -inside_leg)
            .tangentArcPoint((-self.hook_thickness, 0))
            .line(0, inside_leg)
            .close()
            .extrude(width)
        )

        hook_outer = (
            cq.Workplane("XZ")
            .line(self.tray_lip_radius_inner, 0)
            .line(0, -outside_leg)
            .tangentArcPoint((self.hook_thickness, 0))
            .line(0, outside_leg)
            .close()
            .extrude(width)
        )

        rod_center_x = self.tray_lip_radius_inner - self.threaded_rod_diameter_clear / 2
        rod_center_z = self.tray_lip_radius_outer + self.threaded_rod_diameter_clear / 2
        rod_clearance = (
            cq.Workplane("XZ")
            .transformed(
                offset=cq.Vector(
                    rod_center_x,
                    rod_center_z,
                    0,
                )
            )
            .circle(self.threaded_rod_diameter_clear / 2)
            .extrude(width)
        )

        # Assemble hook body from components
        hook_body = hook_top + hook_inner + hook_outer - rod_clearance

        # Translate to add alignment ribs/channels
        hook_body = hook_body.translate((-rod_center_x, 0, -rod_center_z))

        vertical_channel_subtract = (
            cq.Workplane("XY")
            .line(self.channel_size, 0)
            .line(-self.channel_size, -self.channel_size)
            .line(-self.channel_size, self.channel_size)
            .close()
            .extrude(-50)
        )

        horizontal_channel_subtract = (
            cq.Workplane("YZ")
            .line(0, self.channel_size)
            .line(-self.channel_size, -self.channel_size)
            .line(self.channel_size, -self.channel_size)
            .close()
            .extrude(-50)
        )

        hook = hook_body

        if rib_left:
            vertical_rib_add = hook_body.intersect(vertical_channel_subtract).translate(
                (0, -width, 0)
            )
            horizontal_rib_add = hook_body.intersect(
                horizontal_channel_subtract
            ).translate((0, -width, 0))
            hook = hook + vertical_rib_add + horizontal_rib_add

        if channel_right:
            hook = hook - vertical_channel_subtract - horizontal_channel_subtract

        # Final translation to ease adding tool-specific features
        hook = hook.translate(
            (
                -self.threaded_rod_diameter_clear / 2,
                0,
                -self.threaded_rod_diameter_clear / 2 - self.hook_thickness,
            )
        )
        return hook

    def plate_left(self):
        """
        Blank plate that holds no tool but has channels on the right side
        to accommodate adjacent holder rib. Presents a flat surface on the
        left, no rib.
        """
        return self.hook(
            width=self.channel_size * 2,
            inside_leg=self.hook_thickness / 2,
            outside_leg=self.hook_thickness / 2,
            channel_right=True,
            rib_left=False,
        )

    def plate_right(self):
        """
        Blank plate that holds no tool but has ribs on the left side
        to mesh with adjacent holder rib channel. Presents a flat surface on
        the right with no channel.
        """
        return self.hook(
            width=self.channel_size * 2,
            inside_leg=self.hook_thickness / 2,
            outside_leg=self.hook_thickness / 2,
            channel_right=False,
            rib_left=True,
        )

    def rotate_for_print(self, body):
        return body.rotate((0, 0, 0), (1, 0, 0), -90)


th = tool_hook()
show_object(th.hook(), options={"color": "white", "alpha": 0.5})

show_object(
    th.plate_left().translate((0, -5, 0)), options={"color": "green", "alpha": 0.5}
)
show_object(
    th.plate_right().translate((0, th.channel_size * 2, 0)),
    options={"color": "red", "alpha": 0.5},
)
