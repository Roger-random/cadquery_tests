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

# How big of a wedge we want in degrees
angle = 30

# Calculate spool inner radius from measuring circumference of spool center
spool_inner_circumference = 281
inner_radius = spool_inner_circumference / (math.pi*2)

# Outer spool diameter is easier to measure directly
spool_outer_diameter = 200
spool_outer_radius = spool_outer_diameter / 2

# Tray actually extends beyond edge of spool
outer_radius = spool_outer_radius + 10

height = 56

base = (
    cq.Workplane("XY")
    .circle(outer_radius)
    .circle(inner_radius)
    .extrude(1)
    )

wedge = (
    cq.Workplane("XY")
    .lineTo(outer_radius,0)
    .ellipseArc(outer_radius,outer_radius,0,angle,0)
    .close()
    .extrude(height)
    )

show_object(wedge+base)

