# %%

# The markers "# %%" separate code blocks for execution (cells)
# Press shift-enter to exectute a cell and move to next cell
# Press ctrl-enter to exectute a cell and keep cursor at the position
# For more details, see https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter

# %%

from build123d import *
from ocp_vscode import *

# %%

cupholder_od = 4.5 * IN
cupholder_id = 3.5 * IN
cupholder_height = 5 * IN
cup_handle_width = 0.5 * IN

radio_clip_large_diameter = 0.625 * IN
radio_clip_small_diameter = 0.325 * IN
radio_clip_large_depth = 0.125 * IN
radio_clip_small_depth = (0.275 - 0.125) * IN
radio_clip_cut_depth = 1 * IN

# %% utils

align_min_z = (Align.CENTER, Align.CENTER, Align.MIN)
align_max_z = (Align.CENTER, Align.CENTER, Align.MAX)

# %% main cupholder body

cupholder_wall_thickness = (cupholder_od - cupholder_id) / 2

body = Cylinder(
  radius=cupholder_od / 2,
  height=cupholder_height,
  align=align_min_z
)
top_face = body.faces().sort_by(Axis.Z)[-1]

cup_cutout_body = Cylinder(
  radius=cupholder_id / 2,
  height=cupholder_height - cupholder_wall_thickness,
  align=align_max_z
)

body = body - (top_face.center_location * cup_cutout_body)

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

clip_cross_section = section(clip_cutout_body, Pos(outer_tangent_xz_plane.origin) * Plane.XY)
clip_cutout_body += extrude(clip_cross_section, amount = radio_clip_cut_depth)

body -= clip_cutout_body

# %% draw

show(body)

# %%

# exporter = Mesher()
# exporter.add_shape(body)
# exporter.add_code_to_metadata()
# exporter.write("cupholder.3mf")

# %%
