# Project Guidelines

## Modeling Style

- Use build123d's algebra mode, matching the existing root-level model files. Do not introduce builder contexts such as `BuildPart` unless algebra mode cannot express the operation clearly.
- Prefer concise shape algebra:
  - `body += feature` for unions.
  - `body -= cutout` for cuts.
  - `shape_a & shape_b` for intersections.
  - `Pos(...) * shape`, `Rot(...) * shape`, and `plane * sketch` for placement.
  - `edge @ parameter`, `edge % parameter`, and `edge ^ parameter` for positions, tangents, and locations along curves.
- Use selector algebra where it improves clarity, such as `edges | Axis.Z`, and use `new_edges(before, combined=after)` to identify edges created by an operation.
- Keep each model organized into focused `# %%` cells: parameters, reusable utilities, major modeling operations, and show/export.

## Geometry Selection

- Query topology instead of depending on creation order, hardcoded coordinates, or manually maintained indices.
- Prefer build123d filtering and sorting methods over custom predicates or Python `max`/`min` calls:

  ```python
  outer_face = body.faces().filter_by(
      GeomType.CYLINDER).sort_by(SortBy.RADIUS)[-1]
  ```

- Filter to the relevant geometry first, sort by the meaningful axis or property, then select with standard indexing or slicing:
  - `[0]` for the lowest or smallest result.
  - `[-1]` for the highest or largest result.
  - `[1:]` or `[:-1]` to exclude an extreme while preserving selector order.

  ```python
  outer_fillet_edges = outer_face.edges().sort_by(Axis.Z)[1:]
  ```

- Prefer a simple sorted slice over naming an edge and subtracting it from a `ShapeList`.
- Re-query geometry after boolean or fillet operations when later selections depend on the modified topology.
- Preserve intermediate shapes with intent-revealing names such as `body_without_cutout` when they are needed by `new_edges`.
- Treat operation order as significant, especially for fillets and booleans. Validate the resulting geometry rather than assuming an equivalent-looking selector produces the same CAD result.

## Parametric Design

- Put user-adjustable dimensions near the top of the model and derive related values from them.
- Express imperial dimensions with `IN`, using readable fractions such as `(1/32) * IN`.
- Prefer names that describe physical intent and dimension type, such as `cupholder_wall_thickness`, `groove_height`, `slot_count`, and `outer_edge_fillet_radius`.
- Derive feature positions and clearances from existing parameters or queried geometry such as face locations, edge positions, sections, and bounding boxes.
- Avoid hardcoded world coordinates when a stable geometric reference can be queried.
- Ensure dependent features continue to move and resize correctly when upstream parameters change.
- Use shared alignment tuples or locations when they make repeated construction intent clearer.

## Code and Comments

- Follow the existing formatting and naming style: snake_case variables, direct shape expressions, and short modeling sections.
- Keep comments sparse. Comment only non-obvious geometric intent, topology-selection reasoning, or an operation-order requirement.
- Do not narrate straightforward construction steps in comments.
- Use descriptive variable names instead of explanatory comments whenever possible.
- Keep changes surgical and avoid unrelated cleanup or stylistic rewrites.

## Rendering and Validation

- Root-level model files must finish with `show_or_export(...)`.
- After changing geometry, render and preview the result with the `render-model` skill.
- Confirm the model remains a valid, connected solid and inspect the specific geometric condition requested when practical.
- Confirm the corresponding `.3mf`, `.stl`, and `.svg` files were regenerated under `output/<model-name>/`.
- Never edit generated model artifacts by hand.
- Use `git status --short` to ensure only the intended source and generated outputs changed.
- For model-only geometry changes, prefer rendering and focused geometry checks over adding tests unless tests are explicitly requested.

## Reference

- Consult the [build123d cheat sheet](https://github.com/gumyr/build123d/blob/dev/docs/cheat_sheet.rst) for algebraic operators, selectors, topology operations, and object constructors.
- Consule the rest of the `gumyr/build123d` repo for documentation.
