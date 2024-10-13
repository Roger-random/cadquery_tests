"""
Spent spool tray
"""
import math
import cadquery as cq

# Old lathe made in 1951 measures in inches but CadQuery works in mm.
mm_per_inch = 25.4

# Give an additional 0.2mm of space on mating surface dimensions to account
# for 3D printing inaccuracy
additional_clearance = 0.25

# Mitigate 3D printing elephant foot effect
elephant_foot_compensation = 0.5

# Calculate from circumference
inner_radius = 281 / (math.pi*2)

# Outer diameter is easier to measure
outer_radius = 200 / 2

base = (
    cq.Workplane("XY")
    .circle(outer_radius)
    .circle(inner_radius)
    .extrude(1)
    )

show_object(base)

