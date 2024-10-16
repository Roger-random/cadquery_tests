"""
Spent spool tray
"""
import math
import cadquery as cq

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

base_height = 0.6

# Inner ring is sized to be even multiple of 0.4mm nozzle diameter
ring_depth = 8 * 0.4
ring_height = 5

# Guide rail on the sides should be equal to or less than ring height
rail_height = ring_height-2

# Tray dimensions
tray_edge_fillet = 3
tray_top_chamfer = 2 # Adds a bit of structural strength
latch_height = 3
latch_depth = 3
handle_height = 10

wedge = (
    cq.Workplane("XY")
    .lineTo(outer_radius,0)
    .ellipseArc(outer_radius,outer_radius,0,angle,0)
    .close()
    .extrude(height)
    )
#show_object(wedge, options = {"alpha":0.9, "color":"blue"})

base = (
    cq.Workplane("XZ")
    .lineTo(0,ring_height)
    .lineTo(inner_radius + ring_depth, ring_height)
    .lineTo(inner_radius + ring_depth + ring_height, 0)
    .close()
    .revolve(angle, (0,0,0), (0,1,0))
    )

rail_1 = (
    cq.Workplane("YZ")
    .lineTo(0,rail_height)
    .lineTo(rail_height,0)
    .close()
    .extrude(outer_radius)
    )

rail_2 = (
    cq.Workplane("YZ")
    .transformed(rotate=cq.Vector(0,angle,0))
    .lineTo(0,rail_height)
    .lineTo(-rail_height,0)
    .close()
    .extrude(outer_radius)
    )

base = base + rail_1 + rail_2

cleanup = (
    cq.Workplane("XY")
    .circle(outer_radius)
    .circle(inner_radius+additional_clearance)
    .extrude(height*2,both=True)
    )

base = base.intersect(cleanup)

tray = (
    cq.Workplane("XZ")
    .lineTo(inner_radius,height-additional_clearance,True)
    .lineTo(outer_radius,height-additional_clearance)
    .lineTo(outer_radius,latch_height + latch_depth)
    .lineTo(outer_radius-latch_depth, latch_height)
    .lineTo(outer_radius-latch_depth, 0)
    .lineTo(inner_radius + ring_depth + ring_height, 0)
    .lineTo(inner_radius, ring_depth+ring_height)
    .close()
    .revolve(angle, (0,0,0), (0,1,0))
    )

tray = tray-base
tray = tray.edges("not >Z").edges("not <Z").fillet(tray_edge_fillet)
tray = tray.edges(">Z").chamfer(tray_top_chamfer)

show_object(tray, options = {"alpha":0.5, "color":"red"})
show_object(base, options = {"alpha":0.5, "color":"green"})

