# build123d model template

# %%

from build123d import *
from ocp_vscode import *
from utils import show_or_export

# %% parameters

a = 1 * IN
b = 2 * IN
c = 3 * IN

# %% body

body = Box(length=a, width=b, height=c)

# %% show/export

show_or_export(body)

# %%
