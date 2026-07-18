# build123d model for a 3D printable router template for cutting a half circle in the end of a board

# %%

from build123d import *
from ocp_vscode import *

# %% parameters

board_width = (5 + (1/16)) * IN
cutout_diameter = 3 * IN

# %% body

thickness = (1/4) * IN

body = Box(length=board_width,
           width=(cutout_diameter / 2) + (1 * IN), height=thickness)
top_plane = Plane(body.faces().sort_by(Axis.Z)[-1])

# farthest edge in the y and z directions that runs along the x axis
long_edge = body.edges().filter_by(
    Axis.X).sort_by(Axis.Y).sort_by(Axis.Z)[-1]

mast_cutout = Pos(long_edge @ 0.5) * Rot(top_plane) * \
    Circle(radius=cutout_diameter / 2)

body -= extrude(mast_cutout, amount=-thickness)

# %% fillet

zeroish = 1e-6
cutout_fillet_edges = body.edges() | Axis.Z | (lambda e: e.distance_to(mast_cutout) <= zeroish)

body = body.fillet(radius = (1/8) * IN, edge_list=cutout_fillet_edges)

# %% alignment guides

body_corner = long_edge @ 0
guide_corner = body_corner + (thickness, thickness, 0)
guide_shape_template = Box((1/2) * IN, 1 * IN, 2 * thickness, align=(Align.MAX, Align.MAX, Align.MAX))
guide_outer_shape = Pos(guide_corner) * guide_shape_template
guide_inner_shape = Pos(body_corner) * guide_shape_template
guide = guide_outer_shape - guide_inner_shape
guides = guide + guide.mirror(Plane.YZ)

body += guides

# %% show

show(body)
# %%