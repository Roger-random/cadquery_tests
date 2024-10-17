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
ring_height = 4
ring_chamfer = 2 # Because spool inner corner is probably not perfectly square

# Tray dimensions
tray_edge_fillet = 2
tray_top_chamfer = ring_chamfer
latch_height = ring_height
latch_depth = 3

handle_sphere_size=15
handle_cut_depth=5

rib_spacing=7.5
rib_size_bottom = 3
rib_size_top = 1

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
    .lineTo(ring_height/2,0)
    .close()
    .extrude(outer_radius)
    )

rail_2 = (
    cq.Workplane("YZ")
    .transformed(rotate=cq.Vector(0,angle,0))
    .lineTo(0,ring_height)
    .lineTo(-ring_height/2,0)
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
    .lineTo(inner_radius,height-tray_top_chamfer-additional_clearance,True)
    .lineTo(inner_radius+tray_top_chamfer,height-additional_clearance)
    .lineTo(outer_radius-beyond_edge,height-additional_clearance)
    .lineTo(outer_radius,height-beyond_edge)
    .lineTo(outer_radius,latch_height + latch_depth)
    .lineTo(outer_radius-latch_depth, latch_height)
    .lineTo(outer_radius-latch_depth, 0)
    .lineTo(inner_radius + ring_depth + ring_height, 0)
    .lineTo(inner_radius, ring_depth+ring_height)
    .close()
    .revolve(angle, (0,0,0), (0,1,0))
    )

tray = tray.edges("|Z").fillet(tray_edge_fillet)

tray_top_edge_1 = (
    cq.Workplane("YZ")
    .lineTo(0,height-tray_top_chamfer,True)
    .lineTo(0,height)
    .lineTo(tray_top_chamfer/2,height)
    .close()
    .extrude(outer_radius)
    )
tray_top_edge_2 = (
    cq.Workplane("YZ")
    .transformed(rotate=cq.Vector(0,angle,0))
    .lineTo(0,height-tray_top_chamfer,True)
    .lineTo(0,height)
    .lineTo(-tray_top_chamfer/2,height)
    .close()
    .extrude(outer_radius)
    )
tray = tray-tray_top_edge_1
tray = tray-tray_top_edge_2
tray = tray-base

# Add a handle to the tray
handle_cutout = (
    cq.Workplane("XZ")
    .transformed(rotate=cq.Vector(0,angle/2,0))
    .transformed(offset = cq.Vector(outer_radius+handle_sphere_size-handle_cut_depth, height/2, 0))
    .sphere(handle_sphere_size)
    .workplane(offset=-handle_cut_depth)
    .transformed(rotate=cq.Vector(0,45,0))
    .split(keepBottom=True)
    )
tray = tray-handle_cutout

# Flat side of tray warps when printing in thin wall vase mode, add small ribs
rib_span = outer_radius-beyond_edge-inner_radius
rib_count = math.floor(rib_span / rib_spacing)
rib_spacing = rib_span / rib_count

for rib_angle in (0,angle):
    for rib_index in range(1, rib_count+1, 1):
        rib = (
            cq.Workplane("XY")
            .transformed(rotate=cq.Vector(0,0,rib_angle))
            .transformed(offset = cq.Vector(inner_radius + rib_index*rib_spacing, 0, 0))
            .polygon(6, rib_size_bottom, circumscribed=True)
            .workplane(offset=height)
            .polygon(6, rib_size_top, circumscribed=True)
            .loft()
            )
        tray = tray-rib

show_object(tray, options = {"alpha":0.5, "color":"red"})
