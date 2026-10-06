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

## Template files

Several Excel templates are provided in the [**Excel Templates**](https://github.com/Macrostrat/column-ingestion/tree/main/Excel%20Templates) folder as starting points for column ingestion.
All templates follow the same format, with differences primarily in which fields are available by
default in the `units` sheet.
Some documentation is provided in the templates themselves, but this is subsidiary to the full specification
provided below.

New to the format? Start with the [**quickstart guide**](./Column%20ingestion%20quickstart.md) and the
[guided template](https://github.com/Macrostrat/column-ingestion/raw/main/Excel%20Templates/column-ingestion-template.xlsx). The template is built to be read alongside the guide: its
tabs follow the guide's steps, headers are colour-coded by whether a field is required, and each data tab is paired
with an example tab explaining every field.

### Editing the guided template

The guided template is generated from a human-readable description,
[`Excel Templates/column-ingestion-template.yaml`](https://github.com/Macrostrat/column-ingestion/blob/main/Excel%20Templates/column-ingestion-template.yaml): every tab, field,
header colour, hover note, dropdown and example row is defined there (interval names for the age dropdowns are in
`Excel Templates/interval-names.txt`). To change the template, edit the YAML and build it with the
`column_template` Python package in this repository:

```bash
make template     # build column-ingestion-template-new.xlsx from the YAML, then check the quickstart guide
make promote      # replace the published template with the -new copy, then run the tests
make quickstart   # only check the quickstart guide
make test         # check the published Excel file and the quickstart guide both match the YAML
```

`make template` never touches the published `Excel Templates/column-ingestion-template.xlsx`: it writes
`column-ingestion-template-new.xlsx` beside it, so the original and the new version can be compared. The `-new` copy
is a local review file and is ignored by git. Once it looks right, `make promote` copies it over the published
template; commit that together with the YAML.

`make test` builds a fresh copy from the YAML and compares it with the published `.xlsx`. It fails after the YAML is
edited until the new version is promoted, as a reminder that the template people download is out of date (it also
catches the published `.xlsx` being edited by hand).

The first command you run creates a private Python environment in `.venv/` and installs the package into it, so
nothing is installed into your system Python (this also avoids the "externally-managed-environment" error from
Homebrew's Python). `make clean` deletes it; `make install` rebuilds it.

The [quickstart guide](./Column%20ingestion%20quickstart.md) is written by hand, so it is checked rather than
regenerated. `make template`, `make quickstart` and `make test` fail if:

- a field in the YAML isn't named in the guide's section for its tab: document it there, or mark it
  `quickstart: false` in the YAML if the guide should leave it out;
- the guide's tables list a field that no longer exists on that tab in the YAML.

The environment is created with `python3` (3.10 or newer); pass `SYSTEM_PYTHON=...` to use another
(e.g. `make template SYSTEM_PYTHON=python3.12`).

## [Full specification](./Full%20specification.md)

## Examples

Several example datasets are provided in the [**Examples**](https://github.com/Macrostrat/column-ingestion/tree/main/Examples) folder, including both
chronostratigraphic columns and measured sections.

- An excerpt of the [Eastern European Platform chronostratigraphic chart](https://github.com/Macrostrat/column-ingestion/raw/main/Examples/Eurasia-Eastern-European-Platform-chronostratigraphic.xlsx)
  from the Russian Geologic Survey, showing capture of regional chronostratigraphic data (Evgeny Mazko, 2025).
- A [generalized lithostratigraphic column](https://github.com/Macrostrat/column-ingestion/raw/main/Examples/Zebra-River-Group-generalized.xlsx) from southern Namibia,
  showing a minimal height-based column with a basic age model (Daven Quinn, 2026).
- [Detailed measured sections for the Zebra River Group](https://github.com/Macrostrat/column-ingestion/raw/main/Examples/Zebra-River-Group-Measured-sections-full.xlsx), showing a fully
  developed dataset including bed-scale measured section data, facies information, and datasets beyond this specification linked
  into the column framework (samples, notes, carbon isotope measurements, and sequence-stratigraphic surfaces) (Daven Quinn, 2026).
- [Nine measured sections from the southern Marble Mountains](https://github.com/Macrostrat/column-ingestion/raw/main/Examples/hogan-2011-marble-mountains.xlsx), California
  (Wood Canyon Formation), digitized from a published figure, showing a simple facies-based section correlated on a
  datum bed. It is the worked example for the [quickstart guide](./Column%20ingestion%20quickstart.md)
  (data from Hogan et al., 2011).

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
- Top positions are inferred from the unit above, so each unit needs only a `b_pos` (plus a `t_pos` on the topmost unit) if there are no gaps or overlaps within a section.
- Shorthand fields relating to typical lithostratigraphic measurement practices, such as `grainsize` and `covered`.

Most importantly, unit descriptions such as `lithology`, `strat_name`, and `facies` can "fill down" into blank
cells below them (with `fill_values: y` in the **Metadata** sheet), allowing for more rapid data entry when many
adjacent units share similar characteristics. See [Attribute filling](./Full%20specification.md#attribute-filling).

## Next steps

This spec will be refined as it is used by the community. Potential improvements are described in the [**Future updates**](./Future%20updates.md) document.

Ingestion of this format is now available, as part of the **Macrostrat v2** effort:

- **Upload on the Macrostrat website** at `/columns/new` ("Upload data"). Any signed-in user can run a **dry run**,
  which performs the full ingest and then undoes it, reporting errors without saving anything; a successful dry run
  opens the parsed columns in the column editor. Saving columns to the database is limited to administrators.
- **Command line**, for maintainers: `macrostrat columns ingest <file> [--dry-run]`.

Not every field in this spec is used yet. In particular, the **Facies** and **Images** sheets, column-linked data
sheets, column- and project-level age defaults, and the alternate formats (GIS layers, BibTeX) are accepted in a
workbook but not yet read by the ingester; see the [full specification](./Full%20specification.md) for details.

Planned workflows include:

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
