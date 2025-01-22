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
Experiments in thin-wall printing inspired by 3DLabPrint
"""
import math
import cadquery as cq

default_outer_diameter = 110
default_height = 80
default_nozzle_diameter = 0.4

# Big enough that the slicer wouldn't ignore (merge/close) the gap but small
# enough we hope adjacent filament will stick together.
default_zero_gap = 0.1

def single_wall(
        diameter = default_outer_diameter,
        height = default_height,
        thickness = default_nozzle_diameter):
    return (
        cq.Workplane("XY")
        .circle(diameter/2)
        .circle(diameter/2 - thickness)
        .extrude(height)
        )

def radial_wall_vase(
        diameter = default_outer_diameter,
        height = default_height,
        thickness = default_nozzle_diameter,
        rib_depth = 5,
        rib_spacing = 30,
        zero_gap = default_zero_gap):
    cylinder_volume = (
        cq.Workplane("XY")
        .circle(diameter/2)
        .circle(diameter/2 - rib_depth)
        .extrude(height)
        )
    rib = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(diameter/2-rib_depth/2-thickness*2,0,0))
        .rect(rib_depth,zero_gap)
        .extrude(height)
        )
    rib_count = round(math.pi*diameter/rib_spacing)
    rib_angular_spacing = 360/rib_count
    ribs = None
    for r in range(rib_count):
        if r == 0:
            ribs = rib
        else:
            ribs = ribs + rib.rotate((0,0,0),(0,0,1),rib_angular_spacing*r)

    return (
        single_wall(diameter, height, thickness) +
        (cylinder_volume-ribs) -
        rib.translate((thickness*2,0,0))
        )

# When the gap is sliced at an angled spiral, it becomes smaller unless we boost
# its size by sin(angle)
def twist_gap(twist_angle, zero_gap):
    return zero_gap * (1+math.sin(math.radians(twist_angle)))

# TwistExtrude angle parameter is an angle, in degrees, regardless of
# extrusion height. I want to control twist as angle degrees that
# continues regardless of height. So this is a function that calculates
# the twistExtrude angle degrees as a function of extrusion height.
# 1. Convert desired angle degrees to radians, in order to calculate tangent
# 2. Multiple by extrusion height. This is the amount of twistExtrude in
#    terms of length around the circumference.
# 3. Divide this value by the circumference (diameter * pi) to get a fraction
#    of full rotation.
# 4. Mulitply by 360 for number of degrees to feed into twistExtrude.
def twist_extrude_angle(desired_twist, height, diameter):
    return 360*math.tan(math.radians(desired_twist))*height/(diameter*math.pi)

# Returns shape to be printed in vase mode, generating a shape that has
# a cylindrical outer surface and a cylindrical inner surface with ribs
# in between the two surfaces.
def twist_rib_vase(
        diameter = default_outer_diameter,
        height = default_height,
        thickness = default_nozzle_diameter,
        rib_depth = 5,
        rib_spacing = 30,
        rib_twist = 45,
        cut_reverse_ribs = True,
        zero_gap = default_zero_gap):
    cylinder_volume = (
        cq.Workplane("XY")
        .circle(diameter/2)
        .circle(diameter/2 - rib_depth)
        .extrude(height)
        )

    # Enlarge to maintain desired gap size at twist angle
    angled_gap = twist_gap(rib_twist, zero_gap)

    # Convert desired rib angle into angle parameter for twistExtrude
    twistExtrude_angle = twist_extrude_angle(rib_twist, height, diameter)

    full_rib = (
        cq.Workplane("XY")
        .lineTo(diameter/2-rib_depth-thickness, angled_gap/2,forConstruction=True)
        .lineTo(diameter/2-rib_depth-thickness,-angled_gap/2)
        .lineTo(diameter/2+thickness          ,-angled_gap/2)
        .lineTo(diameter/2+thickness          , angled_gap/2)
        .close()
        .twistExtrude(height, twistExtrude_angle)
        )
    shape = cylinder_volume - full_rib
    slot_rib = (
        cq.Workplane("XY")
        .lineTo(diameter/2-rib_depth-thickness, angled_gap/2,forConstruction=True)
        .lineTo(diameter/2-rib_depth-thickness,-angled_gap/2)
        .lineTo(diameter/2-thickness*2        ,-angled_gap/2)
        .lineTo(diameter/2-thickness*2        , angled_gap/2)
        .close()
        .twistExtrude(height,twistExtrude_angle)
        )

    rib_count = round(math.pi*diameter/rib_spacing)
    rib_angular_spacing = 360/rib_count
    for rib_number in range(1,rib_count):
        shape = shape - slot_rib.rotate((0,0,0),(0,0,1),rib_angular_spacing*rib_number)

    if cut_reverse_ribs:
        reverse_rib = (
            cq.Workplane("XY")
            .lineTo(diameter/2-rib_depth-thickness, angled_gap/2,forConstruction=True)
            .lineTo(diameter/2-rib_depth-thickness,-angled_gap/2)
            .lineTo(diameter/2-thickness*2        ,-angled_gap/2)
            .lineTo(diameter/2-thickness*2        , angled_gap/2)
            .close()
            .twistExtrude(height,-twistExtrude_angle)
            )
        for rib_number in range(rib_count):
            shape = shape - reverse_rib.rotate((0,0,0),(0,0,1),rib_angular_spacing*rib_number)

    return shape

# Returns shape to be printed in vase mode, generating a shape that has
# a cylindrical outer surface and ribs inside that surface.
# No inner cylinder.
def inner_twist_rib_vase(
        diameter = default_outer_diameter,
        height = default_height,
        thickness = default_nozzle_diameter,
        rib_depth = 5,
        rib_spacing = 30,
        rib_twist = 45,
        cut_reverse_ribs = True,
        reverse_rib_offset = 25,
        zero_gap = default_zero_gap):
    # Cylinder we will print in vase mode
    shape = (
        cq.Workplane("XY")
        .circle(diameter/2)
        .extrude(height)
        )
    # Enlarge to maintain desired gap size at twist angle
    angled_gap = twist_gap(rib_twist, zero_gap)

    # Convert desired rib angle into angle parameter for twistExtrude
    twistExtrude_angle = twist_extrude_angle(rib_twist, height, diameter)

    # One direction for ribs cut in the outer surface
    slot_rib = (
        cq.Workplane("XY")
        .lineTo(diameter/2-rib_depth+thickness*2, angled_gap/2,forConstruction=True)
        .lineTo(diameter/2-rib_depth+thickness*2,-angled_gap/2)
        .lineTo(diameter/2+thickness            ,-angled_gap/2)
        .lineTo(diameter/2+thickness            , angled_gap/2)
        .close()
        .twistExtrude(height,twistExtrude_angle)
        )

    rib_count = round(math.pi*diameter/rib_spacing)
    rib_angular_spacing = 360/rib_count
    for rib_number in range(rib_count):
        shape = shape - slot_rib.rotate((0,0,0),(0,0,1),rib_angular_spacing*rib_number)

    if cut_reverse_ribs:
        reverse_rib = (
            cq.Workplane("XY")
            .lineTo(diameter/2-rib_depth+thickness*2, angled_gap/2,forConstruction=True)
            .lineTo(diameter/2-rib_depth+thickness*2,-angled_gap/2)
            .lineTo(diameter/2+thickness*2          ,-angled_gap/2)
            .lineTo(diameter/2+thickness*2          , angled_gap/2)
            .close()
            .twistExtrude(height,-twistExtrude_angle)
            )
        for rib_number in range(rib_count):
            shape = shape - reverse_rib.rotate((0,0,0),(0,0,1),rib_angular_spacing*rib_number+reverse_rib_offset)

    return shape

show_object(inner_twist_rib_vase(rib_spacing=120), options={"alpha":0.5})
