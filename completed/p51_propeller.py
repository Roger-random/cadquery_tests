"""
MIT License

Copyright (c) 2025 Roger Cheng

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
I printed a 3DLabPrint P-51D Mustang but it will be on static display instead
of a flying remote control airccraft. So I won't be installing a large noisy
brushless outrunner motor or a real propeller. Instead, I will install a
NEMA17 stepper motor (as used in 3D printers) that will turn a fake propeller
(just for looks, can't propel) and turn it slowly and silently. This is the
propeller and hub that will attach to the NEMA17 5mm diameter motor output shaft.
"""
import cadquery as cq

# Real P-51 Mustangs use propeller approx. 11 feet in diameter. A P-51 has a
# wingspan of about 37 feet. The 3DLabPrint Mustang has a wingspan of 1.4
# meters, so a to-scale propeller will have diameter of 418mm
# For comparison, 3DLabPrint recommended a 12x6 propeller.
overall_diameter = 418

# 3DLabPrint included an aesthetic propeller spinner. I'm not sure if it is
# scaled for the 12x6 propeller or to the real thing, but I intend to use it
# as the outer visible shell because I don't know how to match its curvature
# in CadQuery.
spinner_outer_diameter = 85
spinner_inner_diameter = 25
spinner_base_thickness = 2

# The 3DLabPrint spinner is attached via small lips around its perimeter.
# Here I am trying to duplicate its dimensions.
spinner_lip_diameter_rear = 76.5
spinner_lip_diameter_front = 73.8
spinner_lip_clip_thickness = 2
spinner_lip_length = 4

spinner_clip = (
    cq.Workplane("YZ")
    .circle(spinner_outer_diameter/2)
    .extrude(spinner_base_thickness)
    .faces(">X").workplane()
    .circle(spinner_lip_clip_thickness+spinner_lip_diameter_rear/2)
    .workplane(offset=spinner_lip_length)
    .circle(spinner_lip_clip_thickness+spinner_lip_diameter_front/2)
    .loft()
    )

spinner_cut = (
    cq.Workplane("YZ")
    .transformed(offset=cq.Vector(0,0,2))
    .circle(spinner_lip_diameter_rear/2)
    .workplane(offset=spinner_lip_length)
    .circle(spinner_lip_diameter_front/2)
    .loft()
    )

spinner_clip = spinner_clip-spinner_cut

spinner_center_hole = (
    cq.Workplane("YZ")
    .circle(spinner_inner_diameter/2)
    .extrude(spinner_base_thickness)
    )

spinner_clip = spinner_clip-spinner_center_hole

#show_object(spinner_clip, options={"alpha":0.5})

# This propeller was designed as a reasonable-looking propeller for display
# purposes. It was not designed for aerodynamics and any propulsive capability
# would be completely accidental.
prop_base_diameter = 15
prop_base_height = 7.5
prop_neck_diameter = 12
prop_base_neck_transition = prop_base_diameter - prop_neck_diameter
prop_base_center_offset = 17
prop_base_forward_offset = 12.5

propeller_blade_base = (
    cq.Workplane("XY")
    .circle(prop_base_diameter/2)
    .extrude(prop_base_height)
    .faces(">Z").workplane()
    .circle(prop_base_diameter/2)
    .workplane(prop_base_neck_transition)
    .circle(prop_neck_diameter/2)
    .loft()
    .faces(">Z").workplane()
    .circle(prop_neck_diameter/2)
    .workplane(prop_base_neck_transition)
    .circle(prop_base_diameter/2)
    .loft()
    )

prop_curve_2_distance = 50
prop_curve_3_distance = 105

propeller_blade = (
    propeller_blade_base.faces(">Z").workplane()
    .circle(prop_base_diameter/2)
    .workplane(offset=(prop_base_diameter-5)/2)
    .circle(5)
    .loft()
    .faces(">Z").workplane()
    .circle(5)
    .workplane(prop_curve_2_distance)
    .ellipse(3, 12, 30)
    .workplane(prop_curve_3_distance)
    .ellipse(2, 12, 20)
    .loft()
    )

propeller_tip = (
    propeller_blade.faces(">Z").workplane()
    .transformed(rotate=cq.Vector(0,0,20))
    .lineTo(2,0)
    .ellipseArc(2, 12, 0, 180)
    .close()
    .revolve(180, (0,0,0),(1,0,0))
    )

propeller_blade = propeller_blade + propeller_tip

propeller_blade = (
    propeller_blade
    .translate((prop_base_forward_offset, 0, prop_base_center_offset))
#    .rotate((0,0,0),(1,0,0),45)
    )
#show_object(propeller_blade, options={"alpha":0.2})

"""
propeller_blade_02 = propeller_blade.rotate((0,0,0),(1,0,0),90)
propeller_blade_03 = propeller_blade.rotate((0,0,0),(1,0,0),180)
propeller_blade_04 = propeller_blade.rotate((0,0,0),(1,0,0),-90)

show_object(propeller_blade_02)
show_object(propeller_blade_03)
show_object(propeller_blade_04)
"""

# A block to support a single propeller blade
propeller_block = (
    cq.Workplane("YZ")
    .lineTo(prop_base_diameter/2, prop_base_center_offset+1, forConstruction=True)
    .lineTo(prop_base_diameter/2,
            prop_base_center_offset + prop_base_height + prop_base_neck_transition*2)
    .lineTo(-prop_base_diameter/2,
            prop_base_center_offset + prop_base_height + prop_base_neck_transition*2)
    .lineTo(-prop_base_diameter/2, prop_base_center_offset+1)
    .close()
    .extrude(prop_base_forward_offset-3)
    )
propeller_block_recess_1 = (
    cq.Workplane("XY")
    .lineTo(spinner_base_thickness+1, prop_base_diameter/2, forConstruction=True)
    .lineTo(spinner_base_thickness+3, prop_base_diameter/2-2)
    .lineTo(spinner_base_thickness+5, prop_base_diameter/2)
    .close()
    .extrude(prop_base_center_offset + prop_base_height + prop_base_neck_transition*2)
    )
propeller_block_recess_2 = (
    propeller_block_recess_1.mirror("XZ")
    )
propeller_block = propeller_block - propeller_block_recess_1
propeller_block = propeller_block - propeller_block_recess_2
propeller_block = propeller_block - propeller_blade

# A clip to hold a propeller blade against its support block
propeller_clip_thickness = 0.4*4
propeller_clip_lever = 3

propeller_clip = (
    cq.Workplane("XY")
    .transformed(offset=cq.Vector(0,0,prop_base_center_offset+1))
    .lineTo(spinner_base_thickness+1, prop_base_diameter/2, forConstruction=True)
    .lineTo(spinner_base_thickness+3, prop_base_diameter/2-2)
    .lineTo(spinner_base_thickness+5, prop_base_diameter/2)
    .lineTo(prop_base_forward_offset, prop_base_diameter/2)
    .lineTo(prop_base_forward_offset, 0)
    .lineTo(prop_base_forward_offset+prop_base_diameter/2, 0)
    .lineTo(prop_base_forward_offset+prop_base_diameter/2+propeller_clip_thickness,0)
    .radiusArc((prop_base_forward_offset, prop_base_diameter/2 + propeller_clip_thickness), -prop_base_diameter/2 - propeller_clip_thickness)
    .lineTo(spinner_base_thickness+propeller_clip_thickness+1, prop_base_diameter/2 + propeller_clip_thickness)
    .lineTo(spinner_base_thickness+propeller_clip_thickness+1, prop_base_diameter/2 + propeller_clip_thickness + propeller_clip_lever)
    .lineTo(spinner_base_thickness+1,                          prop_base_diameter/2 + propeller_clip_thickness + propeller_clip_lever)
    .close()
    .extrude(prop_base_height + prop_base_neck_transition*2 - 1)
    )
propeller_clip = propeller_clip-propeller_blade
propeller_clip = propeller_clip+propeller_clip.mirror("XZ")

#show_object(propeller_clip, options={"alpha":0.2})
#show_object(propeller_block, options={"alpha":0.2})

# Cut slots to hold small magnets salvaged from retired iPad case
magnet_width = 6
magnet_length = 16
magnet_slot = (
    cq.Workplane("YZ")
    .transformed(offset=cq.Vector(0,prop_base_center_offset+magnet_length/2,0.2))
    .rect(magnet_width,magnet_length)
    .extrude(spinner_base_thickness)
    )

# Final hub assembly
propeller_hub = spinner_clip - magnet_slot
propeller_hub = propeller_hub - magnet_slot.rotate((0,0,0),(1,0,0),90)
propeller_hub = propeller_hub - magnet_slot.rotate((0,0,0),(1,0,0),180)
propeller_hub = propeller_hub - magnet_slot.rotate((0,0,0),(1,0,0),270)

propeller_hub = propeller_hub + propeller_block.rotate((0,0,0),(1,0,0),45)
propeller_hub = propeller_hub + propeller_block.rotate((0,0,0),(1,0,0),135)
propeller_hub = propeller_hub + propeller_block.rotate((0,0,0),(1,0,0),-45)
propeller_hub = propeller_hub + propeller_block.rotate((0,0,0),(1,0,0),-135)

show_object(propeller_hub, options={"color": "green", "alpha":0.5})

# Motor coupler to go with the hub
coupler_outer_radius = prop_base_center_offset + magnet_length + 2
coupler_disk_thickness = 2
shaft_coupler_diameter=15
shaft_coupler_length = 10
shaft_coupler_additional_radius = 2
shaft_diameter = 5
shaft_d_depth = 0.4
coupler_fastener_diameter = 3.25
motor_coupler = (
    cq.Workplane("YZ")
    .circle(coupler_outer_radius)
    .circle(shaft_diameter/2)
    .extrude(-coupler_disk_thickness)
    )
motor_coupler = motor_coupler + (
    cq.Workplane("YZ")
    .circle(shaft_coupler_diameter/2)
    .circle(shaft_diameter/2)
    .extrude(-shaft_coupler_length)
    )
magnet_mirror = magnet_slot.mirror("YZ")
motor_coupler = motor_coupler - magnet_mirror
motor_coupler = motor_coupler - magnet_mirror.rotate((0,0,0),(1,0,0),90)
motor_coupler = motor_coupler - magnet_mirror.rotate((0,0,0),(1,0,0),180)
motor_coupler = motor_coupler - magnet_mirror.rotate((0,0,0),(1,0,0),270)

# Rotate 45 so math for coupler fastener and slit is easier
motor_coupler = motor_coupler.rotate((0,0,0),(1,0,0),45)

# If this is a D-shaped shaft, add in the flat section.
if shaft_d_depth > 0:
    motor_coupler = motor_coupler + (
        cq.Workplane("YZ")
        .lineTo( shaft_diameter/2, shaft_diameter/2-shaft_d_depth, forConstruction = True)
        .lineTo( shaft_diameter/2, shaft_diameter/2)
        .lineTo(-shaft_diameter/2, shaft_diameter/2)
        .lineTo(-shaft_diameter/2, shaft_diameter/2-shaft_d_depth)
        .close()
        .extrude(-shaft_coupler_length)
        )

# Add location for coupler fastener
motor_coupler = motor_coupler + (
    cq.Workplane("YZ")
    .lineTo( shaft_coupler_diameter/2, 0, forConstruction = True)
    .lineTo( 0                       , shaft_coupler_diameter/2)
    .lineTo(-shaft_coupler_diameter/2, 0)
    .lineTo(-shaft_coupler_diameter/2, shaft_coupler_diameter/2 + shaft_coupler_additional_radius)
    .lineTo( shaft_coupler_diameter/2, shaft_coupler_diameter/2 + shaft_coupler_additional_radius)
    .close()
    .extrude(-shaft_coupler_length)
    )

# Subtract hole for coupler fastener
motor_coupler = motor_coupler - (
    cq.Workplane("XZ")
    .transformed(offset=cq.Vector(
        -coupler_disk_thickness-(shaft_coupler_length-coupler_disk_thickness)/2,
        shaft_diameter + shaft_coupler_additional_radius/2,
        0))
    .circle(coupler_fastener_diameter/2)
    .extrude(coupler_outer_radius, both=True)
    )

# Cut slit for coupler
coupler_slit_width = 0.5
motor_coupler = motor_coupler - (
    cq.Workplane("YZ")
    .lineTo( coupler_slit_width/2, 0)
    .lineTo( coupler_slit_width/2, shaft_coupler_diameter/2 + shaft_coupler_additional_radius)
    .lineTo( coupler_outer_radius/2, coupler_outer_radius)
    .lineTo(-coupler_outer_radius/2, coupler_outer_radius)
    .lineTo(-coupler_slit_width/2, shaft_coupler_diameter/2 + shaft_coupler_additional_radius)
    .lineTo(-coupler_slit_width/2, 0)
    .close()
    .extrude(-shaft_coupler_length)
    )

# Rotate 45 back now coupler fastener and slit has been created
motor_coupler = motor_coupler.rotate((0,0,0),(1,0,0),-45)

show_object(motor_coupler, options={"color": "blue", "alpha":0.5})

# Show other components in final position and orientation
show_object(propeller_clip.rotate((0,0,0),(1,0,0),45), options={"color": "red", "alpha":0.5})
show_object(propeller_clip.rotate((0,0,0),(1,0,0),135), options={"color": "red", "alpha":0.5})
show_object(propeller_clip.rotate((0,0,0),(1,0,0),-45), options={"color": "red", "alpha":0.5})
show_object(propeller_clip.rotate((0,0,0),(1,0,0),-135), options={"color": "red", "alpha":0.5})

show_object(propeller_blade.rotate((0,0,0),(1,0,0),45), options={"color": "yellow", "alpha":0.5})
show_object(propeller_blade.rotate((0,0,0),(1,0,0),135), options={"color": "yellow", "alpha":0.5})
show_object(propeller_blade.rotate((0,0,0),(1,0,0),-45), options={"color": "yellow", "alpha":0.5})
show_object(propeller_blade.rotate((0,0,0),(1,0,0),-135), options={"color": "yellow", "alpha":0.5})
