"""
MIT License

Copyright (c) 2024 Roger Cheng

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

"""
Spent Spool Storage System

Reuse empty 3D printing filament spools as the core for a storage system for
small parts. This script generates wedge-shaped storage trays that sit in a
matching base. Bases for all wedges (plus any placeholders) snap-fit
together into a ring to hold everything together.

Since different filament vendors use different spools, this script adapts to
parameters specifying spool dimensions:
    1. Inner radius
    2. Outer radius
    3. Height (distance between two sides)

The fourth critical parameter is the size of the desired storage wedge
specified in degrees. A full spool storage system can be assembled out of any
number of wedges (or placeholders) as long as they add up to 360 degrees.

Works best in the range of 30-60 degrees.
Minimum size is roughly 15 degrees depending on spool outer radius.
Maximum size is 120 degrees as the geometry starts failing beyond that.

For the adventurous experimenters, more parameters are present as constants
and can be adjusted but interactions can be unpredictable.

Written in CQ-Editor 0.3.0dev

"""
import math
import cadquery as cq

#######################################################################
#
#  How big of a wedge we want in degrees
#
angle = 15

#######################################################################
#
#  Dimensions of target spent spool spindle
#
#spool_height = 55 # MH Build
spool_height = 70 # Filament PM

# Calculate spool inner radius from measuring circumference of spool center
#spool_inner_circumference = 283 # MH Build
spool_inner_circumference = 347 # Filament PM
inner_radius = spool_inner_circumference / (math.pi*2)

# Outer spool diameter is easier to measure directly
spool_outer_diameter = 200 # MH Build, Filament PM
spool_outer_radius = spool_outer_diameter / 2

#######################################################################
#
#  Additional space between mating surfaces due to 3D printing inaccuracy.
#  May require adjustment to fit specific combinations of printer,
#  filment, print profile, etc.
#
#  If base segments don't fit into each other, increase this value.
#  If they fit too loosely, decrease this value.
#
additional_clearance = 0.25

#######################################################################
#
#  Dimensions of storage system components
#

# Tray actually extends beyond edge of spool
beyond_edge = 10
outer_radius = spool_outer_radius + beyond_edge

ring_depth = 6
ring_height = 4
ring_chamfer = 2 # Because spool inner corner is probably not perfectly square
ring_tab_radius = ring_depth/4 # half of ring depth, and this is radius, so divide by by two again
ring_tab_distance = 3 # Degrees
ring_tab_arm_half = ring_tab_radius/2

height = spool_height - ring_height

# Tray dimensions
tray_edge_fillet = 2
tray_top_chamfer = ring_chamfer

latch_depth = 5
latch_protrude = 0.5
latch_gap = latch_protrude+additional_clearance

handle_sphere_size=15
handle_cut_depth=5

#######################################################################
#
#  Profile for inner ring segments that clicks together
#
def ring_root_profile():
    return (
        cq.Workplane("XZ")
        .lineTo(0,ring_height)
        .lineTo(inner_radius + ring_depth, ring_height)
        .lineTo(inner_radius + ring_depth + ring_height/2, ring_height/2)
        .lineTo(inner_radius + ring_depth + ring_height/2, 0)
        .close()
        )

#######################################################################
#
# Given a ring root profile, add left and right side rails
#
def add_side_rails(base):
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

    # Clean up the extraneous guilde rail segments
    cleanup = (
        cq.Workplane("XY")
        .circle(outer_radius)
        .circle(inner_radius+additional_clearance)
        .extrude(height*2,both=True)
        )
    base = base.intersect(cleanup)

    return base

#######################################################################
#
# Generate the outer fence which keeps the tray from falling out.
# Intended to be added to a base with side rails.
#
def build_outer_fence():
    # Add a short fence to keep tray from falling out too easily
    fence = (
        cq.Workplane("XZ")
        .lineTo(outer_radius-latch_depth+latch_protrude+latch_gap,0,True)
        .lineTo(outer_radius-latch_depth+latch_gap,ring_height)
        .lineTo(outer_radius                      ,ring_height)
        .lineTo(outer_radius                      ,0)
        .close()
        .revolve(angle, (0,0,0), (0,1,0))
        )

    # Tab for holding down the fence during tray removal
    fence_tab_ball = (
        cq.Workplane("XZ")
        .transformed(rotate=cq.Vector(0,angle/2,0))
        .transformed(offset = cq.Vector(
            outer_radius-handle_sphere_size+handle_cut_depth, ring_height/2, 0))
        .sphere(handle_sphere_size)
        )
    fence_tab_keep = (
        cq.Workplane("XZ")
        .lineTo(outer_radius,0,True)
        .lineTo(outer_radius,ring_height)
        .lineTo(outer_radius + handle_sphere_size,ring_height)
        .lineTo(outer_radius + handle_sphere_size,0)
        .close()
        .revolve(angle, (0,0,0), (0,1,0))
        )
    return fence + fence_tab_ball.intersect(fence_tab_keep)

#######################################################################
#
# Position (in terms of radius) for the tab/slot connecting segments
#
def calculate_tab_position_radius():
    return inner_radius+ring_depth/2+ring_tab_radius/2

#######################################################################
#
# Generate the tab linking segments together, keep this symmetric with
# slot cutter below.
#
def build_link_tab():
    tab_position_radius = calculate_tab_position_radius()
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
    return tab+tab_arm

#######################################################################
#
# Generate the tab linking segments together, keep this symmetric with
# tab above.
#
def build_link_slot_cutter():
    tab_position_radius = calculate_tab_position_radius()
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
    return slot+slot_arm

#######################################################################
#
# Build a base for the tray
#
def build_base():
    base = ring_root_profile().revolve(angle, (0,0,0), (0,1,0))
    base = add_side_rails(base)
    base = base + build_outer_fence()
    base = base + build_link_tab()
    base = base - build_link_slot_cutter()

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

    return base

show_object(build_base(), options = {"alpha":0.5, "color":"green"})

#######################################################################
#
# A placeholder segment is the base but with side # rails and fence
# cut off. Used to hold the ring together in absence of tray+base
#
def build_placeholder():
    ring_root_keep = ring_root_profile().revolve(360, (0,0,0), (0,1,0))
    placeholder = build_base().intersect(ring_root_keep)

    return placeholder

show_object(build_placeholder().translate((0,0,-ring_height*2)),
            options = {"alpha":0.5, "color":"aquamarine"})

def chamfer_tray_radial_edges(tray):
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

    return tray

#######################################################################
#
# Add handle to tray
#
def add_handle(tray):
    # Constant parameters
    handle_width_half = 2

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
    tray = tray - (handle_cutout - handle_keep)

    handle_add = (
        cq.Workplane("XZ")
        .transformed(rotate=cq.Vector(0,angle/2,0))
        .transformed(offset = cq.Vector(outer_radius-handle_sphere_size+handle_cut_depth, height/2, 0))
        .sphere(handle_sphere_size)
        )
    handle_add = handle_add.intersect(handle_keep)
    tray = tray+handle_add

    return tray

#######################################################################
#
# Cut small ribs in the side of the tray as reinforcement
# Critical to prevent flat sides warping under vase mode printing.
#
def cut_reinforcement_ribs(tray):
    # Constant parameters
    rib_spacing_target=7.5
    rib_size_bottom = 3
    rib_size_top = 1

    # Derived parameters
    rib_span = outer_radius-beyond_edge-inner_radius
    rib_count = math.floor(rib_span / rib_spacing_target)
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

    return tray

#######################################################################
#
# A placeholder segment is the base but with side # rails and fence
# cut off. Used to hold the ring together in absence of tray+base
#
def build_tray():
    tray = (
        cq.Workplane("XZ")
        .lineTo(inner_radius,height-tray_top_chamfer-additional_clearance,True)
        .lineTo(inner_radius+tray_top_chamfer,height-additional_clearance)
        .lineTo(outer_radius-beyond_edge,height-additional_clearance)
        .lineTo(outer_radius,height-beyond_edge)
        .lineTo(outer_radius,ring_height + latch_depth)
        .lineTo(outer_radius-latch_depth, ring_height)
        .lineTo(outer_radius-latch_depth+latch_protrude-additional_clearance, 0)
        .lineTo(inner_radius + ring_depth + ring_height + additional_clearance, 0)
        .lineTo(inner_radius + additional_clearance, ring_depth+ring_height)
        .close()
        .revolve(angle, (0,0,0), (0,1,0))
        )

    # Slice off a tiny bit for clearance
    tray = tray.faces("<Y").workplane(offset=-additional_clearance).split(keepBottom=True)
    tray = tray.edges("|Z").fillet(tray_edge_fillet)

    tray = chamfer_tray_radial_edges(tray)
    tray = add_handle(tray)
    tray = cut_reinforcement_ribs(tray)

    return tray

show_object(build_tray(), options = {"alpha":0.5, "color":"red"})
