import cadquery as cq

mm_per_inch = 25.4
key_size_inch = (5/16)*0.90

key_length_inch = 2
handle_length_inch = 2.5

print_bed_adhesion_fillet = 5
elephant_foot_compensation = 0.5

key_size_mm = key_size_inch * mm_per_inch
key_length_mm = key_length_inch * mm_per_inch
handle_length_mm = handle_length_inch * mm_per_inch

key = (
    cq.Workplane("XY")
    .box(key_size_mm, key_length_mm, key_size_mm)
    )

handle = (
    cq.Workplane("XY", origin=(0, key_length_mm/2,0))
    .box(handle_length_mm,key_size_mm*2,key_size_mm)
    .edges("|Z")
    .fillet(print_bed_adhesion_fillet)
    )

result = (
    key.union(handle)
    .chamfer(elephant_foot_compensation)
    )

show_object(result)
