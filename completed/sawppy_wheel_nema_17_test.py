"""
Find out if it is practica to couple a Sawppy rover wheel directly to a
NEMA 17 motor output shaft (5mm)
"""

import cadquery as cq

circumscribe_radius = 22
thickness = 10

coupler = (
    cq.Workplane("XY")
    .polygon(3, circumscribe_radius, circumscribed=True)
    .circle(2.5)
    .extrude(thickness)
    .edges("|Z").fillet(2)
    )

adjustment_gap = (
    cq.Workplane("YZ")
    .transformed(offset=cq.Vector(0,thickness/2))
    .rect(0.5,thickness)
    .extrude(-circumscribe_radius*2)
    )
coupler = coupler - adjustment_gap

fastener_shaft = (
    cq.Workplane("XZ")
    .transformed(offset=cq.Vector(-6,thickness/2))
    .circle(3.2/2)
    .extrude(circumscribe_radius,both=True)
    )
coupler = coupler - fastener_shaft

for y_offset in (circumscribe_radius-6, -circumscribe_radius+6):
    fastener_flat = (
        cq.Workplane("YZ")
        .transformed(offset=cq.Vector(y_offset,thickness/2))
        .rect(circumscribe_radius, thickness)
        .extrude(-circumscribe_radius)
        .edges("|Z").fillet(1)
        )
    coupler = coupler - fastener_flat

coupler = coupler.faces(">Z or <Z").chamfer(0.5)

show_object(coupler, options = {"alpha":0.5, "color":"red"})
