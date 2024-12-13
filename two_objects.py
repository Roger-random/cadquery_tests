"""
Experiment generating multiple objects intended to be
imported into a 3D printing slicer together.
"""
import cadquery as cq

# Inner content where we can go wild with experimentation
inner = (
    cq.Workplane("XY")
    .box(30,30,10)
    )
ball = (
    cq.Workplane("XY")
    .sphere(12.5)
    )
inner = inner.intersect(ball)
shaft = (
    cq.Workplane("XY")
    .circle(4.1)
    .extrude(10, both=True)
    )
inner = inner - shaft

# Outer frame to be printing rigid (normal)
outer = (
    cq.Workplane("XY")
    .box(35,35,10)
    .edges("|Z")
    .fillet(2)
    .faces("|Z")
    .chamfer(0.5)
    )
outer = outer-ball-ball.shell(0.2)

show_object(outer, options = {"alpha":0.5, "color":"green"})
show_object(inner, options = {"alpha":0.5, "color":"red"})