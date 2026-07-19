# build123d model template

# %%

from build123d import *
from ocp_vscode import *

# %% parameters

a = 1 * IN
b = 2 * IN
c = 3 * IN

# %% body

body = Box(length=a, width=b, height=c)

# %% show

show(body)

# %% export

# exporter = Mesher()
# exporter.add_shape(body)
# exporter.add_code_to_metadata()
# exporter.write("example.3mf")

# %%
