"""
Spindle end adapter

The old lathe came with some nonstandard attachment at the end of its spindle
whose purpose is currently unknown.

Whatever it is, it appears to be threaded onto the factory spindle so this
is an effort at making something to help me take it off.
"""

import cadquery as cq

# Give an additional 0.2mm of space to account for 3D printing inaccuracy
additional_clearance = 0.2

result = (
    cq.Workplane("XY")
    .box(10, 20, 30)
    )

show_object(result)
