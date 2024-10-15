"""
Tail stock wrench

According to pictures, a Logan 955 was supposed to come with a small handle
to tighten the tailstock holding nut. It is a 7/8" nut so I could use a
normal wrench but a short handle would be more convenient in the tight
space. It doesn't take a lot of torque to keep the tailstock in place so a
3D printed replacement may suffice.

This is designed upside-down in order to present a flat bottom surface for
3D printing. There's probably a better way to approach the problem but it
works for now.
"""

import cadquery as cq

# Old lathe made in 1951 measures in inches but CadQuery works in mm.
mm_per_inch = 25.4

# Give an additional 0.2mm of space on mating surface dimensions to account
# for 3D printing inaccuracy
additional_clearance = 0.25

# Mitigate 3D printing elephant foot effect
elephant_foot_compensation = 0.5

# Wrench dimensions
nut_size_inch = 7/8
nut_size = 7/8 * mm_per_inch + additional_clearance * 2 # Apply clearance distance twice for diameter

wrench_width = nut_size + 15
wrench_height = 15
wrench_length = 70

handle_radius = 10
handle_end_fillet = handle_radius - 1
handle_join_fillet = 6

handle_to_socket_angle = 5

handle = (
    cq.Workplane("XZ")
    .circle(handle_radius)
    .extrude(-wrench_length)
    .faces(">Y")
    .fillet(handle_end_fillet)
    )

socket = (
    cq.Workplane("XY")
    .transformed(rotate=cq.Vector(handle_to_socket_angle,0,0))
    .circle(wrench_width/2)
    .extrude(wrench_height, both=True)
    )

wrench = socket + handle

# slice off the unnecessary bottom part
wrench = (
    wrench.workplane()
    .transformed(
        rotate=cq.Vector(-handle_to_socket_angle,0,0),
        offset=cq.Vector(0,0,-2))
    .split(keepTop = True, keepBottom = False)
    )

# Fillet edge where socket and handle join
socket_handle_join_edge = wrench.edges(cq.selectors.NearestToPointSelector(
    (0, wrench_width/2, handle_radius)))
#show_object(socket_handle_join_edge)
wrench = socket_handle_join_edge.fillet(handle_join_fillet)

# Cut hole for nut
wrench = (
    wrench.faces(">Z").workplane()
    .polygon(6, nut_size, circumscribed=True)
    .cutThruAll()
    )

# Unexpected behavior: fillet works here but chamfer does not. I don't understand
# enough to know if this is my bug or a CadQuery bug.
wrench = wrench.faces("<Z or >Z").fillet(elephant_foot_compensation)

show_object(wrench)

