import cadquery as cq

mm_per_inch = 25.4

wrench_size = (1/2) * mm_per_inch * 1.05

arm_width = 20
arm_length = 18
thickness = 12

arm_move = arm_length/2

arm = (
    cq.Workplane("XY")
    .box(arm_width, arm_length, thickness)
    .translate((0,arm_move,0))
    )

wrench_head = (
    cq.Workplane("XY")
    .box(wrench_size, wrench_size, thickness*2)
    )

result = arm.union(arm.rotate((0,0,0),(0,0,1),120))
result = result.union(arm.rotate((0,0,0),(0,0,1),-120))

result = result.cut(wrench_head)

result = result.chamfer(1)

show_object(result)
