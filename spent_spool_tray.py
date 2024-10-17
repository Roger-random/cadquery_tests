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
angle = 15

# Calculate spool inner radius from measuring circumference of spool center
spool_inner_circumference = 281
inner_radius = spool_inner_circumference / (math.pi*2)

# Outer spool diameter is easier to measure directly
spool_outer_diameter = 200
spool_outer_radius = spool_outer_diameter / 2

# Tray actually extends beyond edge of spool
beyond_edge = 10
outer_radius = spool_outer_radius + beyond_edge

height = 54

base_height = 0.6

ring_depth = 6
ring_height = 3
ring_chamfer = 2 # Because spool inner corner is probably not perfectly square

# Tray dimensions
tray_edge_fillet = 3
latch_height = 3
latch_depth = 3

handle_radius = 5
handle_height = 10
handle_fillet = 1
handle_protusion = handle_radius/2
handle_profile_height = handle_height + handle_radius*4

rib_radius = 2
rib_offset = 1.5


# Visualize the wedge-shaped volume we're working within

wedge = (
    cq.Workplane("XY")
    .lineTo(outer_radius,0)
    .ellipseArc(outer_radius,outer_radius,0,angle,0)
    .close()
    .extrude(height)
    )
#show_object(wedge, options = {"alpha":0.9, "color":"blue"})

# Build a base

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
    .lineTo(0,ring_height)
    .lineTo(ring_height,0)
    .close()
    .extrude(outer_radius)
    )

rail_2 = (
    cq.Workplane("YZ")
    .transformed(rotate=cq.Vector(0,angle,0))
    .lineTo(0,ring_height)
    .lineTo(-ring_height,0)
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
base = base.edges("<Z").edges("<X").chamfer(ring_chamfer)

show_object(base, options = {"alpha":0.5, "color":"green"})

# Build a tray

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

tray = tray.edges(">Z").edges(">X").chamfer(beyond_edge)
tray = tray.edges("not >Z").edges("not <Z").fillet(tray_edge_fillet)

# Add a handle to the tray
tray_handle_profile_starting_height = latch_height + latch_depth

tray_handle = (
    cq.Workplane("XY")
    .transformed(rotate=cq.Vector(0, 0, angle/2))
    .transformed(offset = cq.Vector(outer_radius + handle_protusion, 0, tray_handle_profile_starting_height))
    .circle(handle_radius)
    .extrude(handle_profile_height)
    )

handle_inner = outer_radius - handle_radius + handle_protusion
tray_handle_profile = (
    cq.Workplane("XZ")
    .lineTo(handle_inner,                 tray_handle_profile_starting_height)
    .lineTo(handle_inner+handle_radius*2, tray_handle_profile_starting_height + handle_radius*2)
    .lineTo(handle_inner+handle_radius*2, tray_handle_profile_starting_height + handle_radius*2 + handle_height)
    .lineTo(handle_inner,                 tray_handle_profile_starting_height + handle_profile_height)
    .lineTo(inner_radius,                 tray_handle_profile_starting_height + handle_profile_height)
    .close()
    .revolve(angle, (0,0,0), (0,1,0))
    )

tray_handle = tray_handle.intersect(tray_handle_profile)
tray_handle = tray_handle.fillet(handle_fillet)

tray = tray + tray_handle

# Flat side of tray warps when printing in thin wall vase mode, add small ribs
rib_count = math.floor(height / 10)
rib_height = height / rib_count

for rib in range(1, rib_count, 1):
    rib_1 = (
        cq.Workplane("YZ")
        .transformed(offset = cq.Vector(-rib_offset, rib*rib_height, 0))
        .circle(rib_radius)
        .extrude(outer_radius)
        )
    tray = tray-rib_1
    rib_2 = (
        cq.Workplane("YZ")
        .transformed(rotate=cq.Vector(0,angle,0))
        .transformed(offset = cq.Vector(rib_offset, rib*rib_height, 0))
        .circle(rib_radius)
        .extrude(outer_radius)
        )
    tray = tray-rib_2

show_object(tray, options = {"alpha":0.5, "color":"red"})
