# build123d model for a 3D printable router template for rounding a corner with
# maximum alignment guides and sufficient room for clamps with large router base

# %%

from build123d import *
from ocp_vscode import *

# %% parameters

board_width = (5 + (1/16)) * IN
corner_radius = 1/2 * IN

# %% body

thickness = (1/4) * IN

body = Box(length=board_width, width=board_width, height=thickness)
top_plane = Plane(body.faces().sort_by(Axis.Z)[-1])

# %% corner radius

# farthest edge in the x and y directions that runs along the z axis
corner_edges = body.edges().filter_by(Axis.Z)
corner_edge = corner_edges.sort_by(Axis.Y).sort_by(Axis.X)[-1]

body = fillet(corner_edge, radius=corner_radius)

# %% alignment guides

alignment_setback = 1 * IN

guide_box = Box(thickness, board_width - alignment_setback,
                thickness * 2, align=[Align.MIN, Align.MIN, Align.MAX])

back_y_corner = corner_edges.sort_by(-Axis.Y).sort_by(Axis.X)[-1] @ 1

y_guide = Pos(back_y_corner) * guide_box

diagonal_plane = Plane([(0, 0, 0), (1, 1, 0), (0, 0, 1)])

x_guide = mirror(y_guide, diagonal_plane)

body += y_guide + x_guide

# %% material saving cutouts

half_board_width = board_width/2
cutout = top_plane * offset(Rectangle(board_width, board_width), -3/4 * IN)
brace = top_plane * make_face(offset(Line((-half_board_width, -half_board_width), (half_board_width, half_board_width)), 1/4 * IN))
cutout -= brace

body_before_cutout = body
body -= extrude(cutout, -thickness)

body = fillet(new_edges(body_before_cutout, combined=body) | Axis.Z, radius=1/4 * IN)

# %% show

show(body)

# %% export

exporter = Mesher()
exporter.add_shape(body)
exporter.add_code_to_metadata()
exporter.write("corner-router-template.3mf")

# %%
