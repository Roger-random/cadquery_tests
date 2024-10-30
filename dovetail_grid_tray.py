import math
import cadquery as cq

grid_unit_width = 20 #mm
grid_unit_depth = 15 # mm
cell_height = 25 #mm

cell_grid_width = 1
cell_grid_depth = 1

tray_gap = 0.1 #mm

cell_width = cell_grid_width * grid_unit_width
cell_depth = cell_grid_depth * grid_unit_depth

edge_chamfer = 1
corner_fillet = 2

label_depth = 10 / math.sqrt(2)

def build_dovetail_x(
    dovetail_gap = 0,
    dovetail_depth = grid_unit_width * 0.25,
    dovetail_width = grid_unit_width * 0.5):
    dovetail = (
        cq.Workplane("XY")
        .lineTo(0,                  dovetail_depth/2, forConstruction = True)
        .lineTo( dovetail_width/2, -dovetail_depth/2)
        .lineTo(-dovetail_width/2, -dovetail_depth/2)
        .close()
        .extrude(cell_height)
        )
    if dovetail_gap > 0:
        dovetail_subtract = dovetail.faces("|Z").shell(-dovetail_gap)
        dovetail = dovetail - dovetail_subtract
    elif dovetail_gap < 0:
        dovetail_add = dovetail.faces("|Z").shell(-dovetail_gap)
        dovetail = dovetail + dovetail_add

    return dovetail

def build_dovetail_y(
    gap = 0,
    depth = grid_unit_depth * 0.25,
    width = grid_unit_depth * 0.5):
    dovetail = (
        build_dovetail_x(gap, depth, width)
        .rotate((0,0,0), (0,0,1), -90)
        )
    return dovetail

def build_tray():
    tray = (
        cq.Workplane("XY")
        .lineTo(0,          cell_depth)
        .lineTo(cell_width, cell_depth)
        .lineTo(cell_width, 0)
        .close()
        .extrude(cell_height)
        )
    if tray_gap > 0:
        tray_gap_subtract = tray.faces("|Z").shell(-tray_gap)
        tray = tray - tray_gap_subtract
    elif tray_gap < 0:
        raise ArgumentException("Trays with negative gap will not fit together.")

    intersect_volume = (
        cq.Workplane("XY")
        .box(cell_width+grid_unit_width, cell_depth+grid_unit_depth, cell_height)
        .translate((cell_width/2, cell_depth/2, cell_height/2))
        .edges("|X").chamfer(edge_chamfer+grid_unit_depth/2)
        .edges("|Y").chamfer(edge_chamfer+grid_unit_width/2)
        )
    tray = tray.intersect(intersect_volume)
    tray = tray.edges("not (|X or |Y)").fillet(corner_fillet)

    dovetail_offset_y = grid_unit_width * 0.25 * 0.2
    dovetail_offset_x = grid_unit_depth * 0.25 * 0.2
    dovetail_gap = 0.1

    for x_slot in range(cell_grid_width):
        x_position = grid_unit_width/2 + x_slot*grid_unit_width
        tray = tray + (
            build_dovetail_x(dovetail_gap)
            .translate((x_position, dovetail_offset_y, 0))
            )
        tray = tray - (
            build_dovetail_x(-dovetail_gap)
            .translate((x_position, cell_depth+dovetail_offset_y, 0))
            )

    for y_slot in range(cell_grid_depth):
        y_position = grid_unit_depth/2 + y_slot*grid_unit_depth
        tray = tray + (
            build_dovetail_y(dovetail_gap)
            .translate((dovetail_offset_x, y_position, 0))
            )
        tray = tray - (
            build_dovetail_y(-dovetail_gap)
            .translate((cell_width+dovetail_offset_x, y_position, 0))
            )

    tray = tray.intersect(intersect_volume)
    
    if label_depth > 0:
        tray = tray - (
            cq.Workplane("YZ")
            .lineTo(-label_depth, cell_height-label_depth*2,forConstruction=True)
            .lineTo(-label_depth, cell_height)
            .lineTo( label_depth, cell_height)
            .close()
            .extrude(cell_width, both=True))

    return tray

volume = (
    cq.Workplane("XY")
    .lineTo(0,                                 grid_unit_depth * cell_grid_depth)
    .lineTo(grid_unit_width * cell_grid_width, grid_unit_depth * cell_grid_depth)
    .lineTo(grid_unit_width * cell_grid_width, 0)
    .close()
    .extrude(cell_height)
    )
show_object(volume, options = {"alpha":0.9, "color":"green"})

show_object(build_tray(),
    options = {"alpha":0.5, "color":"blue"})
#show_object(build_tray().translate((0,cell_depth,0)), options = {"alpha":0.5, "color":"orange"})
