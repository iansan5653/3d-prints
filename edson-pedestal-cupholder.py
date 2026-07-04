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

cupholder_body = {
    "outer_diameter": 4.5 * IN,
    "inner_diameter": 3.5 * IN,
    "height": 5 * IN,
    "handle_width": 0.5 * IN
}

radio_clip = {
    "large_diameter": 0.625 * IN,
    "small_diameter": 0.325 * IN,
    "large_depth": 0.125 * IN,
    "small_depth": (0.275 - 0.125) * IN
}

# %%

cupholder_wall_thickness = (cupholder_body["outer_diameter"] - cupholder_body["inner_diameter"]) / 2

body = Cylinder(radius=cupholder_body["outer_diameter"] / 2, height=cupholder_body["height"])
cup_cutout = Cylinder(radius=cupholder_body["inner_diameter"] / 2, height=cupholder_body["height"] - cupholder_wall_thickness)

body = body - cup_cutout

# %%

show(body)

# %%

exporter = Mesher()
exporter.add_shape(body)
exporter.add_code_to_metadata()
exporter.write("heater_intake_vent.3mf")

# %%
