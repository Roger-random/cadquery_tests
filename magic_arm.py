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
ball_surround_gap = 0.25
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
#show_object(ball_surround_outer, options={"color":"red","alpha":0.5})

# Build the arm connecting to the ball joint
arm_length = 100
arm_side_outer = 17
rod_side = arm_side_outer - 5
arm_side_inner = rod_side + ball_surround_gap * 2

arm_outer_shell = (
    cq.Workplane("XZ")
    .transformed(rotate=cq.Vector(0,0,45))
    .rect(arm_side_outer, arm_side_outer)
    .extrude(-arm_length)
    .edges("|Y")
    .fillet(2.5)
    )

arm_actuating_rod_channel = (
    cq.Workplane("XZ")
    .transformed(rotate=cq.Vector(0,0,45))
    .rect(arm_side_inner, arm_side_inner)
    .extrude(9-arm_length)
    )

arm_actuating_rod = (
    cq.Workplane("XZ")
    .transformed(rotate=cq.Vector(0,0,45))
    .rect(rod_side, rod_side)
    .extrude(1-arm_length)
    )

arm_end_ball_cavity = (
    cq.Workplane("YZ")
    .sphere(ball_surround_gap + ball_diameter/2)
    )

mid_joint_diameter = 40
mid_joint_shell_thickness = 2.4
mid_joint_external = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(0, arm_length, -ball_surround_outer_radius))
    .circle(mid_joint_diameter/2)
    .extrude(ball_surround_outer_radius * 2)
    )

mid_joint_internal = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(0, arm_length, mid_joint_shell_thickness - end_ball_lug_side/2))
    .circle(mid_joint_diameter/2 - mid_joint_shell_thickness)
    .extrude(ball_surround_outer_radius + end_ball_lug_side/2)
    )

mid_joint_cone_angle_radians = math.radians(30)
mid_joint_cone = (
    cq.Workplane("YZ")
    .transformed(offset=cq.Vector(arm_length, 0, 0))
    .lineTo(0, ball_surround_outer_radius, forConstruction = True)
    .lineTo(mid_joint_diameter/2 -
            mid_joint_shell_thickness,
            ball_surround_outer_radius)
    .lineTo(mid_joint_diameter/2 -
            mid_joint_shell_thickness -
            math.tan(mid_joint_cone_angle_radians) * ball_surround_outer_radius,
            -ball_surround_outer_radius)
    .lineTo(0, -ball_surround_outer_radius)
    .close()
    .revolve(360, (0,0,0),(0,1,0))
    )

mid_joint_ramp = (
    cq.Workplane("XZ")
    .transformed(offset=cq.Vector(0, 0, -arm_length))
    .rect(end_ball_lug_side, end_ball_lug_side)
    .extrude(-mid_joint_diameter/2)
    ) - mid_joint_cone

mid_joint_internal = (
    mid_joint_internal -
    mid_joint_ramp.rotate((0, arm_length, 0), (0, arm_length, 1), 60) -
    mid_joint_ramp.rotate((0, arm_length, 0), (0, arm_length, 1), -60)
    )

mid_joint_fastener_diameter = 6.25
mid_joint_fastener_clearance = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(0, arm_length, 0))
    .circle(mid_joint_fastener_diameter/2)
    .extrude(ball_surround_outer_radius, both=True)
    )

rod_actuation_preload = 1
arm_actuating_rod = (
    arm_actuating_rod -
    mid_joint_cone.translate((0,rod_actuation_preload,0))
    )

#show_object(mid_joint_ramp.rotate((0, arm_length, 0), (0, arm_length, 1), 60), options={"color":"green","alpha":0.5})

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

#################################################################################
# 80 columns
# 2345678901234567890123456789012345678901234567890123456789012345678901234567890

combined = end_ball_assembly + arm

chop = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(0,0,-ball_diameter/(2*math.sqrt(2))))
    .rect(arm_length*3,arm_length*3)
    .extrude(-ball_surround_outer_radius)
    )
show_object(combined - chop, options={"color":"blue", "alpha":0.5})
