"""
Chuck keys for lathe chucks.

3D printed plasteic is not strong enough for actual work but will suffice
for getting the jaws moving for cleanup work.

Configurable for two slightly different key sizes. The 3-jaw chuck on this
lathe requires a 5/16" key and the 4-jaw chuck wants 7mm.
"""

import cadquery as cq

mm_per_inch = 25.4

jaws = 4

if jaws == 3:
    key_size = (5/16) * mm_per_inch
    label_text = "3 JAW"
elif jaws == 4:
    key_size = 7
    label_text = "4 JAW"
else:
    raise ValueError("Unsupported configuration for 'jaws' variable")

key_clearance = 0.2

key_size -= key_clearance

print_bed_adhesion_fillet = 5
elephant_foot_compensation = 1.25

key_length = 40
handle_length = 50

# Key that fits into chuck
key = (
    cq.Workplane("XY")
    .box(key_size, key_length, key_size)
    )

# Handle for key
handle = (
    cq.Workplane("XY", origin=(0, key_length/2,0))
    .box(handle_length,key_size*2,key_size)
    .edges("|Z")
    .fillet(print_bed_adhesion_fillet)
    )

# Combine key and handle

# After key and handle are combined, I want to fillet the edges where
# they join. The edges are selected via a building box of these dimensions.
selection_box_center = (key_length/2)-key_size
selection_box_size = key_size*1.1

combined = (
    key.union(handle)
    .edges(cq.selectors.BoxSelector(
        (-selection_box_size, selection_box_center-selection_box_size, -selection_box_size),
        ( selection_box_size, selection_box_center+selection_box_size, +selection_box_size),
        boundingbox = True))
    .fillet(print_bed_adhesion_fillet)
    .chamfer(elephant_foot_compensation)
    )

# Emboss text label
labeled = (
    combined.faces("<Z")
    .workplane(origin=(0, key_length/2,0))
    .text(label_text,10,-0.5)
    )

show_object(labeled)
