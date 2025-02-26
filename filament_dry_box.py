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

import cadquery as cq

class filament_dry_box:
    """
    3D-printed filaments tend to pick up moisture to varying degrees (depending
    on chemical formulation) and that moisture interferes with the process of
    printing. Sometimes the interference is negligible and can be safely
    ignored but not always. There are lots of solutions floating around the
    internet for keeping filament dry. Here is my take building something
    tailored to my personal preferences.
    """
    def __init__(self):
        pass

    def generate_box():
        return cq.Workplane("XY").box(1,2,3)

if 'show_object' in globals():
    box = filament_dry_box()
    show_object(box.generate_box(), options={"color":"blue", "alpha":0.5})
