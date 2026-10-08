---
name: render-model
description: "Render, export, open, and visually inspect build123d 3D models in this repository. Use when creating or changing a model, checking CAD geometry, regenerating 3MF/STL/SVG outputs, previewing a part, or reviewing whether a model looks correct."
argument-hint: "model-name.py"
---

# Render and View a Model

Use the bundled renderer so model execution and artifact validation are
consistent:

```bash
python3 .github/skills/render-model/scripts/render_model.py <model-name.py>
```

The model must be a root-level Python file that calls `show_or_export`. A
successful run regenerates and validates:

- `output/<model-name>/<model-name>.3mf`
- `output/<model-name>/<model-name>.stl`
- `output/<model-name>/<model-name>.svg`

It also creates a white-background PNG preview under
`.render-model-previews/` and prints its absolute path as `Preview PNG:`.

## Visually inspect the result

For agent inspection, pass the `Preview PNG:` path to the image-viewing tool.
Do not infer the model's appearance from source code or the SVG text. Actually
view the PNG before describing or approving the geometry.

- For the user, run the renderer with `--open` to open the PNG in VS Code.
- For interactive CAD inspection, run the model's `# %%` cells in VS Code.
  `show_or_export` sends notebook output to the ocp-vscode viewer, where the
  model can be rotated and individual faces can be inspected.

Check the preview for the intended overall form, missing or unexpected
features, disconnected geometry, and obviously incorrect scale or orientation.
An SVG is a fixed isometric hidden-line view, so use the ocp-vscode viewer when
the requested check depends on another angle or internal geometry.

## After editing a model

1. Render the changed model with the bundled script.
2. Visually inspect the PNG (and use ocp-vscode when one view is insufficient).
3. Confirm all three artifacts were regenerated.
4. Use `git status --short` to ensure only the intended source and generated
   model outputs changed.

Do not edit generated 3MF, STL, or SVG files by hand.
