"""
Spindle end ring wrench
"""

import cadquery as cq
from spindle_end_ring import make_spindle_end_ring, inner_radius, outer_radius, tab_length

# Old lathe made in 1951 measures in inches but CadQuery works in mm.
mm_per_inch = 25.4

# Give an additional 0.2mm of space on mating surface dimensions to account
# for 3D printing inaccuracy
additional_clearance = 0.2

chamfer_size = 0.5

# Plate dimensions
handle_width = 30
handle_length = 200

ring = make_spindle_end_ring()

# Add a handle
handle = (
    cq.Workplane("XY")
    .center(inner_radius+handle_length/2,0)
    .box(handle_length, handle_width, tab_length)
    )

# Round off end of the handle
handle = (
    handle.edges("|Z").edges(">X")
    .fillet(handle_width/2 - 1)
    )

wrench = ring + handle

# Round off where handle joins the ring
join_edges = (
    wrench
    .edges(cq.selectors.BoxSelector(
        (inner_radius+1, handle_width, tab_length),
        (outer_radius+1, -handle_width, -tab_length)
        ))
    )
wrench = join_edges.fillet(handle_width)

# Rotate to sit diagonally on print bed
wrench = wrench.rotate((0,0,0),(0,0,1),40)

wrench = wrench.faces("<Z or >Z").chamfer(chamfer_size)

show_object(wrench)
