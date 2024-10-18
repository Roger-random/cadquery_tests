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
#spool_inner_circumference = 283 # MH Build
spool_inner_circumference = 347 # Filament PM
inner_radius = spool_inner_circumference / (math.pi*2)

# Outer spool diameter is easier to measure directly
spool_outer_diameter = 200 # MH Build, Filament PM
spool_outer_radius = spool_outer_diameter / 2

# Tray actually extends beyond edge of spool
beyond_edge = 10
outer_radius = spool_outer_radius + beyond_edge

#height = 55 # MH Build
height = 68 # Filament PM

ring_depth = 6
ring_height = 4
ring_chamfer = 2 # Because spool inner corner is probably not perfectly square
ring_tab_radius = ring_depth/4 # half of ring depth, and this is radius, so divide by by two again
ring_tab_distance = 3 # Degrees
ring_tab_arm_half = ring_tab_radius/2

# Tray dimensions
tray_edge_fillet = 2
tray_top_chamfer = ring_chamfer

latch_depth = 3
latch_gap = latch_depth-2
latch_height = 1

handle_sphere_size=15
handle_width_half = 2
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

#######################################################################
#
# Build a base

# Start with the ring root
base = (
    cq.Workplane("XZ")
    .lineTo(0,ring_height)
    .lineTo(inner_radius + ring_depth, ring_height)
    .lineTo(inner_radius + ring_depth + ring_height, 0)
    .close()
    .revolve(angle, (0,0,0), (0,1,0))
    )

# Add rails left and right to guide the tray
for rail_index in (0,1):
    if rail_index == 0:
        mirror = 1
    else:
        mirror = -1

    rail = (
        cq.Workplane("YZ")
        .transformed(rotate=cq.Vector(0,angle*rail_index,0))
        .lineTo(0,ring_height)
        .lineTo((ring_height*mirror)/2,0)
        .close()
        .extrude(outer_radius)
        )
    base = base + rail

# Add a short fence to keep tray from falling out too easily
latch = (
    cq.Workplane("XZ")
    .lineTo(outer_radius-latch_depth+latch_gap*2,0,True)
    .lineTo(outer_radius-latch_depth+latch_gap,ring_height)
    .lineTo(outer_radius                      ,ring_height)
    .lineTo(outer_radius                      ,0)
    .close()
    .revolve(angle, (0,0,0), (0,1,0))
    )
base = base + latch

# Taper towards the outer edge
base_wedge = (
    cq.Workplane("XZ")
    .lineTo(inner_radius             , ring_height, True)
    .lineTo(inner_radius + ring_depth, ring_height)
    .lineTo(outer_radius             , latch_height)
    .lineTo(outer_radius             , ring_height)
    .close()
    .revolve(angle, (0,0,0), (0,1,0))
    )
base = base - base_wedge

# Clean up the extraneous guilde rail segments
cleanup = (
    cq.Workplane("XY")
    .circle(outer_radius)
    .circle(inner_radius+additional_clearance)
    .extrude(height*2,both=True)
    )

base = base.intersect(cleanup)

# Add fetures to link segments together

# First add the tab
tab_position_radius = inner_radius+ring_depth/2+ring_tab_radius/2
tab = (
    cq.Workplane("XY")
    .transformed(rotate=cq.Vector(0,0,angle+ring_tab_distance))
    .transformed(offset = cq.Vector(tab_position_radius, 0, 0))
    .circle(ring_tab_radius)
    .extrude(ring_height)
    .chamfer(0.5)
)
tab_arm = (
    cq.Workplane("XZ")
    .transformed(rotate=cq.Vector(0,angle-2,0))
    .lineTo(tab_position_radius-ring_tab_arm_half, 0, True)
    .lineTo(tab_position_radius-ring_tab_arm_half, ring_height)
    .lineTo(tab_position_radius+ring_tab_arm_half, ring_height)
    .lineTo(tab_position_radius+ring_tab_arm_half, 0)
    .close()
    .revolve(ring_tab_distance+2)
    .chamfer(0.5)
    )
base = base+tab_arm
base = base+tab

# Then cut the slot for the adjacent segment's tab
slot = (
    cq.Workplane("XY")
    .transformed(rotate=cq.Vector(0,0,ring_tab_distance))
    .transformed(offset = cq.Vector(tab_position_radius, 0, 0))
    .circle(ring_tab_radius+additional_clearance)
    .extrude(ring_height)
)
slot_arm = (
    cq.Workplane("XZ")
    .lineTo(tab_position_radius-ring_tab_arm_half-additional_clearance, 0, True)
    .lineTo(tab_position_radius-ring_tab_arm_half-additional_clearance, ring_height)
    .lineTo(tab_position_radius+ring_tab_arm_half+additional_clearance, ring_height)
    .lineTo(tab_position_radius+ring_tab_arm_half+additional_clearance, 0)
    .close()
    .revolve(ring_tab_distance)
    )
slot = slot+slot_arm

base = base - slot

# Chamfer the inner bottom corner because corresponding spool interior is not perfectly square
ring_chamfer_cut = (
    cq.Workplane("XZ")
    .lineTo(inner_radius+ring_chamfer, 0)
    .lineTo(inner_radius             , ring_chamfer)
    .close()
    .revolve(angle)
    )
base = base - ring_chamfer_cut

# Slice off a tiny bit for clearance
base = base.faces("<Y").workplane(offset=-additional_clearance).split(keepBottom=True)

show_object(base, options = {"alpha":0.5, "color":"green"})

# Build a tray
tray = (
    cq.Workplane("XZ")
    .lineTo(inner_radius,height-tray_top_chamfer-additional_clearance,True)
    .lineTo(inner_radius+tray_top_chamfer,height-additional_clearance)
    .lineTo(outer_radius-beyond_edge,height-additional_clearance)
    .lineTo(outer_radius,height-beyond_edge)
    .lineTo(outer_radius,ring_height + latch_depth)
    .lineTo(outer_radius-latch_depth, ring_height)
    .lineTo(outer_radius-latch_depth+latch_gap, 0)
    .lineTo(inner_radius + ring_depth + ring_height + additional_clearance, 0)
    .lineTo(inner_radius + additional_clearance, ring_depth+ring_height)
    .close()
    .revolve(angle, (0,0,0), (0,1,0))
    )

# Slice off a tiny bit for clearance
tray = tray.faces("<Y").workplane(offset=-additional_clearance).split(keepBottom=True)

tray = tray.edges("|Z").fillet(tray_edge_fillet)

for edge_index in (0,1):
    if edge_index == 0:
        mirror = 1
    else:
        mirror = -1

    # Cut top edge for a bit of added strength
    top_edge = (
        cq.Workplane("YZ")
        .transformed(rotate=cq.Vector(0,angle*edge_index,0))
        .lineTo(0,height-tray_top_chamfer,True)
        .lineTo(0,height)
        .lineTo(mirror*tray_top_chamfer/2,height)
        .close()
        .extrude(outer_radius)
        )
    tray = tray - top_edge

    # Cut bottom edge to fit base
    bottom_edge = (
        cq.Workplane("YZ")
        .transformed(rotate=cq.Vector(0,angle*edge_index,0))
        .lineTo(0,(ring_height+additional_clearance))
        .lineTo(((ring_height*mirror/2)+(mirror*additional_clearance)),0)
        .close()
        .extrude(outer_radius)
        )
    tray = tray - bottom_edge

# Add a handle to the tray
handle_cutout = (
    cq.Workplane("XZ")
    .transformed(rotate=cq.Vector(0,angle/2,0))
    .transformed(offset = cq.Vector(outer_radius+handle_sphere_size-handle_cut_depth, height/2, 0))
    .sphere(handle_sphere_size)
    )
handle_keep = (
    cq.Workplane("XY")
    .transformed(rotate=cq.Vector(0,0, angle/2))
    .lineTo(outer_radius - handle_cut_depth,    handle_width_half, True)
    .lineTo(outer_radius + handle_sphere_size,  handle_width_half)
    .lineTo(outer_radius + handle_sphere_size, -handle_width_half)
    .lineTo(outer_radius - handle_cut_depth,   -handle_width_half)
    .close()
    .extrude(height)
    )
handle_cutout = handle_cutout - handle_keep
tray = tray-handle_cutout

handle_add = (
    cq.Workplane("XZ")
    .transformed(rotate=cq.Vector(0,angle/2,0))
    .transformed(offset = cq.Vector(outer_radius-handle_sphere_size+handle_cut_depth, height/2, 0))
    .sphere(handle_sphere_size)
    )
handle_add = handle_add.intersect(handle_keep)
tray = tray+handle_add

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
