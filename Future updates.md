# Future updates

This ingestion format is under active development as part of the Macrostrat v2 project, and
will continue to evolve over time. This document collects draft specifications that may be included
in future iterations of the ingestion format.

## Additional `units`/`facies` fields for visualization

It may be useful to control the appearance of units or facies in column renderings.
To that end, the following fields are being evaluated for future versions of the ingestion template.

- `color`: Color associated with the unit (hex code or named color)
- `symbol_color`: Color associated with the unit
- `symbol`: FGDC symbol associated with the unit or facies


## Future chronostratigraphic fields

Chronostratigraphy is one of the most important and complex aspects of stratigraphic columns,
so there are many ways to express age constraints. Several fields are in evaluation for more
flexible age modeling in future versions of these ingestion templates.

### Absolute ages

Units tied to absolute ages are supported within Macrostrat, but their overuse
allows inconsistent age models to be introduced without appropriate checks. We will
support absolute ages in future versions, once appropriate constraints are introduced.

- `t_age`: Absolute age of the top boundary of the unit (**not yet implemented**).
- `b_age`: Absolute age of the bottom boundary of the unit (**not yet implemented**).

### Correlated surfaces

Each unit implicitly has a _surface_ at its top and bottom boundaries. In some cases, these surfaces
can be correlated across columns to build a more consistent age model across
multiple columns. This feature requires a separate **`surfaces` sheet** which
will carry chronostratigraphic information that can be updated simultaneously across multiple units and columns.
The **`units` sheet** would then include the following fields to reference these surfaces:

- `t_surface`: Correlated surface at the top of the unit
- `b_surface`: Correlated surface at the base of the unit

This feature could also rely on a locally defined timescale and hierarchy of intervals.
Since we have not defined a data model for this yet, these fields are not yet implemented.
