import cadquery as cq

exploded_view_spacer = 20

window_thickness = 1.25
window_diameter  = 24

reflector_thickness = 10.5
reflector_outer_diameter = 23.5
reflector_inner_diameter = 21.5
reflector_depth_front = 7.15
reflector_depth_rear = 1.8

led_diameter = 5
led_ring_diameter = 15.2

def make_front_window():
    fw = cq.Workplane("XZ")
    fw = fw.circle(window_diameter/2)
    fw = fw.extrude(window_thickness)

    return fw

def make_reflector():
    r = cq.Workplane("XZ")
    r = r.circle(reflector_outer_diameter/2)
    r = r.extrude(reflector_thickness)

    r = r.faces("<Y")
    r = r.hole(reflector_inner_diameter)

    r = r.faces("<Y").workplane(offset=-reflector_depth_front)
    r = r.circle(reflector_outer_diameter/2)
    r = r.extrude(reflector_thickness-reflector_depth_front-reflector_depth_rear)

    # Center LED
    r = r.faces("<Y")
    r = r.hole(led_diameter, reflector_thickness)

    # Perimeter LEDs
    r = r.faces("<Y")
    r = r.polygon(8,led_ring_diameter).vertices()
    r = r.hole(led_diameter, reflector_thickness)

    return r

la = cq.Assembly()
offset_y = window_thickness
la = la.add(
    make_front_window(),
    name = "window",
    color = cq.Color(1,1,1,0.2),
    loc = cq.Location((0,offset_y,0)))

offset_y += exploded_view_spacer
offset_y += reflector_thickness
la = la.add(
    make_reflector(),
    name = "reflector",
    color = cq.Color(0.9, 0.9, 0.9),
    loc = cq.Location((0,offset_y,0)))

show_object(la)