"""
Tail stock wrench

According to pictures, a Logan 955 was supposed to come with a small handle
to tighten the tailstock holding nut. It is a 7/8" nut so I could use a
normal wrench but a short handle would be more convenient in the tight
space. It doesn't take a lot of torque to keep the tailstock in place so a
3D printed replacement may suffice.
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

handle = (
    cq.Workplane("XZ")
    .circle(handle_radius)
    .extrude(-wrench_length)
    .faces(">Y")
    .fillet(handle_end_fillet)
    )

socket = (
    cq.Workplane("XY")
    .transformed(rotate=cq.Vector(5,0,0))
    .circle(wrench_width/2)
    .extrude(wrench_height, both=True)
    )

wrench = socket + handle

# slice off the unnecessary bottom part
sliceoff = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(0,0,-wrench_height-3))
    .box(wrench_length*3, wrench_length*3, wrench_height*2)
    )
wrench = wrench - sliceoff

# Fillet edge where socket and handle join
wrench = (
    wrench.edges(cq.selectors.NearestToPointSelector(
        (0, wrench_width/2, handle_radius)))
    .fillet(handle_join_fillet)
    )

# Cut hole for nut
wrench = (
    wrench.faces(">Z").workplane()
    .polygon(6, nut_size, circumscribed=True)
    .cutThruAll()
    )

wrench = wrench.faces("<Z or >Z").fillet(elephant_foot_compensation)

show_object(wrench)

