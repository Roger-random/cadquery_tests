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
NEMA17 stepper motor (as used in 3D printers) that will turn slowly and
silently. This is the propeller and hub that will attach to the NEMA17 5mm
diameter motor output shaft.
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

# The 3DLabPrint spinner is attached via small lips around its perimeter.
# Here I am trying to duplicate its dimensions.
spinner_lip_diameter_rear = 76.5
spinner_lip_diameter_front = 73.8
spinner_lip_clip_thickness = 2
spinner_lip_length = 4

spinner_clip = (
    cq.Workplane("YZ")
    .circle(spinner_outer_diameter/2)
    .extrude(2)
    .faces(">X").workplane()
    .circle(spinner_lip_clip_thickness+spinner_lip_diameter_rear/2)
    .workplane(offset=spinner_lip_length)
    .circle(spinner_lip_clip_thickness+spinner_lip_diameter_front/2)
    .loft()
    )

spinner_cut = (
    cq.Workplane("YZ")
    .circle(spinner_lip_diameter_rear/2)
    .extrude(2)
    .faces(">X").workplane()
    .circle(spinner_lip_diameter_rear/2)
    .workplane(offset=spinner_lip_length)
    .circle(spinner_lip_diameter_front/2)
    .loft()
    )

spinner_clip = spinner_clip-spinner_cut

show_object(spinner_clip)