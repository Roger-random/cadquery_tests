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

"""
Experiment into designing a 3D-printable articulated arm mechanism that has
three joints that are all tightened/loosened simultaneously with a single
knob. Frequently seen sold as "Magic Arm". Larger units are sold for holding
photography equipment in place, smaller units can be found sold as indicator
holder for machinists.
"""

import math
import cadquery as cq

# The ball for the ball-and-socket joint at the effector end

ball_diameter = 20

end_ball = (
    cq.Workplane("XY")
    .sphere(ball_diameter/2)
    )

# The lug that will be added to the ball. This is the part that can be
# customized for different attachments. Example: dial indicator holder.
end_ball_lug_side = ball_diameter/math.sqrt(2)
end_ball_lug_round_diameter = 6
end_ball_lug_round_length = 5
end_ball_lug_transition = 6
end_ball_lug_square_length = 20

# The main lug shape
end_ball_lug = (
    cq.Workplane("XZ")
    .circle(end_ball_lug_round_diameter/2)
    .extrude(ball_diameter/2 + end_ball_lug_round_length)
    .faces("<Y")
    .circle(end_ball_lug_round_diameter/2)
    .workplane(offset=end_ball_lug_transition)
    .rect(end_ball_lug_side, end_ball_lug_side)
    .loft()
    .faces("<Y")
    .rect(end_ball_lug_side, end_ball_lug_side)
    .extrude(end_ball_lug_square_length)
    ).edges("|Y").fillet(1)

# Hole for dial indicator
end_ball_lug_hole_offset = (
    end_ball_lug_square_length +
    end_ball_lug_round_length +
    end_ball_lug_transition +
    ball_diameter/2 -
    end_ball_lug_side
    )
end_ball_lug_hole_diameter = 9.5

end_ball_lug_hole = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(0, -end_ball_lug_hole_offset, 0))
    .circle(end_ball_lug_hole_diameter/2)
    .extrude(end_ball_lug_side, both=True)
    )

# Slot allowing the lug to flex and clamp on indicator
end_ball_lug_slot_width = 2

end_ball_lug_slot = (
    cq.Workplane("XZ")
    .transformed(offset=cq.Vector(0, 0, end_ball_lug_hole_offset))
    .rect(end_ball_lug_slot_width, end_ball_lug_side)
    .extrude(end_ball_lug_square_length)
    )

# Clamping fastener
end_ball_lug_fastener_clearance_diameter = 3.5
end_ball_lug_fastener_clearance_offset = (
    end_ball_lug_square_length +
    end_ball_lug_round_length +
    end_ball_lug_transition +
    ball_diameter/2 -
    end_ball_lug_fastener_clearance_diameter * 1.5
    )

end_ball_lug_fastener_clearance = (
    cq.Workplane("YZ")
    .transformed(offset=cq.Vector(-end_ball_lug_fastener_clearance_offset, 0, 0))
    .circle(end_ball_lug_fastener_clearance_diameter/2)
    .extrude(end_ball_lug_side, both=True)
    )

# Assemble the end ball-and-socket
end_ball_assembly = (
    end_ball +
    end_ball_lug -
    end_ball_lug_hole -
    end_ball_lug_slot -
    end_ball_lug_fastener_clearance
    )

# Create the socket surrounind the ball
ball_surround_thickness = end_ball_lug_round_length
ball_surround_gap = 0.2
ball_surround_inner_radius = ball_surround_gap + ball_diameter/2
ball_surround_outer_radius = ball_surround_thickness + ball_diameter/2
ball_surround_inner_45 = ball_surround_inner_radius/math.sqrt(2)
ball_surround_outer_45 = ball_surround_outer_radius/math.sqrt(2)

ball_surround_outer = (
    cq.Workplane("YZ")
    .sphere(ball_surround_thickness + ball_diameter/2)
    )

# Cut a cone so the end lug can swivel around freely in a 90 degree cone
lug_clearance = (
    cq.Workplane("YZ")
    .lineTo(end_ball_lug_round_diameter/2, 0)
    .lineTo(-ball_diameter, ball_diameter + end_ball_lug_round_diameter/2)
    .lineTo(-ball_diameter, 0)
    .close()
    .revolve(360, (0,0,0), (1,0,0))
    )
ball_surround_outer = ball_surround_outer - lug_clearance

# Build the arm connecting to the ball joint
arm_length = 50
arm_side_outer = 17
rod_side = arm_side_outer - 5
arm_side_inner = rod_side + ball_surround_gap * 2

# Outer shell will link the ball-and-socket to center (mid) joint
arm_outer_shell = (
    cq.Workplane("XZ")
    .transformed(rotate=cq.Vector(0,0,45))
    .rect(arm_side_outer, arm_side_outer)
    .extrude(-arm_length)
    .edges("|Y")
    .fillet(2.5)
    )

# Channel inside for rod that transmits pushing force from mid joint to
# ball in socket
arm_actuating_rod_channel = (
    cq.Workplane("XZ")
    .transformed(rotate=cq.Vector(0,0,45))
    .rect(arm_side_inner, arm_side_inner)
    .extrude(9-arm_length)
    )

# Rod that transmits pushing force from mid joint to ball in socket
arm_actuating_rod = (
    cq.Workplane("XZ")
    .transformed(rotate=cq.Vector(0,0,45))
    .rect(rod_side, rod_side)
    .extrude(1-arm_length)
    )

# The actual "socket" part of ball and socket
arm_end_ball_cavity = (
    cq.Workplane("YZ")
    .sphere(ball_surround_gap + ball_diameter/2)
    )

# Build the center/mid joint
mid_joint_diameter = 40
mid_joint_shell_perimeter = 2.4
mid_joint_shell_bottom = 1
arm_side_height = arm_side_outer / math.sin(math.radians(45))

# External cylinder that will be joined with arm outer shell
mid_joint_external = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(
        0,
        arm_length,
        -arm_side_height/2))
    .circle(mid_joint_diameter/2)
    .extrude(arm_side_height)
    )

# Internal volume for the joint cone pressure mechanism
mid_joint_internal = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(
        0,
        arm_length,
        mid_joint_shell_bottom - end_ball_lug_side/2))
    .circle(mid_joint_diameter/2 - mid_joint_shell_perimeter)
    .extrude(ball_surround_outer_radius + end_ball_lug_side/2)
    )

# Pressure angle on the cone
mid_joint_cone_angle_radians = math.radians(30)

mid_joint_cone = (
    cq.Workplane("YZ")
    .transformed(offset=cq.Vector(arm_length, 0, 0))
    .lineTo(0, ball_surround_outer_radius, forConstruction = True)
    .lineTo(mid_joint_diameter/2 -
            mid_joint_shell_perimeter,
            ball_surround_outer_radius)
    .lineTo(mid_joint_diameter/2 -
            mid_joint_shell_perimeter -
            math.tan(mid_joint_cone_angle_radians) * ball_surround_outer_radius,
            -ball_surround_outer_radius)
    .lineTo(0, -ball_surround_outer_radius)
    .close()
    .revolve(360, (0,0,0),(0,1,0))
    )

# Static ramp inside mid joint to push against cone
mid_joint_ramp_vertical_offset = -1.5
mid_joint_ramp_height = end_ball_lug_side + mid_joint_ramp_vertical_offset*2
mid_joint_ramp = (
    cq.Workplane("XZ")
    .transformed(offset=cq.Vector(0, mid_joint_ramp_vertical_offset, -arm_length))
    .rect(end_ball_lug_side, mid_joint_ramp_height)
    .extrude(-mid_joint_diameter/2)
    ) - mid_joint_cone

mid_joint_internal = (
    mid_joint_internal -
    mid_joint_ramp.rotate((0, arm_length, 0), (0, arm_length, 1), 60) -
    mid_joint_ramp.rotate((0, arm_length, 0), (0, arm_length, 1), -60)
    )

# Fastener through center of mid joint.
mid_joint_fastener_diameter = 6.5
mid_joint_fastener_clearance = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(0, arm_length, 0))
    .circle(mid_joint_fastener_diameter/2)
    .extrude(ball_surround_outer_radius, both=True)
    )

# We only need a subset of the cone used in geometrical construction, a function
# of the range of motion we need to make the arm work.
cone_range_of_motion = 2
cone_thickness = mid_joint_ramp_height - mid_joint_shell_bottom
cone_center_hole_radius = cone_range_of_motion + mid_joint_fastener_diameter/2

cone_slice = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(
        0,
        arm_length,
        mid_joint_shell_bottom + cone_range_of_motion - end_ball_lug_side/2))
    .circle(mid_joint_diameter/2)
    .circle(cone_center_hole_radius)
    .extrude(cone_thickness)
    )

# Take up some slack already in the actuating rod that exists to help printing.
rod_actuation_preload = 1
arm_actuating_rod = (
    arm_actuating_rod -
    mid_joint_cone.translate((0,rod_actuation_preload,0))
    )

# Clearance between actuation rod and knob
knob_height = 20
knob_bottom = 0.6

knob_volume = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(
        0,
        arm_length,
        mid_joint_ramp_height/2 + mid_joint_ramp_vertical_offset))
    .circle(mid_joint_diameter/2 - mid_joint_shell_perimeter)
    .extrude(knob_height)
    )
arm_actuating_rod = (
    arm_actuating_rod -
    knob_volume
    )

# Assemble half of the arm. Print this twice for the three-jointed mechanism.
arm = (
    ball_surround_outer +
    arm_outer_shell +
    mid_joint_external -
    mid_joint_internal -
    mid_joint_fastener_clearance -
    arm_actuating_rod_channel +
    arm_actuating_rod -
    arm_end_ball_cavity
    )

pressure_cone = mid_joint_cone.intersect(cone_slice)
show_object(pressure_cone, options={"color":"red","alpha":0.5})

knob_hex_head = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(
        0,
        arm_length,
        mid_joint_ramp_height/2 + mid_joint_ramp_vertical_offset + knob_bottom))
    .polygon(6, 11, circumscribed = True)
    .extrude(knob_height)
    )

knob = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(
        0,
        arm_length,
        mid_joint_ramp_height/2 + mid_joint_ramp_vertical_offset))
    .polygon(12,
        mid_joint_diameter - mid_joint_shell_perimeter*2,
        circumscribed = False)
    .circle(mid_joint_fastener_diameter/2)
    .extrude(knob_height)
    .faces(">Z")
    .fillet(2)
    ) - knob_hex_head

show_object(knob, options={"color":"green","alpha":0.5})

combined = end_ball_assembly + arm

chop = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(0,0,-ball_diameter/(2*math.sqrt(2))))
    .rect(arm_length*3,arm_length*3)
    .extrude(-ball_surround_outer_radius)
    )
show_object(combined - chop, options={"color":"blue", "alpha":0.5})

#################################################################################
# Tooling
cone_lathe_base = (
    cq.Workplane("XY")
    .circle(12)
    .circle(mid_joint_fastener_diameter/2)
    .extrude(-20)
    .faces(">Z").workplane()
    .circle(cone_center_hole_radius)
    .circle(mid_joint_fastener_diameter/2)
    .extrude(cone_thickness-0.5)
    )

cone_lathe_base_hex_head = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(
        0,
        0,
        cone_thickness-20))
    .polygon(6, 11, circumscribed = True)
    .extrude(-40)
    )

cone_lathe_base = cone_lathe_base - cone_lathe_base_hex_head
show_object(cone_lathe_base.translate((0,arm_length,-ball_surround_outer_radius*3)), options={"color":"yellow", "alpha":0.5})

# This is really just a big washer, but I don't have a metal one handy
cone_lathe_disc = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(
        0,
        0,
        cone_thickness+5))
    .circle(10)
    .circle(mid_joint_fastener_diameter/2)
    .extrude(3)
    )

show_object(cone_lathe_disc.translate((0,arm_length,-ball_surround_outer_radius*3)), options={"color":"yellow", "alpha":0.5})

# 2345678901234567890123456789012345678901234567890123456789012345678901234567890
