# Shared helper for build123d model scripts.
#
# When a script is run interactively (VS Code interactive window / Jupyter
# notebook) the passed parts are shown with ocp_vscode. When the same script is
# run from the command line the parts are exported to `.3mf`, `.stl` and `.svg`
# files whose names are inferred from the source file name.

import sys
from pathlib import Path

from build123d import Compound, ExportSVG, LineType, Mesher, export_stl
from ocp_vscode import show


def is_notebook() -> bool:
    """Return True when running inside an IPython/Jupyter kernel."""
    try:
        # get_ipython is injected into the namespace only inside IPython.
        return get_ipython().__class__.__name__ == "ZMQInteractiveShell"  # type: ignore[name-defined]  # noqa: F821
    except NameError:
        return False


def show_or_export(*parts) -> None:
    """Show the parts in a notebook, or export them on the CLI.

    On the command line the parts are written to `.3mf`, `.stl` and `.svg`
    files whose base name is inferred from the running script's file name.
    """
    if not parts:
        raise ValueError("show_or_export requires at least one part")

    if is_notebook():
        show(*parts)
        return

    base_path = Path(sys.argv[0]).with_suffix("")
    combined = parts[0] if len(parts) == 1 else Compound(children=list(parts))

    mesher = Mesher()
    for part in parts:
        mesher.add_shape(part)
    mesher.add_code_to_metadata()
    mesher.write(str(base_path.with_suffix(".3mf")))

    export_stl(combined, str(base_path.with_suffix(".stl")))

    _export_svg(combined, base_path.with_suffix(".svg"))

    print(f"Exported {len(parts)} part(s) to {base_path}.{{3mf,stl,svg}}")


def _export_svg(shape, path: Path) -> None:
    """Write an isometric hidden-line preview image of ``shape``."""
    visible, hidden = shape.project_to_viewport(
        viewport_origin=(1000, -1000, 1000),
        viewport_up=(0, 0, 1),
        look_at=shape.center(),
    )

    svg = ExportSVG()
    svg.add_layer("visible", line_color=(0, 0, 0), line_weight=0.3)
    svg.add_layer("hidden", line_color=(160, 160, 160),
                  line_weight=0.2, line_type=LineType.ISO_DOT)
    svg.add_shape(visible, "visible")
    svg.add_shape(hidden, "hidden")
    svg.write(str(path))
