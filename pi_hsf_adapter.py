"""
Exploring the idea of a totally overkill thermal solution for a Raspberry Pi:
The heat sink and fan (HSF) assembly of an Intel CPU in LGA1155 (or similar)
form factor.
    
"""

import math
import cadquery as cq

hsf_mount_length = 75
hsf_mount_width = 12.5
hsf_mount_thickness = 1.57 # Standard FR4 PCB thickness

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

pi_mount_border = 10
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
pi_mount_standoff_height = 3

# Pi spec sheet doesn't explicitlys give size of clearance area?
# Empircally measured at 6mm.
pi_mount_standoff_radius = 6/2

adapter = (
    adapter.faces(">Z").workplane()
    .rect(pi_mount_width, pi_mount_height, forConstruction = True)
    .vertices()
    .circle(pi_mount_standoff_radius)
    .extrude(pi_mount_standoff_height)
    )

# Add a raised plate to draw heat from Pi with help of a pad of thermally
# conductive and electrically insulating material. Dimensions start with
# the rectangle defined by mounting holes, which should keep it clear of
# USB and Ethernet protrusions. Then cut out clearance for GPIO pins and
# the microSD slot.

pi_thermal_pad_thickness = 1
pi_thermal_plate_thickness = pi_mount_standoff_height - pi_thermal_pad_thickness

pi_thermal_plate = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(0, 0, hsf_mount_thickness/2))
    .rect(pi_mount_width,pi_mount_height)
    .extrude(pi_thermal_plate_thickness)
    )

pi_thermal_clearance_gpio = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(0, pi_mount_height/2, hsf_mount_thickness/2))
    .rect(pi_mount_width,8)
    .extrude(pi_thermal_plate_thickness)
    )
pi_thermal_plate = pi_thermal_plate - pi_thermal_clearance_gpio


pi_thermal_clearance_microsd = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(15/2-pi_mount_width/2, 1, hsf_mount_thickness/2))
    .rect(15,15)
    .extrude(pi_thermal_plate_thickness)
    )
pi_thermal_plate = pi_thermal_plate - pi_thermal_clearance_microsd


adapter = adapter + pi_thermal_plate

# Add a raised section on the other side in the shape of a CPU bridging the
# gap between base plate and bottom of HSF in order to conduct heat.

# TODO: this value varies between CPU generations, how to deal with variation?
hsf_thermal_pad_thickness = 6

hsf_thermal_pad_width = 32

hsf_thermal_pad = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(0,0, -hsf_mount_thickness/2))
    .rect(hsf_thermal_pad_width, hsf_thermal_pad_width)
    .extrude(-hsf_thermal_pad_thickness)
    .edges("|Z").fillet(hsf_thermal_pad_thickness)
    )

show_object(hsf_thermal_pad, options = {"alpha":0.5, "color":"red"})

# Cut Pi mounting holes
# TODO: Look up proper minor diameter of M2.5 thread
pi_mount_hole_radius = 2.4/2

pi_mount_holes = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(0,0, -hsf_mount_thickness/2))
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

show_object(adapter, options = {"alpha":0.5, "color":"green"})
