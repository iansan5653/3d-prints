# %%

# The markers "# %%" separate code blocks for execution (cells)
# Press shift-enter to exectute a cell and move to next cell
# Press ctrl-enter to exectute a cell and keep cursor at the position
# For more details, see https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter

# %%

from build123d import *
from ocp_vscode import *
from utils import show_or_export

# %%

cupholder_od = 4.5 * IN
cupholder_id = 4 * IN
cupholder_height = 4.5 * IN
cup_handle_width = 0.5 * IN

cupholder_wall_thickness = (cupholder_od - cupholder_id) / 2
cupholder_floor_thickness = cupholder_wall_thickness * 2

radio_clip_large_diameter = 0.625 * IN
radio_clip_small_diameter = 0.325 * IN
radio_clip_large_depth = 0.125 * IN
radio_clip_small_depth = (0.275 - 0.125) * IN
radio_clip_cut_depth = (3/4) * IN

center_fastener_diameter = 5/16 * IN
center_fastener_cbr_diameter = 3/4 * IN
center_fastener_cbr_depth = 1/4 * IN

offset_fastener_diameter = 3/16 * IN
offset_fastener_cbr_diameter = 5/16 * IN
offset_fastener_cbr_depth = 3/16 * IN

slot_count = 10
slot_height = cupholder_height - 1.5 * IN
slot_width = cup_handle_width

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

outer_tangent_xz_plane = Plane(
    origin=(0, cupholder_od / 2, cupholder_height - radio_clip_cut_depth),
    z_dir=(0, -1, 0)
)
clip_inner_cutout = outer_tangent_xz_plane * Cylinder(
    radius=radio_clip_small_diameter / 2,
    height=cupholder_wall_thickness,
    align=align_min_z
)
clip_outer_cutout = outer_tangent_xz_plane.offset(radio_clip_large_depth) * Cylinder(
    radius=radio_clip_large_diameter / 2,
    height=cupholder_wall_thickness,
    align=align_min_z
)
clip_cutout_body = clip_inner_cutout + clip_outer_cutout

clip_cross_section = section(clip_cutout_body, Pos(
    outer_tangent_xz_plane.origin) * Plane.XY)
clip_cutout_body += extrude(clip_cross_section, amount=radio_clip_cut_depth)

body_without_cutout = body
body -= clip_cutout_body

top_face = body.faces().sort_by(Axis.Z)[-1]
cutout_fillet_edges = new_edges(body_without_cutout, combined=body) & top_face.edges(
) | outer_tangent_xz_plane.location.z_axis

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

# %% show/export

show_or_export(body)

# %%
