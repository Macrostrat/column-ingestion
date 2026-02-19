# Macrostrat column ingestion format

These templates and format specification for stratigraphic column data allow preparation of stratigraphic information
for ingestion into Macrostrat using tabular formats (e.g., Excel spreadsheets). These ingestion templates
were created in 2025-2026 by Evgeny Mazko and Daven Quinn for use by the broader geology
community.

> [!caution]
> This is a draft document describing ongoing work. The format described here
> is subject to change as the specification is implemented.


## Overview

These column ingestion sheets can be used to describe chronostratigraphic charts (i.e., based on age),
measured sections (height), or boreholes (depth), using the following sheets of tabular data.

- The [`units` sheet](./Format%20documentation.md#the-units-sheet) is the core of the ingestion format,
  carrying information about individual stratigraphic units and their positions within a column (in age or depth/height space).
- The [`columns` sheet](./Format%20documentation.md#the-columns-sheet) carries metadata about columns
- The [`metadata` sheet](./Format%20documentation.md#the-metadata-sheet) carries information about the project, compiler, and import defaults
- Other ancillary sheets (e.g., `facies`, `refs`) provide additional metadata that helps fill the data table
- [*Column associated data sheets*](./Format%20documentation.md#column-associated-data-sheets)
  can be included to provide additional information about units, facies, or other aspects of the column.

Altogether, these formats provide a flexible way to describe stratigraphic columns and associated information.
They are good target for data ingestion but may also serve as an easy-to-produce archival format as well (e.g., for
paper supplementary materials).

Columns ingested using these tools will be ready to be represented in Macrostrat's database and open-source visualization tools. For example:

- [**Las Animas Arch** composite column](https://dev.macrostrat.org/columns/77)
- [**ODP Site U1332, Hole C** borehole log](https://dev.macrostrat.org/columns/5113#facet=fossil-taxa) showing integration with PBDB for fossil taxa.

## Template files

Several Excel templates are provided in the [**Excel Templates**](./Excel%20Templates) folder as starting points for column ingestion.
All templates follow the same format, with differences primarily in which fields are available by
default in the `units` sheet.
Some documentation is provided in the templates themselves, but this is subsidiary to the full format documentation
provided below.

## [Format documentation](./Format%20documentation.md)

## Examples

Several example datasets are provided in the [**Examples**](./Examples) folder, including both
chronostratigraphic columns and measured sections.

- An excerpt of the [Eastern European Platform chronostratigraphic chart](./Examples/Eurasia-Eastern-European-Platform-Chronostratigraphic.xlsx)
  from the Russian Geologic Survey, showing capture of regional chronostratigraphic data (Evgeny Mazko, 2025).
- A [generalized lithostratigraphic column](Zebra-River-Group-Generalized.xlsx) from southern Namibia,
  showing a minimal height-based column with a basic age model (Daven Quinn, 2026).
- [Detailed measured sections for the Zebra River Group](./Examples/Zebra-River-Group-Detailed.xlsx), showing a fully
  developed dataset including bed-scale measured section data, facies information, and datasets beyond this specification linked
  into the column framework (samples, notes, carbon isotope measurements, and sequence-stratigraphic surfaces) (Daven Quinn, 2026).

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

**Composite columns** (in Macrostrat, `col_type: "column"`) represent
chronostratigraphic charts with no direct physical measurement of
unit thicknesses or positions. Instead, units are defined by their age ranges.
For chronostratigraphic columns, age information must be provided to define an
age model, in the form of relative positions within chronostratigraphic
intervals (e.g., "Lower Silurian", "Upper Devonian"). _Absolute_ ages are not
currently supported.

### Measured sections

**Measured sections** are detailed stratigraphic or borehole logs defined in terms of physical positions
(height or depth). These columns (`col_type: "section"`) are typically much
more detailed than chronostratigraphic charts (i.e., an individual unit may
represent a single cm- to meter-scale bed, rather than an entire Formation or
Member). Measured sections are typically simpler than chronostratigraphic
columns, without overlapping units or complex hierarchical structures.
Efficient entry of these columns is supported by several affordances for rapid
data entry, including:

- A **Facies** table, which summarizes of environmental and lithologic information that can be applied across many units
- Top and bottom positions are inferred, allowing only one of `t_pos` or `b_pos` to be specified if there are no gaps or overlaps within a section.
- Shorthand fields relating to typical lithostratigraphic measurement practices, such as `grainsize` and `covered`.

Most importantly, unit descriptions such as `lithology`, `environment`, and `facies` can "fill up" to subsequent
units, allowing for more rapid data entry when many adjacent units share similar characteristics.

## Next steps

This spec will be refined as it is used by the community. Potential improvements are described in the [**Future updates**](./Future%20updates.md) document.
This spec for ingestion is not currently supported by ingestion scripts, but this work is in progress as part of
the **Macrostrat v2** effort. Ingestion scripts will target the following workflows:

- Creation and revision of columns to the Macrostrat website and database (with appropriate permissions)
- Offline validation and visualization
- Creation of Geopackage-based relational datasets for offline use and editing (using a prototype
  `.mcol` Macrostrat column exchange format)

These tools
will allow progressive enhancement of an in-progress stratigraphic dataset and eventual
inclusion into the Macrostrat database for broader use.


## Support

This work is part of the "Macrostrat v2" effort and is supported by the National Science Foundation
under grant [OAC-2311091](https://www.nsf.gov/awardsearch/showAward?AWD_ID=2311091&HistoricalAwards=false) to Daven Quinn and
collaborators.
