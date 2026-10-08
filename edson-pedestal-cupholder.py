# %%

# The markers "# %%" separate code blocks for execution (cells)
# Press shift-enter to exectute a cell and move to next cell
# Press ctrl-enter to exectute a cell and keep cursor at the position
# For more details, see https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter

# %%

from math import cos, isclose, radians, sin

from build123d import *
from ocp_vscode import *
from utils import show_or_export

# %%

cupholder_od = 4 * IN
cupholder_id = 3.5 * IN
cupholder_height = 3.5 * IN
cup_handle_width = 0.625 * IN

cupholder_wall_thickness = (cupholder_od - cupholder_id) / 2
cupholder_floor_thickness = cupholder_wall_thickness * 2

radio_clip_large_diameter = 0.625 * IN
radio_clip_small_diameter = 0.325 * IN
radio_clip_large_depth = 0.125 * IN
radio_clip_small_depth = (0.275 - 0.125) * IN
radio_clip_cut_depth = (1/2) * IN

center_fastener_diameter = 5/16 * IN
center_fastener_cbr_diameter = 3/4 * IN
center_fastener_cbr_depth = 1/4 * IN

offset_fastener_diameter = 3/16 * IN
offset_fastener_cbr_diameter = 5/16 * IN
offset_fastener_cbr_depth = 3/16 * IN

slot_count = 8
slot_height = cupholder_height - 1 * IN
slot_width = cup_handle_width

groove_height = (1/16) * IN
groove_opening_clearance = (1/4) * IN
outer_edge_fillet_radius = (1/32) * IN

# %% utils

align_min_z = (Align.CENTER, Align.CENTER, Align.MIN)
align_max_z = (Align.CENTER, Align.CENTER, Align.MAX)

# %% main cupholder body

body = Cylinder(
    radius=cupholder_od / 2,
    height=cupholder_height,
    align=align_min_z
)
top_face = body.faces().sort_by(Axis.Z)[-1]

cup_cutout_body = Cylinder(
    radius=cupholder_id / 2,
    height=cupholder_height - cupholder_floor_thickness,
    align=align_max_z
)

body = body - (top_face.center_location * cup_cutout_body)

bottom_inside_face = body.faces().sort_by(Axis.Z)[1]
body = fillet(bottom_inside_face.edges(), (1/8) * IN)


# %% radio clip cutout

clip_cutout_angle = radians(1/16 * 360)
clip_cutout_plane = Plane(
    origin=(
        -cupholder_od / 2 * sin(clip_cutout_angle),
        cupholder_od / 2 * cos(clip_cutout_angle),
        cupholder_height - radio_clip_cut_depth
    ),
    z_dir=(sin(clip_cutout_angle), -cos(clip_cutout_angle), 0)
)
clip_inner_cutout = clip_cutout_plane * Cylinder(
    radius=radio_clip_small_diameter / 2,
    height=cupholder_wall_thickness,
    align=align_min_z
)
clip_outer_cutout = clip_cutout_plane.offset(radio_clip_large_depth) * Cylinder(
    radius=radio_clip_large_diameter / 2,
    height=cupholder_wall_thickness,
    align=align_min_z
)
clip_cutout_body = clip_inner_cutout + clip_outer_cutout

clip_cross_section = section(clip_cutout_body, Pos(
    clip_cutout_plane.origin) * Plane.XY)
clip_cutout_body += extrude(clip_cross_section, amount=radio_clip_cut_depth)

body_without_cutout = body
body -= clip_cutout_body

top_face = body.faces().sort_by(Axis.Z)[-1]
cutout_fillet_edges = new_edges(body_without_cutout, combined=body) & top_face.edges(
) | clip_cutout_plane.location.z_axis

body = fillet(cutout_fillet_edges, (1/8) * IN)

# %% fastener holes

bottom_inside_face = body.faces().sort_by(Axis.Z)[1]

center_location = bottom_inside_face.center_location

body -= center_location * CounterBoreHole(
    radius=center_fastener_diameter / 2,
    counter_bore_depth=center_fastener_cbr_depth,
    counter_bore_radius=center_fastener_cbr_diameter / 2,
    depth=cupholder_floor_thickness
)

offset_location = Pos((1 + (1/8)) * IN, 0, 0) * center_location

body -= offset_location * CounterBoreHole(
    radius=offset_fastener_diameter / 2,
    counter_bore_depth=offset_fastener_cbr_depth,
    counter_bore_radius=offset_fastener_cbr_diameter / 2,
    depth=cupholder_floor_thickness
)

# %% handle slot

handle_slot_z_inset = cupholder_floor_thickness * 2

body_without_handle_slot = body
body -= Pos(0, 0, handle_slot_z_inset) * Box(cupholder_od, cup_handle_width,
                                             cupholder_height, align=(Align.MAX, Align.CENTER, Align.MIN))

handle_slot_fillet_edges = new_edges(
    body_without_handle_slot, combined=body) | Axis.X

body = fillet(handle_slot_fillet_edges, (1/8) * IN)

# %% material saving slots

single_slot_box = center_location * \
    Box(cupholder_od, slot_width, slot_height,
        align=(Align.MAX, Align.CENTER, Align.MIN))
single_slot_box = fillet(single_slot_box.edges(), (1/8) * IN)

slot_boxes = [Rot(0, 0, (360 / slot_count) * i)
              for i in range(1, slot_count)] * single_slot_box

body -= slot_boxes

# %% outer edge fillets

outer_face = body.faces().filter_by(
    GeomType.CYLINDER).sort_by(SortBy.RADIUS)[-1]
outer_fillet_edges = outer_face.edges().sort_by(Axis.Z)[1:]
body = fillet(outer_fillet_edges, outer_edge_fillet_radius)

# %% aesthetic cutout

## Creates a torus around the exterior of the cup, stopping at an offset from each edge in the way
def groove_cutter(body, z, end_clearance=0):
    cross_section = section(body, Plane(origin=(0, 0, z)))
    circular_edges = cross_section.edges().filter_by(GeomType.CIRCLE)
    outer_radius = max(edge.radius for edge in circular_edges)
    outer_arcs = [
        edge for edge in circular_edges
        if isclose(edge.radius, outer_radius)
    ]

    if not end_clearance:
        return Pos(0, 0, z) * Torus(outer_radius, groove_height / 2)

    groove_segments = []
    for outer_arc in outer_arcs:
        if outer_arc.length <= 2 * end_clearance:
            raise ValueError("Groove arc is too short for the end clearance")

        groove_path = outer_arc.trim(
            end_clearance / outer_arc.length,
            1 - end_clearance / outer_arc.length
        )
        profile_plane = Plane(
            origin=groove_path @ 0,
            z_dir=groove_path % 0
        )
        groove_segment = sweep(
            profile_plane * Circle(groove_height / 2),
            groove_path,
            is_frenet=True
        )
        groove_segments.append(
            groove_segment
            # round the ends:
            + Pos(groove_path @ 0) * Sphere(groove_height / 2)
            + Pos(groove_path @ 1) * Sphere(groove_height / 2)
        )

    return Compound(children=groove_segments)


body_bounds = body.bounding_box()
slot_bounds = single_slot_box.bounding_box()
groove_offset = (slot_bounds.min.Z - body_bounds.min.Z) / 2

bottom_groove_z = body_bounds.min.Z + groove_offset
top_groove_z = body_bounds.max.Z - groove_offset

body -= groove_cutter(body, bottom_groove_z)
body -= groove_cutter(body, top_groove_z, groove_opening_clearance)

# %% show/export

show_or_export(body)

# %%
