"""
Spindle end ring with hex drive
"""

import cadquery as cq
from spindle_end_ring import make_spindle_end_ring, outer_radius

# Old lathe made in 1951 measures in inches but CadQuery works in mm.
mm_per_inch = 25.4

# Give an additional 0.2mm of space on mating surface dimensions to account
# for 3D printing inaccuracy
additional_clearance = 0.2

chamfer_size = 0.5

# Plate dimensions
plate_thickness = 7
hex_size = (1/4) * mm_per_inch + additional_clearance

ring = make_spindle_end_ring()

plate = (
    ring.faces("<Z").workplane()
    .circle(outer_radius)
    .polygon(6, hex_size, circumscribed=True)
    .extrude(plate_thickness)
    )

adapter = plate+ring

adapter = adapter.faces("<Z or >Z").chamfer(chamfer_size)

show_object(adapter)