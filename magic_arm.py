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

ball_diameter = 30

end_ball = (
    cq.Workplane("XY")
    .sphere(ball_diameter/2)
    )

end_ball_lug_side = 12.5
end_ball_lug_round_length = 5
end_ball_lug_transition = 5
end_ball_lug_square_length = 25
end_ball_lug = (
    cq.Workplane("XZ")
    .circle(end_ball_lug_side/2)
    .extrude(ball_diameter/2 + end_ball_lug_round_length)
    .faces("<Y")
    .circle(end_ball_lug_side/2)
    .workplane(offset=end_ball_lug_transition)
    .rect(end_ball_lug_side, end_ball_lug_side)
    .loft()
    .faces("<Y")
    .rect(end_ball_lug_side, end_ball_lug_side)
    .extrude(end_ball_lug_square_length)
    )

end_ball_lug_hole_offset = (
    10 +
    end_ball_lug_round_length +
    end_ball_lug_transition +
    ball_diameter/2
    )
end_ball_lug_hole_diameter = 9.5
end_ball_lug_hole = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(0, -end_ball_lug_hole_offset, 0))
    .circle(end_ball_lug_hole_diameter/2)
    .extrude(end_ball_lug_side, both=True)
    )

end_ball_lug_slot_width = 2
end_ball_lug_slot = (
    cq.Workplane("XZ")
    .transformed(offset=cq.Vector(0, 0, end_ball_lug_hole_offset))
    .rect(end_ball_lug_slot_width, end_ball_lug_side)
    .extrude(end_ball_lug_square_length)
    )

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

end_ball_assembly = (
    end_ball +
    end_ball_lug -
    end_ball_lug_hole -
    end_ball_lug_slot -
    end_ball_lug_fastener_clearance
    )


#################################################################################
# 2345678901234567890123456789012345678901234567890123456789012345678901234567890


show_object(end_ball_assembly)