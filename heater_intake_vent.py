# %%

# The markers "# %%" separate code blocks for execution (cells)
# Press shift-enter to exectute a cell and move to next cell
# Press ctrl-enter to exectute a cell and keep cursor at the position
# For more details, see https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter

# %%

from build123d import *
from ocp_vscode import *
from build123d.topology import Shape


def vector_to(a: Shape, b: Shape):
    pt_a, pt_b = a.closest_points(b)
    return pt_b - pt_a


# %%


duct_id = 60 * MM
wall_thickness = (1/8) * IN
face_thickness = (7/16) * IN
face_depth = (1/8) * IN
fastener_count = 3

vent_radius = duct_id / 2 - wall_thickness
duct_circle = Circle(radius=duct_id / 2)
vent_circle = offset(duct_circle, -wall_thickness)

# Build face plate
face_plate = extrude(
    (offset(vent_circle, face_thickness) - vent_circle), face_depth)
front_face = Plane(face_plate.faces().sort_by(Axis.Z)[-1])

face_plate = chamfer(face_plate.edges().filter_by(GeomType.CIRCLE).sort_by(
    SortBy.RADIUS)[-2:].sort_by(Axis.Z)[-1], 3/64 * IN)

# Drill countersink fastener holes for #6 screw
no6_fastener_hole = CounterSinkHole(
    radius=0.164/2 * IN,
    counter_sink_radius=0.312/2 * IN,
    depth=1 * IN
)
hole_locations = front_face * \
    PolarLocations(radius=vent_radius +
                   (face_thickness / 2), count=fastener_count, start_angle=90)
face_plate -= hole_locations * no6_fastener_hole

vent: Part = face_plate

# Add male side
insert_path = Plane.YZ * Polyline((0, 0), (0, -1/2 * IN), (0.5 * IN, -2 * IN))
duct_male_insert = sweep(
    (duct_circle - vent_circle), insert_path, transition=Transition.ROUND)

vent += duct_male_insert

# Build vent bars
vent_bar_count = 7
vent_bar_depth = 1/2 * IN
vent_bar = Rotation(25, 0, 0) * Box(duct_id,
                                    wall_thickness * (2/3), vent_bar_depth)

# Repeat vent bars and cut to fit
vent_bar_locations = front_face * \
    (GridLocations(0, duct_id / vent_bar_count, 1, vent_bar_count))
vent_bars = Compound(vent_bar_locations * vent_bar)

# Move bars so that bottom edge is coincident with face plane
vent_bar_bottom = vent_bars.edges().sort_by(Axis.Y)[0].center()
z_offset_to_align_face = vent_bar_bottom.project_to_plane(
    front_face) - vent_bar_bottom
y_offset_to_open_bottom = (0, duct_id / vent_bar_count * (4/5), 0)
vent_bars = Pos(z_offset_to_align_face + y_offset_to_open_bottom) * vent_bars

# Trim bars to fit
vent_bars &= extrude(front_face * vent_circle, -vent_bar_depth)

vent += vent_bars

# Drainage notch
bottom_edge = vent.edges()\
    .filter_by(GeomType.CIRCLE)\
    .filter_by(lambda e: e.radius == vent_radius and (e @ 0).Z == front_face.origin.Z)\
    .sort_by(Axis.Y)[0]
notch_plane = front_face.shift_origin(bottom_edge @ 0.5)
notch_circle = notch_plane * Circle(radius=1/16 * IN)
notch_path = notch_plane.rotated(
    (0, 90, 0)) * Line((0, 0), (1/2 * IN, 1/16 * IN))
notch = sweep(notch_circle, notch_path)
vent -= notch

show(vent)

# %%

exporter = Mesher()
exporter.add_shape(vent)
exporter.add_code_to_metadata()
exporter.write("heater_intake_vent.3mf")

# %%
