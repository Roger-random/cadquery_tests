"""
Spindle end adapter

The old lathe came with some nonstandard attachment at the end of its spindle
whose purpose is currently unknown and blocks gearbox access cover from
swinging open. (Gearbox access cover can still be unbolted to access gears.)

Whatever it is, it appears to be threaded onto the factory spindle so this
is an effort at making something to help me take it off.

Good news: it worked well gripping the thing.

Bad news: it is more tightly installed than the chuck, which unthreaded before
this guy would.

Good news: it now works as a handle for swapping chucks.
"""

import cadquery as cq

# Old lathe made in 1951 measures in inches but CadQuery works in mm.
mm_per_inch = 25.4

# Give an additional 0.2mm of space on mating surface dimensions to account
# for 3D printing inaccuracy
additional_clearance = 0.3

# Top and bottom face chamfers
top_face_chamfer_size = 0.5
bottom_face_chamfer_size = 0.5

# Size of each tab
tab_thickness = 0.11 * mm_per_inch - additional_clearance
tab_depth = 0.1 * mm_per_inch - additional_clearance
tab_length = 0.45 * mm_per_inch + top_face_chamfer_size
tab_count = 12

# Dimensions for ring of tabs
inner_radius = (2.45/2) * mm_per_inch + additional_clearance
outer_radius = inner_radius + tab_depth + 4
ring_length = tab_length

# Two modes: base that fits a 1/2" square drive wrench or a handle
handle_not_square_drive = True

if handle_not_square_drive:
    # Add a handle
    handle_width = 30
    handle_length = 200
else:
    # Add a base for square drive wrench
    base_thickness = 12
    square_drive = (1/2) * mm_per_inch + additional_clearance

tab = (
    cq.Workplane("XY")
    .center(0, inner_radius)
    .box(tab_thickness, tab_depth*2, tab_length)
    )

ring = (
    cq.Workplane("XY")
    .circle(outer_radius)
    .circle(inner_radius)
    .extrude(ring_length/2, both=True)
    )

adapter = ring

for angle in range(0,360,int(360/tab_count)):
    adapter = adapter.union(tab.rotate((0,0,0),(0,0,1),angle))

if handle_not_square_drive:
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
    adapter = adapter.union(handle)
    # Round off where handle joins the ring
    join_edges = (
        adapter
        .edges(cq.selectors.BoxSelector(
            (inner_radius+1, handle_width, ring_length),
            (outer_radius+1, -handle_width, -ring_length)
            ))
        )
    adapter = join_edges.fillet(handle_width)

    # Rotate to sit diagonally on print bed
    adapter = adapter.rotate((0,0,0),(0,0,1),40)
else:
    base = (
        adapter.faces("<Z").workplane()
        .circle(outer_radius)
        .rect(square_drive, square_drive, centered=True)
        .extrude(base_thickness)
        )
    adapter = adapter.union(base)

adapter = adapter.faces("<Z").chamfer(bottom_face_chamfer_size)
adapter = adapter.faces(">Z").chamfer(top_face_chamfer_size)

show_object(adapter)

