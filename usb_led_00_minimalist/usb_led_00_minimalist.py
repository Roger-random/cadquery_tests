import cadquery as cq

def make_front_window():
    window_diameter  = 24
    window_thickness = 1.25
    
    fw = cq.Workplane("XZ")
    fw = fw.circle(window_diameter)
    fw = fw.extrude(window_thickness)
    
    return fw


la = cq.Assembly()
la = la.add(
    make_front_window(),
    name = "window",
    color = cq.Color(1,1,1,0.2))

show_object(la)