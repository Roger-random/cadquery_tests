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

    def __init__(self, hook_thickness=6, inside_leg_length=30):
        self.inside_slope_degrees = 23
        self.inside_slope_radians = math.radians(self.inside_slope_degrees)
        self.hook_thickness = hook_thickness
        self.tray_lip_radius_inner = 10
        self.tray_lip_radius_outer = self.tray_lip_radius_inner + self.hook_thickness
        self.threaded_rod_diameter_clear = 6.5
        self.hook_top = (
            self.tray_lip_radius_outer
            + self.threaded_rod_diameter_clear
            + self.hook_thickness
        )
        self.inside_leg_length = inside_leg_length
        self.hook_inner_x = (
            self.tray_lip_radius_outer * 2
            + self.inside_leg_length * math.sin(self.inside_slope_radians)
        )
        pass

    def hook(
        self,
        width=5,
        outside_leg=1,
        channel_right=False,
        rib_left=False,
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
            .extrude(width / 2, both=True)
        )

        hook_inner = (
            cq.Workplane("XZ")
            .transformed(rotate=cq.Vector(0, 0, -self.inside_slope_degrees))
            .line(-self.tray_lip_radius_inner, 0)
            .line(0, -self.inside_leg_length)
            .tangentArcPoint((-self.hook_thickness, 0))
            .line(0, self.inside_leg_length)
            .close()
            .extrude(width / 2, both=True)
        )

        hook_outer = (
            cq.Workplane("XZ")
            .line(self.tray_lip_radius_inner, 0)
            .line(0, -outside_leg)
            .tangentArcPoint((self.hook_thickness, 0))
            .line(0, outside_leg)
            .close()
            .extrude(width / 2, both=True)
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
            .extrude(width / 2, both=True)
        )

        # Assemble hook body from components
        hook = hook_top + hook_inner + hook_outer - rod_clearance

        # Final translation to ease adding tool-specific features
        hook = hook.translate(
            (
                -rod_center_x - self.threaded_rod_diameter_clear / 2,
                0,
                -rod_center_z
                - self.threaded_rod_diameter_clear / 2
                - self.hook_thickness,
            )
        )
        return hook

    def blank_holder(self, width=4, depth=0, additional_height=30):
        """
        Returns the blank holder volume that can be used as end plate
        but more typically a tool-specific cavity will be subtracted.
        """
        hook = self.hook(width=width)

        if depth > self.hook_thickness:
            reinforcement_leg = (
                cq.Workplane("XZ")
                .line(depth, 0)
                .line(0, -self.hook_top - additional_height)
                .line(-depth, 0)
                .close()
                .extrude(width / 2, both=True)
            )

            hook = hook + self.body_corner_roundoff(reinforcement_leg, depth)

        return (hook, width)

    def body_corner_roundoff(self, body, depth):
        """
        Fillet the outer corners to reduce liklihood of print lifting
        """
        return (
            body.faces("<Z")
            .edges("|Y")
            .fillet(depth / 2.01)
            .faces(">Z")
            .edges(">X")
            .fillet(depth / 2.01)
        )

    def chuck_key_3jaw_2piece(self):
        """
        Tool clip corresponding to custom-made 3-jaw chuck key
        """
        return self.rectangular_opening_2piece(
            opening_width=21,
            opening_depth=21,
            side_wall=2.5,
            depth_wall=2.5,
            height=100,
        )

    def circular_opening(
        self,
        opening_diameter,
        opening_height,
        taper_height,
        shaft_diameter,
        side_wall,
        depth_wall,
        additional_height,
    ):
        """
        Tool holder with cylindrical channel
        """

        opening_radius = opening_diameter / 2
        overall_width = opening_diameter + side_wall * 2
        overall_depth = opening_diameter + depth_wall * 2
        overall_height = self.hook_top + additional_height

        volume, volume_width = self.blank_holder(
            width=overall_width,
            depth=overall_depth,
            additional_height=additional_height,
        )

        subtract = (
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(opening_radius + depth_wall, 0, 0))
            .circle(opening_radius)
            .extrude(-opening_height)
            .faces("<Z")
            .workplane()
            .circle(opening_radius)
            .workplane(offset=taper_height)
            .circle(shaft_diameter / 2)
            .loft()
            .faces("<Z")
            .workplane()
            .circle(shaft_diameter / 2)
            .extrude(overall_height)
        )

        return volume - subtract

    def rectangular_opening(
        self,
        opening_width,
        opening_depth,
        opening_height,
        taper_height,
        channel_width,
        channel_depth,
        side_wall,
        depth_wall,
        additional_height,
    ):
        """
        Tool holder with rectangular channel
        """

        overall_width = opening_width + side_wall * 2
        overall_depth = opening_depth + depth_wall * 2

        volume, volume_width = self.blank_holder(
            width=overall_width,
            depth=overall_depth,
            additional_height=additional_height,
        )
        subtract = (
            cq.Workplane("XY")
            .rect(opening_depth, opening_width)
            .extrude(-opening_height)
            .faces("<Z")
            .workplane()
            .rect(opening_depth, opening_width)
            .workplane(offset=taper_height)
            .rect(channel_depth, channel_width)
            .loft()
            .faces("<Z")
            .workplane()
            .rect(channel_depth, channel_width)
            .extrude(additional_height + th.hook_top)
        )

        subtract = subtract.translate((depth_wall + opening_depth / 2, 0, 0))

        return volume - subtract

    def peg(
        self,
        peg_end_diameter,
        peg_length,
        peg_angle,
        side_margin,
    ):
        overall_width = peg_end_diameter + side_margin * 2
        peg_overall_length = self.hook_thickness + peg_length + peg_end_diameter / 2

        peg_hook = self.hook(width=overall_width, outside_leg=50)

        peg_hook = peg_hook.faces(">Z").edges(">X").fillet(th.hook_thickness * 0.9)

        peg_end = (
            cq.Workplane("YZ")
            .sphere(peg_end_diameter / 2)
            .translate((peg_overall_length, 0, 0))
        )

        peg_shaft = (
            cq.Workplane("YZ").circle(peg_end_diameter / 3).extrude(peg_overall_length)
        )

        peg = peg_end + peg_shaft

        peg = peg.translate((0, 0, -peg_end_diameter / 3)).rotate(
            (0, 0, 0), (0, 1, 0), -peg_angle
        )

        assembly = peg_hook + peg

        assembly = assembly.edges(
            sel.NearestToPointSelector(
                (self.hook_thickness, 0, -peg_end_diameter * 0.6)
            )
        ).fillet((overall_width - peg_end_diameter * 0.8) / 2)

        return assembly


def transform_for_display(
    body: cq.Shape, x_offset=0, y_offset=0, sides_on_bed=True, show_object_options=None
):
    left_split = body.workplane().split(keepTop=True)
    right_split = body.workplane().split(keepBottom=True)

    left_display = left_split.translate((0, y_offset, 0))
    right_display = right_split.translate((0, y_offset, 0))

    if sides_on_bed:
        left_print = left_split.rotate((0, 0, 0), (1, 0, 0), 90).translate(
            (-x_offset, 15, 0)
        )
        right_print = right_split.rotate((0, 0, 0), (1, 0, 0), -90).translate(
            (-x_offset, -15, 0)
        )
    else:
        left_print = left_split.rotate((0, 0, 0), (1, 0, 0), -90).translate(
            (-x_offset, -15, 0)
        )
        right_print = right_split.rotate((0, 0, 0), (1, 0, 0), 90).translate(
            (-x_offset, 15, 0)
        )

    if show_object_options:
        show_object(left_display, options=show_object_options)
        show_object(right_display, options=show_object_options)
        show_object(left_print, options=show_object_options)
        show_object(right_print, options=show_object_options)

    return (left_display, right_display, left_print, right_print)


def chuck_key_3_jaw(th: tool_hook):
    tool_holder = th.rectangular_opening(
        opening_width=27,
        opening_depth=27,
        opening_height=1,
        taper_height=10,
        channel_width=21,
        channel_depth=21,
        side_wall=3,
        depth_wall=3,
        additional_height=70,
    )

    transform_for_display(
        tool_holder,
        x_offset=th.hook_inner_x + 20,
        y_offset=0,
        sides_on_bed=True,
        show_object_options={"color": "green", "alpha": 0.5},
    )


def chuck_key_4_jaw(th: tool_hook):
    tool_holder = th.circular_opening(
        opening_diameter=20,
        opening_height=1,
        taper_height=30,
        shaft_diameter=12,
        side_wall=1,
        depth_wall=1,
        additional_height=50,
    )

    transform_for_display(
        tool_holder,
        x_offset=th.hook_inner_x + 20,
        y_offset=0,
        sides_on_bed=True,
        show_object_options={"color": "green", "alpha": 0.5},
    )


def hex_key_5_32(th: tool_hook):
    tool_holder = th.circular_opening(
        opening_diameter=15,
        opening_height=20,
        taper_height=30,
        shaft_diameter=5,
        side_wall=3,
        depth_wall=3,
        additional_height=50,
    )

    transform_for_display(
        tool_holder,
        x_offset=th.hook_inner_x + 20,
        y_offset=0,
        sides_on_bed=True,
        show_object_options={"color": "green", "alpha": 0.5},
    )


def hex_key_3_16(th: tool_hook):

    tool_holder = th.circular_opening(
        opening_diameter=18,
        opening_height=25,
        taper_height=30,
        shaft_diameter=6.5,
        side_wall=3,
        depth_wall=3,
        additional_height=50,
    )

    transform_for_display(
        tool_holder,
        x_offset=th.hook_inner_x + 20,
        y_offset=0,
        sides_on_bed=True,
        show_object_options={"color": "green", "alpha": 0.5},
    )


def end_plates(th: tool_hook):
    end_plate = th.hook(width=10, outside_leg=50)

    end_plate = end_plate.faces(">Z").edges(">X").fillet(th.hook_thickness * 0.9)

    transform_for_display(
        end_plate,
        x_offset=th.hook_inner_x + 20,
        y_offset=0,
        sides_on_bed=True,
        show_object_options={"color": "red", "alpha": 0.5},
    )


def peg_11_16(th: tool_hook):
    peg_hook = th.peg(peg_end_diameter=17, peg_length=15, peg_angle=15, side_margin=7)

    transform_for_display(
        peg_hook,
        x_offset=th.hook_inner_x + 20,
        y_offset=0,
        sides_on_bed=False,
        show_object_options={"color": "blue", "alpha": 0.5},
    )


def peg_7_8(th: tool_hook):
    peg_hook = th.peg(peg_end_diameter=22, peg_length=15, peg_angle=15, side_margin=5)

    transform_for_display(
        peg_hook,
        x_offset=th.hook_inner_x + 20,
        y_offset=0,
        sides_on_bed=False,
        show_object_options={"color": "blue", "alpha": 0.5},
    )


def mt2_chuck(th: tool_hook):
    tool_holder = th.circular_opening(
        opening_diameter=20,
        opening_height=1,
        taper_height=70,
        shaft_diameter=16,
        side_wall=18,
        depth_wall=3,
        additional_height=50,
    )

    transform_for_display(
        tool_holder,
        x_offset=th.hook_inner_x + 20,
        y_offset=0,
        sides_on_bed=True,
        show_object_options={"color": "green", "alpha": 0.5},
    )


def jacobs_chuck_key(th: tool_hook):
    tool_holder = th.circular_opening(
        opening_diameter=15.5,
        opening_height=1,
        taper_height=30,
        shaft_diameter=8.5,
        side_wall=4,
        depth_wall=3,
        additional_height=40,
    )

    transform_for_display(
        tool_holder,
        x_offset=th.hook_inner_x + 20,
        y_offset=0,
        sides_on_bed=True,
        show_object_options={"color": "green", "alpha": 0.5},
    )


th = tool_hook(hook_thickness=10)
jacobs_chuck_key(th)
