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
additional_clearance = 0.2

# Top and bottom face chamfers
top_face_chamfer_size = 1
bottom_face_chamfer_size = 2

# Size of each tab
tab_thickness = 0.11 * mm_per_inch - additional_clearance
tab_depth = 0.1 * mm_per_inch - additional_clearance
tab_length = 0.45 * mm_per_inch + top_face_chamfer_size
tab_count = 12

# Dimensions for ring of tabs
inner_radius = (2.45/2) * mm_per_inch + additional_clearance
outer_radius = inner_radius + tab_depth + 4
ring_length = tab_length

# Dimensions for base
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

