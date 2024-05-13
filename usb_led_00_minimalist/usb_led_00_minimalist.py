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
led_base_diameter = 5.3
led_base_height = 1.0
led_overall_height = 8.7

led_ring_diameter = 15.2

led_pcb_thickness = 1.25
led_pcb_diameter = 23.5

color_clear_plastic = cq.Color(1,1,1,0.2)
color_pcb = cq.Color(0,0.5,0)
color_mirror_finish = cq.Color(0.7, 0.7, 0.7)

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

def make_led():
    r = cq.Workplane("XY")
    r = r.lineTo(led_base_diameter/2,0)
    r = r.lineTo(led_base_diameter/2,led_base_height)
    r = r.lineTo(led_diameter/2,led_base_height)
    r = r.lineTo(led_diameter/2,led_overall_height-(led_diameter/2))
    r = r.radiusArc((0,led_overall_height),-led_diameter/2)
    r = r.close()
    r = r.revolve()

    return r

def make_led_ring():
    lr = cq.Assembly()
    lr = lr.add(
        (
            cq.Workplane("XZ")
            .circle(led_pcb_diameter/2)
            .extrude(led_pcb_thickness)
        ),
        name = "led_pcb",
        color = color_pcb)
    lr = lr.add(
        make_led(),
        name = "led_center",
        color = color_clear_plastic)

    return lr

la = cq.Assembly()
offset_y = window_thickness
la = la.add(
    make_front_window(),
    name = "window",
    color = color_clear_plastic,
    loc = cq.Location((0,offset_y,0)))

offset_y += exploded_view_spacer
offset_y += reflector_thickness
la = la.add(
    make_reflector(),
    name = "reflector",
    color = color_mirror_finish,
    loc = cq.Location((0,offset_y,0)))

show_object(make_led_ring())