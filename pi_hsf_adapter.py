"""
Exploring the idea of a totally overkill thermal solution for a Raspberry Pi:
The heat sink and fan (HSF) assembly of an Intel CPU in LGA1155 (or similar)
form factor.
    
"""

import math
import cadquery as cq

hsf_mount_length = 75
hsf_mount_width = 12.5
hsf_mount_thickness = 1.5 # Standard FR4 PCB thickness = 1.57mm or 0.062"

overall_width = hsf_mount_length+hsf_mount_width*2

hsf_plate = (
    cq.Workplane("XY")
    .transformed(rotate=cq.Vector(0, 0, 45))
    .box(
        hsf_mount_width,
        hsf_mount_width+hsf_mount_length*math.sqrt(2),
        hsf_mount_thickness)
    .box(
        hsf_mount_width+hsf_mount_length*math.sqrt(2),
        hsf_mount_width,
        hsf_mount_thickness)
    )

# Cosmetic additions to fit base
hsf_plate_tabs = (
    cq.Workplane("XY")
    .rect(overall_width-hsf_mount_width,
          overall_width-hsf_mount_width,
          forConstruction = True)
    .vertices()
    .box(hsf_mount_width,
         hsf_mount_width,
         hsf_mount_thickness)
    )

hsf_plate_tabs_fillet = 5

hsf_plate_tabs_intersect = (
    cq.Workplane("XY")
    .box(overall_width, overall_width, hsf_mount_thickness)
     .edges("|Z")
    .fillet(hsf_plate_tabs_fillet)
    )

hsf_plate_tabs = hsf_plate_tabs.intersect(hsf_plate_tabs_intersect)

hsf_plate = hsf_plate + hsf_plate_tabs

# Dimensions from Raspberry Pi product brief
pi_mount_width = 58
pi_mount_height = 49
pi_center_offset_x = -2.5

pi_mount_border = 11
pi_plate_thickness = hsf_mount_thickness

pi_plate = (
    cq.Workplane("XY")
    .box (
        pi_mount_width + pi_mount_border,
        pi_mount_height + pi_mount_border,
        pi_plate_thickness
        )
    )

adapter = hsf_plate + pi_plate

# Add Pi mounting standoff

# Must be tall enough to clear legs of through-hold components
pi_mount_standoff_height = 2.5

# Pi spec sheet doesn't explicitlys give size of clearance area?
# Empircally measured at 6mm.
pi_mount_standoff_radius = 6/2

adapter = (
    adapter.faces(">Z").workplane()
    .transformed(offset=cq.Vector(pi_center_offset_x,0,0))
    .rect(pi_mount_width, pi_mount_height, forConstruction = True)
    .vertices()
    .circle(pi_mount_standoff_radius)
    .extrude(pi_mount_standoff_height)
    )

# Cut Pi mounting holes
# TODO: Look up proper minor diameter of M2.5 thread
pi_mount_hole_radius = 2.4/2

pi_mount_holes = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(pi_center_offset_x,0, -hsf_mount_thickness/2))
    .rect(pi_mount_width, pi_mount_height, forConstruction = True)
    .vertices()
    .circle(pi_mount_hole_radius)
    .extrude(hsf_mount_thickness + pi_mount_standoff_height)
    )
adapter = adapter - pi_mount_holes

# Cut HSF mounting holes
hsf_mount_hole_radius = 4.15/2 # Spec says diameter 4.03 +0.05/-0.03. Even looser for prototype.
hsf_mount_holes = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(0,0, -hsf_mount_thickness/2))
    .rect(hsf_mount_length, hsf_mount_length, forConstruction = True)
    .vertices()
    .circle(hsf_mount_hole_radius)
    .extrude(hsf_mount_thickness)
    )
adapter = adapter - hsf_mount_holes

# Cut center hole for thermal transfer bar
thermal_bar_radius = 36/2
thermal_bar = (
    cq.Workplane("XY")
    .circle(thermal_bar_radius)
    .extrude(hsf_mount_thickness, both=True)
    )
adapter = adapter - thermal_bar

show_object(adapter, options = {"alpha":0.5, "color":"green"})

# Representation of bent acrylic stand
stand_height = 60
stand = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(0,0, hsf_mount_thickness/2))
    .rect(overall_width, overall_width)
    .extrude(-stand_height)
     .edges("|Z")
    .fillet(hsf_plate_tabs_fillet)
    .faces("|Z")
    .shell(-1.6) # Approx. 1/16" thick acrylic
    )

# Cut slots for aluminum piece to sit in
hsf_openings = (
    cq.Workplane("XY")
    .rect(overall_width-hsf_mount_width,
          overall_width-hsf_mount_width,
          forConstruction = True)
    .vertices()
    .box(hsf_mount_width + 0.25,
         hsf_mount_width + 0.25,
         hsf_mount_thickness)
    )
stand = stand - hsf_openings

stand_rear_opening = (
    cq.Workplane("XZ")
    .rect(overall_width/2, overall_width*2)
    .extrude(-overall_width)
    )
stand = stand - stand_rear_opening

show_object(stand, options = {"alpha":0.5, "color":"blue"})