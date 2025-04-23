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

    def __init__(self, hook_thickness=6):
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
        pass

    def hook(
        self,
        width=5,
        inside_leg=30,
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
            .extrude(-width)
        )

        hook_inner = (
            cq.Workplane("XZ")
            .transformed(rotate=cq.Vector(0, 0, -self.inside_slope_degrees))
            .line(-self.tray_lip_radius_inner, 0)
            .line(0, -inside_leg)
            .tangentArcPoint((-self.hook_thickness, 0))
            .line(0, inside_leg)
            .close()
            .extrude(-width)
        )

        hook_outer = (
            cq.Workplane("XZ")
            .line(self.tray_lip_radius_inner, 0)
            .line(0, -outside_leg)
            .tangentArcPoint((self.hook_thickness, 0))
            .line(0, outside_leg)
            .close()
            .extrude(-width)
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
            .extrude(-width)
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

    def end_plate(self, width=4, depth=0, height=30):
        """
        Blank plate that holds no tool to serve as end plate
        """
        hook = self.hook(
            width=width,
            inside_leg=height,
            outside_leg=1,
        )

        if depth > self.hook_thickness:
            reinforcement_leg = (
                cq.Workplane("XZ")
                .line(depth, 0)
                .line(0, -height - self.hook_top - self.hook_thickness / 2)
                .line(-depth, 0)
                .close()
                .extrude(-width)
                .faces("<Z")
                .edges("|Y")
                .fillet(depth / 2.1)
                .faces(">Z")
                .edges(">X")
                .fillet(depth / 2.1)
            )
            hook = hook + reinforcement_leg

        return (hook, width)

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

    def circular_opening(self, opening_radius, side_wall, height):
        """
        Single-piece clip with cylindrical opening
        """
        overall_width = opening_radius * 2 + side_wall * 2
        hook_main = self.hook(width=overall_width)

        body = (
            cq.Workplane("XY")
            .line(overall_width, 0)
            .line(0, -overall_width)
            .line(-overall_width, 0)
            .close()
            .extrude(-height)
            .edges("|Y")
            .fillet(self.hook_thickness / 2)
        )

        opening = (
            cq.Workplane("XY")
            .transformed(
                offset=cq.Vector(
                    side_wall + opening_radius, -side_wall - opening_radius, 0
                )
            )
            .circle(opening_radius)
            .extrude(-height)
        )

        return hook_main + body - opening

    def rectangular_opening_2piece(
        self, opening_width, opening_depth, side_wall, depth_wall, height
    ):
        """
        Two-piece clip with rectangular opening
        """
        main_width = opening_width + side_wall
        overall_width = opening_width + side_wall * 2
        overall_depth = opening_depth + depth_wall * 2

        hook_main = self.hook(width=main_width)

        hook_main_body = (
            cq.Workplane("XY")
            .line(overall_depth, 0)
            .line(0, -main_width)
            .line(-overall_depth, 0)
            .close()
            .extrude(-height)
            .edges("|Y")
            .fillet(self.hook_thickness / 2)
        )

        opening_clearance = (
            cq.Workplane("XY")
            .transformed(offset=(overall_width / 2, -overall_depth / 2))
            .rect(opening_width, opening_depth)
            .extrude(-height)
        )

        main = hook_main + hook_main_body - opening_clearance

        hook_side = self.hook(width=side_wall)
        hook_side_body = (
            cq.Workplane("XY")
            .line(overall_depth, 0)
            .line(0, -side_wall)
            .line(-overall_depth, 0)
            .close()
            .extrude(-height)
            .edges("|Y")
            .fillet(self.hook_thickness / 2)
        )

        side = hook_side + hook_side_body

        return (main, main_width, side)


def rotate_for_print(body):
    return body.rotate((0, 0, 0), (1, 0, 0), -90)


th = tool_hook(hook_thickness=10)
y_offset = 0

end_plate, end_plate_width = th.end_plate(depth=26)
y_offset -= end_plate_width
show_object(
    end_plate.translate((0, y_offset, 0)),
    options={"color": "red", "alpha": 0.5},
)

# show_object(
#     th.circular_opening(6, 2.4, 40).translate((0, y_offset, 0)),
#     options={"color": "orange", "alpha": 0.5},
# )
# y_offset = y_offset - 16.8

# duo = th.chuck_key_3jaw_2piece()
# show_object(
#     duo[0].translate((0, y_offset, 0)), options={"color": "white", "alpha": 0.5}
# )
# show_object(
#     duo[2].translate((0, y_offset - duo[1], 0)),
#     options={"color": "white", "alpha": 0.5},
# )

# y_offset = y_offset - 26

# show_object(
#     th.end_plate(depth=26).translate((0, y_offset, 0)),
#     options={"color": "green", "alpha": 0.5},
# )
