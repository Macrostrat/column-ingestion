# Macrostrat column ingestion

> [!caution]
> This is a draft document describing ongoing work. The format and features described here
> are subject to change.

These templates and format specification for stratigraphic column data allow users to
format stratigraphic information for ingestion into Macrostrat. These ingestion templates
were created in 2025-2026 by Evgeny Mazco and Daven Quinn for use by the broader geology
community.

## Overview

Ingestion of both chronostratigraphic and lithostratigraphic columns is supported using
the same ingestion process and fields, but the formatting requirements differ slightly
in order to accommodate different patterns in the typical dataset.

- The [`units` sheet](./Format%20documentation.md#units-sheet) is the core of the ingestion format,
  carrying information about individual stratigraphic units and their positions within a column (in age or depth/height space).
- The [`columns` sheet](./Format%20documentation.md#columns-sheet) carries metadata about columns
- The [`metadata` sheet](./Format%20documentation.md#metadata-sheet) carries information about the project, compiler, and import defaults
- Other ancillary sheets (e.g., `facies`, `refs`) provide additional metadata that helps fill the data table
- [*Column associated data sheets*](./Format%20documentation.md#column-associated-data-sheets)
  can be included to provide additional information about units, facies, or other aspects of the column.

Altogether, these formats provide a flexible way to describe stratigraphic columns and associated information.
They are good target for data ingestion but may also serve as an easy-to-produce archival format as well (e.g., for
paper supplementary materials.

They allow column targeting Macrostrat's data structures and visualization formats. For example:

- [**Las Animas Arch** chronostratigraphic column](https://dev.macrostrat.org/columns/77)
- [**ODP Site U1332, Hole C** lithostratigraphic column](https://dev.macrostrat.org/columns/5113#facet=fossil-taxa) showing integration with PBDB for fossil taxa.

## [Format documentation](./Format%20documentation.md)

## Examples

Several example datasets are provided in the [**Examples**](./Examples) folder, including both
chronostratigraphic and lithostratigraphic columns.

- An excerpt of the [Eastern European Platform chronostratigraphic chart](./Examples/Eurasia-Eastern-European-Platform-Chronostratigraphic.xlsx)
  from the Russian Geologic Survey, showing capture of regional chronostratigraphic data (Evgeny Mazco, 2025).
- A [generalized lithostratigraphic column](Zebra-River-Group-Generalized.xlsx) from southern Namibia,
  showing a minimal lithostratigraphic dataset with a basic age model (Daven Quinn, 2026).
- [Detailed measured sections for the Zebra River Group](./Examples/Zebra-River-Group-Detailed.xlsx), showing a fully
  developed dataset including bed-scale lithostratigraphic data, facies information, and datasets beyond this specification linked
  into the column framework (samples, notes, carbon isotope measurements, and sequence-stratigraphic surfaces) (Daven Quinn, 2026).



## Ingestion approach

### Chronostratigraphic columns

For chronostratigraphic columns, the `units` sheet must include age data for each unit, in the form of relative
positions within chronostratigraphic intervals (e.g., "Lower Silurian", "Upper Devonian"). _Absolute_ ages
are not currently supported. These units are assigned information about the stratigraphic names, lithology, and
environmental information that describe the unit.

### Lithostratigraphic columns

Lithostratigraphic columns can be ingested into the same data structures as chronostratigraphic columns,
but they typically are much more detailed (i.e., an individual unit may represent a single cm- to meter-scale
bed, rather than a formation or member). Lithostratigraphic columns are required to have positions defined
in physical units (`t_pos` and `b_pos`); age data is optional and secondary.

Lithostratigraphic columns are typically simpler than chronostratigraphic columns, without overlapping units
or complex hierarchical structures. This allows several affordances for easier data entry:

- A **Facies** table, which summarizes of environmental and lithologic information that can be applied across many units
- Top and bottom positions are inferred, allowing only one of `t_pos` or `b_pos` to be specified if there are no gaps or overlaps within a section.
- Shorthand fields relating to typical lithostratigraphic measurement practices, such as `grainsize` and `covered`.

Most importantly, unit descriptions such as `lithology`, `environment`, and `facies` can "fill up" to subsequent
units, allowing for more rapid data entry when many adjacent units share similar characteristics.

## Next steps

This spec for ingestion is not currently supported by ingestion scripts, but this work is in progress as part of
the **Macrostrat v2** effort. Ingestion scripts will target the following workflows:

- Upload of columns to the Macrostrat website and database
- Revision of existing columns in Macrostrat
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
