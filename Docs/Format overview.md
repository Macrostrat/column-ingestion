# Column ingestion format overview

These column ingestion sheets can be used to describe chronostratigraphic charts (i.e., based on age),
measured sections (height), or boreholes (depth), using the following sheets of tabular data.

- The [`units` sheet](./Full%20specification.md#the-units-sheet) is the core of the ingestion format,
  carrying information about individual stratigraphic units and their positions within a column (in age or depth/height space).
- The [`columns` sheet](./Full%20specification.md#the-columns-sheet) carries metadata about columns
- The [`metadata` sheet](./Full%20specification.md#the-metadata-sheet) carries information about the project, compiler, and import defaults
- Other ancillary sheets (e.g., `facies`, `refs`) provide additional metadata that helps fill the data table
- [*Column-linked data sheets*](./Full%20specification.md#column-linked-data-sheets)
  can be included to provide additional information about units, facies, or other aspects of the column.

Altogether, these formats provide a flexible way to describe stratigraphic columns and associated information.
They are good target for data ingestion but may also serve as an easy-to-produce archival format as well (e.g., for
paper supplementary materials).

Columns ingested using these tools will be ready to be represented in Macrostrat's database and open-source visualization tools. For example:

- [**Las Animas Arch** composite column](https://dev.macrostrat.org/columns/77)
- [**ODP Site U1332, Hole C** borehole log](https://dev.macrostrat.org/columns/5113#facet=fossil-taxa) showing integration with PBDB for fossil taxa.

## Templates

Two Excel templates are provided in the [**Excel Templates**](https://github.com/Macrostrat/column-ingestion/tree/main/Excel%20Templates)
folder as starting points. Both follow the same format and are read the same way on upload; they differ only in
which fields the `units` sheet offers.

- The [**simple template**](https://github.com/Macrostrat/column-ingestion/raw/main/Excel%20Templates/column-ingestion-template-simple.xlsx)
  is a measured column with one `position` per unit, and is the one the [quickstart guide](./Quickstart.md) walks through.
- The [**expanded template**](https://github.com/Macrostrat/column-ingestion/raw/main/Excel%20Templates/column-ingestion-template-expanded.xlsx)
  has every field: separate `b_pos` / `t_pos`, sections, minor lithologies, covered intervals, contacts and top ages.

Their tabs follow the quickstart's steps, headers are colour-coded by whether a field is required, and each data tab
is paired with an example tab explaining every field. This documentation is subsidiary to the
[full specification](./Full%20specification.md).

## Ingestion approach

The `units` sheet is the core of the ingestion format, carrying information
about bodies of rock within a column and the stratigraphic names, lithology,
and environmental information that describe them. However,
the scale of units varies dramatically between scales of stratigraphic columns.
These templates support a range of approaches to defining units, with
shorthands that can speed data entry for common use cases.

Ingestion of chronostratigraphic columns, measured sections, and borehole logs
are supported using the same ingestion process and fields, but the formatting
requirements differ slightly in order to accommodate different patterns that
are present across scales and types of data.

### Composite columns

**Composite columns** (`col_type: composite`) represent
chronostratigraphic charts with no direct physical measurement of
unit thicknesses or positions. Instead, units are defined by their age ranges.
For chronostratigraphic columns, age information must be provided to define an
age model, in the form of relative positions within chronostratigraphic
intervals (e.g., "Lower Silurian", "Upper Devonian"). _Absolute_ ages are not
currently supported.

### Measured columns

**Measured columns** are detailed measured sections or borehole logs defined in terms of physical positions
(height or depth). These columns (`col_type: measured`) are typically much
more detailed than chronostratigraphic charts (i.e., an individual unit may
represent a single cm- to meter-scale bed, rather than an entire Formation or
Member). Measured columns are typically simpler than chronostratigraphic
columns, without overlapping units or complex hierarchical structures.
Efficient entry of these columns is supported by several affordances for rapid
data entry, including:

- A **Facies** table, which summarizes of environmental and lithologic information that can be applied across many units
- Top positions are inferred from the unit above, so each unit needs only one position (plus an empty closing row at the top) where units don't overlap.
- Shorthand fields and rows relating to typical lithostratigraphic measurement practices, such as `grainsize`, `covered`, and rows named `covered` or `gap`.

Most importantly, unit descriptions such as `lithology`, `strat_name`, and `facies` can "fill up" into blank
cells above them (with `fill_values: y` in the **Metadata** sheet; downward, for cores logged by depth), allowing
for more rapid data entry when many adjacent units share similar characteristics. See [Attribute filling](./Full%20specification.md#attribute-filling).
