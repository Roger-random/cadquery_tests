import cadquery as cq

grid_unit = 20 #mm
cell_height = 40 #mm

cell_grid_width = 1
cell_grid_depth = 1

cell_spacing = 0.5 #mm
cell_width = cell_grid_width * grid_unit - cell_spacing*2
cell_depth = cell_grid_depth * grid_unit - cell_spacing*2

volume = (
    cq.Workplane("XY")
    .lineTo(0,                           grid_unit * cell_grid_depth)
    .lineTo(grid_unit * cell_grid_width, grid_unit * cell_grid_depth)
    .lineTo(grid_unit * cell_grid_width, 0)
    .close()
    .extrude(cell_height)
    )
show_object(volume,
    options = {"alpha":0.9, "color":"green"})

core = (
    cq.Workplane("XY")
    .lineTo(             cell_spacing,              cell_spacing, forConstruction = True)
    .lineTo(             cell_spacing, cell_depth + cell_spacing)
    .lineTo(cell_width + cell_spacing, cell_depth + cell_spacing)
    .lineTo(cell_width + cell_spacing,              cell_spacing)
    .close()
    .extrude(cell_height)
    )

show_object(core,
    options = {"alpha":0.5, "color":"blue"})
