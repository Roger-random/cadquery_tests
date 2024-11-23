"""
Generate a series of blocks for generic 608 bearings, combining
them together into a single test piece.

Originally created to see if support material generation is
good enough to allow bearings to be used at arbitrary angles
in a 3D printed project.
"""
import cadquery as cq

def bearing_block():
    return (
        cq.Workplane("XY")
        .polygon(4, 30, circumscribed=True)
        .circle(5)
        .extrude(20)
        .faces(">Z").workplane()
        .circle(11)
        .extrude(-7, combine="cut")
        .faces("<Z").workplane()
        .circle(11)
        .extrude(-7, combine="cut")
        .translate((15,15,0))
        )

big_block = bearing_block()

for block in range(1,7):
    big_block = big_block + (
        bearing_block()
        .translate((0,block*30,0))
        .rotate((0,0,0),(0,1,0),block*-15)
        )

show_object(big_block)
