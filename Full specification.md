# Macrostrat column ingestion format: full specification

Version `0.2.0` - October 9, 2026

Macrostrat stratigraphic columns can be ingested from tabular formats (such as Excel spreadsheets)
that follow a defined template. Details on the required sheets and fields are provided below.

- New to the format? The [**quickstart guide**](./Column%20ingestion%20quickstart.md) covers the essentials for building
  a column spreadsheet; this document describes every sheet, field, and option.
- See the [**Examples**](https://github.com/Macrostrat/column-ingestion/tree/main/Examples) folder for example datasets.
- The [**Future updates**](./Future%20updates.md) documents collects features that may be included in future versions of this format.

This format can help prepare columns for assimilation into Macrostrat and may be useful as a lightweight archival
specification for column-based information (e.g., for paper supplements).

## Overview of sheets

- [**Units**](#the-units-sheet): Core table defining stratigraphic units
- [**Columns**](#the-columns-sheet): Metadata for each column
- [**Metadata**](#the-metadata-sheet): High-level project metadata
- [*Refs*](#the-refs-sheet): Reference information for citations
- [*Facies*](#the-facies-sheet): User-defined facies descriptions
- [*Images*](#the-images-sheet): Images associated with columns
- [*Column-linked data sheets*](#column-linked-data-sheets): Arbitrary datasets linked to columns (_Prototype_)

Some data can be provided in alternate formats:

- Column and project metadata can be provided as layers in an associated GIS file instead of in the `geom` and `rgeom` fields
- References can be provided as a BibTeX or BibJSON file instead of a `refs` sheet
- Column images can be provided as separate image files, if included

General considerations:

- All tables can include `comments` and/or `notes` for additional notes or clarifications.
- Extra columns will be skipped, allowing non-conforming data to be carried alongside this spec
- Extra sheets will also be ignored (although sheets following a certain format will be treated as [column-linked data](#column-linked-data-sheets))

## The `units` sheet

The core table for defining units within a column. Each row represents a
rock unit, placed by the surface it begins at (see [Column position](#column-position)),
with ages tied to its surfaces (see [Chronostratigraphic position](#chronostratigraphic-position)).

### Unique identifiers

- `unit_id`: Unique identifier for each stratigraphic unit
  Not usually required, but useful to track changes between versions or reference in other tables
  At a minimum, units must be unique within a column
- `col_id`: Unique identifier linking stratigraphic unit to a specific column
  Required if multiple columns are provided in the same spreadsheet
- `section_id`: Unique identifier for each section (packages of units bounded by age gaps)
  Required only if there are multiple sections per column. Sections can also be inferred
  from gaps in [chronostratigraphic position](#chronostratigraphic-position) fields.

### Column position

The most important aspect of a stratigraphic column is the vertical position of
each unit. A column is a stack of **surfaces** (contacts) with **units** of rock between
them, laid out along the column's **axis** (`axis_type`, set in the
[**Columns**](#column-metadata-fields) or [**Metadata**](#column-type-defaults) sheet):

- `height`: measured position, increasing upward (e.g., meters above the base of a section).
  The default for **Measured columns** (`col_type: measured`).
- `depth`: measured position, increasing downward (e.g., meters below the top of a core).
- `age`: an ordination of stratigraphic surfaces, numbered forward in time from oldest to youngest
  (see [Age axes](#age-axes)). The default for **Composite columns** (`col_type: composite`).

#### How positions work

Each row records one surface and the unit that follows it along the axis. Walking up a
measured section, that surface is the unit's base; logging down a core, it is the unit's
top. Most columns need only **one position per row**, and each unit runs
from its own position to the next row's.

The last unit has no next row, so the sheet ends with a **closing row that holds only a
position**: the top of the section, or the base of the core. It is not a unit; it marks
the surface where the column ends.

A measured section (`axis_type: height`):

| `position` | `lithology`    | `strat_name`          |
|-----------:|----------------|-----------------------|
| 9.7        |                |                       |
| 8.3        | sandstone      |                       |
| 6.9        | conglomerate   |                       |
| 0          | sandstone      | Wood Canyon Formation |

This is three units: sandstone from 0 to 6.9 m, conglomerate from 6.9 to 8.3 m and
sandstone from 8.3 to 9.7 m, with the empty row at 9.7 m closing the section. With
`fill_values: y`, `strat_name` carries up from the base to all three.

Both examples put the top of the column at the top of the sheet, as a column is drawn.
The ingester sorts rows by position, so any order works.

In a core with `axis_type: depth`, positions read downward:

| `position` | `lithology` |
|-----------:|-------------|
| 0          | ooze        |
| 3.2        | chalk       |
| 7.5        |             |

This is ooze from 0 to 3.2 m and chalk from 3.2 to 7.5 m, with the row at 7.5 m marking
the base of the core.

The rest of the format builds on this model:

- **Gaps** break the stack: a row named `gap` marks the base of missing rock.
  **Overlaps** need explicit `b_pos` / `t_pos` (see [Constraints](#constraints)).
- **Covered intervals** are units like any other, marked by a row named `covered` or by
  the `covered` field.
- **Age axes** number surfaces instead of measuring them. The next surface is simply the
  next number, so no closing row is needed (see [Age axes](#age-axes)).
- **Ages** belong to surfaces too: `b_int` / `t_int` constrain the surfaces a unit begins
  and ends at, and the age model fills in the rest
  (see [Chronostratigraphic position](#chronostratigraphic-position)).
- **Filling** runs in the same direction: a value carries from a row to the rows after it
  along the axis (see [Attribute filling](#attribute-filling)).

#### Positional fields

- `position`: Position of the row's surface, where the unit begins along the axis (synonyms: `pos`,
  `height`, `depth`). It is the base of the unit on a height or age axis, and its top on a depth axis.
- `b_pos`: Position of the unit's stratigraphic base
- `t_pos`: Position of the unit's stratigraphic top

`b_pos` and `t_pos` name the base and top directly on any axis; on a depth axis, `b_pos`
is the larger number.

For physical thicknesses of units in **Composite columns**, see the
[thickness fields](#thickness).

#### Constraints

- A unit extends from its surface to the next surface along the axis. On height and
  depth axes, that is the next row's position; on an age axis, it is the next number.
- A row whose `unit_name` or `lithology` is `gap` marks missing rock: its position ends
  the unit below it, and no unit is created up to the next row. Its other descriptive
  values are ignored; a `b_int` / `b_prop` on it dates its surface.
- A row whose `unit_name` or `lithology` is `covered` is a covered unit, as with
  `covered: y` (see [Lithology](#lithology)). Written in place of the lithology, it leaves
  the lithology unknown.
- For overlaps, or for gaps without a `gap` row, give `b_pos` and `t_pos` explicitly. Explicit
  values override those inferred from adjacent rows. Complex overlapping relationships
  can be described by units that share `b_pos`/`t_pos` values.
- `b_pos` must lie stratigraphically below `t_pos`: it is the smaller number on a height
  or age axis, and the larger on a depth axis.
- On height and depth axes, the last row along the axis is the empty closing row
  (see [How positions work](#how-positions-work)): it closes the unit before it and is
  not a unit itself, so its descriptive values are ignored. A `b_int` / `b_prop` on it
  dates the closing surface. Instead of a closing row, the last unit can give an explicit
  `t_pos` (`b_pos` on a depth axis).
- A `height` column on a depth axis, or a `depth` column on a height axis, raises a warning,
  since it usually means `axis_type` is wrong.
- Every row needs a position (`position`, `b_pos` or `t_pos`) on every axis, Composite
  Columns included. Row order in the sheet is never used, so rows can be sorted freely.
  Rows without a position are left out, with a warning.

#### Age axes

On an age axis, positions are a sequence of events numbered forward in time, with `1`
the oldest. Each number names a stratigraphic surface: a unit at position `n` rests on
surface `n` and is capped by surface `n + 1`.

- Units with consecutive numbers are in contact. A skipped number is a missing event:
  time that passed with no rock recorded.
- Units that share a number are laterally equivalent.
- A unit spanning several events gives both `b_pos` and `t_pos`.
- Positions order the column's surfaces but carry no age of their own. Each surface takes
  its age from the age model (see [Chronostratigraphic position](#chronostratigraphic-position)):
  between tie points, surfaces are spaced evenly in time by their numbers.

#### Attribute filling

For **Measured columns**, units are often defined at small (meter- to sub-meter)
scale, reflecting the scale of rock attributes captured during field stratigraphic
measurement or core logging. It can be tedious to enter repeated values for attributes
that change infrequently.

With filling enabled (`fill_values: y` in the **Columns** or **Metadata** sheet; off by
default), descriptive fields left blank are carried from the preceding unit. For
instance, a single `strat_name` at the base of a formation can be applied to every
measured unit above it, up to the next unit where a new value is entered.

- A blank cell in a filled field takes the value of the preceding unit along the axis,
  in the direction position numbers increase: values carry **upward** on a height axis and
  **downward** on a depth axis. Enter a value at the base of the interval it applies to
  in a measured section, and at the top of the interval in a core. Cells holding only
  spaces count as blank.
- `none` (in any case) in a filled field means the unit has no value, and ends the run.
- `covered` and `gap` written as a `unit_name` or `lithology` describe that row only: they
  are not carried, and a run continues past them.
- Values carry within a section, not between sections.
- Filled fields: `lithology`, `minor_lith`, `environment`, `grainsize`, `color`,
  `strat_name`, `unit_name`, `facies`.
- Never filled: `unit_description`, `comments`, `basal_surface`, `lateral_relationship`,
  `covered`, the positional fields, and the chronostratigraphic fields (`b_int`, `t_int`,
  `b_prop`, `t_prop`), which follow their own rules
  (see [Chronostratigraphic position](#chronostratigraphic-position)).
- [Covered](#lithology) units take and pass on values like any other unit. A blank
  lithology directly above a covered unit therefore inherits that unit's inferred lithology.
- Filling never applies on an age axis. Positions there record the order of events, and
  lateral equivalents share positions, so the preceding unit is not well defined.

### Chronostratigraphic position

Chronostratigraphic position columns are used to tie a column's positional axis
to geologic time. Ages are entered only at **tie points**, and an age model fills in the rest.
This is essential for **Composite columns** (since the primary axis
of the column is based on age) but optional for **Measured columns**.

- Each section needs **at least two tie points at different positions** for an age model to be built.
  With fewer, the ingester skips the age model for that section (with a warning), and its units keep
  only the ages written on them.
- Between tie points, ages are interpolated linearly by position.
- Beyond the highest or lowest tie point, ages are **not** extrapolated: a boundary outside the
  tie points takes the age of the nearest one. Add a tie point near the top and base of a section
  if their ages matter.
- Boundaries you give are recorded with status `relative`; boundaries the model fills in are
  recorded as `modeled`.

- `b_int` : Geologic interval at the bottom boundary of the unit. Name (e.g., "Devonian") or Macrostrat interval ID;
  names are listed in [Macrostrat's interval list](https://dev.macrostrat.org/lex/intervals)
- `t_int` : Geologic age at the top boundary of the unit. Name (e.g., "Devonian") or Macrostrat interval ID
- `b_prop` : Position of the bottom boundary of the unit, relative to its interval (optional)
- `t_prop` : Position of the top boundary of the unit, relative to its interval (optional)

Some additional approaches to chronostratigraphic compilation are described in the
[Future updates](./Future%20updates.md#future-chronostratigraphic-fields) document.

#### Constraints

- These fields constrain surfaces: `b_int`/`b_prop` set the age of the unit's base surface, and
  `t_int`/`t_prop` the age of its top surface. Neither is required; a surface given one is a tie point.
- A blank `b_prop` is read as `0` (the oldest end of the interval), so give an estimate rather than
  leaving it blank. A `t_int` with a blank `t_prop` is read as `1` (the youngest end).
- Adjacent units share a surface, so a surface can be constrained from either side: by the base
  of the unit above it or the top of the unit below it. A unit with only `b_int` takes its top age
  from the unit above, so usually only the topmost unit needs `t_int`/`t_prop`, or the empty
  closing row a `b_int`/`b_prop` (see [How positions work](#how-positions-work)). If the two sides
  disagree, the narrower interval is used and a warning is raised.
- `b_int` must be older than `t_int` (if both provided)
- `b_prop` and `t_prop` must be between 0 and 1
- Correlated horizons in different columns should be given the same `b_int` and `b_prop`.

- Values of these fields that do not match ordering provided by `b_pos`/`t_pos`
  will raise warnings during ingestion.
- Column- and project-level `b_int` / `t_int` fields (in the **Columns** and **Metadata** sheets)
  are descriptive only: the ingester does not currently use them to build or fill an age model.

### Names and descriptions

- `unit_name`: Display name of the rock unit
- `unit_description`: Original description of the stratigraphic unit from stratigraphic chart or supplemental materials, if provided

These fields are generally important for Composite columns but optional for Measured columns.

### Stratigraphic names

Stratigraphic names are formal (or potentially formal) names associated with a unit. Often, they will be linked specifically
to an external lexicon, such as [Macrostrat's stratigraphic lexicon](https://dev.macrostrat.org/lex/strat-names).

- `strat_name`: Stratigraphic unit name(s) associated with the unit.

#### Formatting stratigraphic names

Typically, names can be found in [Macrostrat's stratigraphic lexicon](https://dev.macrostrat.org/lex/strat-names); in this
case, only the formal name needs to be provided.

If names are not linked to an external lexicon, multiple stratigraphic names can be expressed in hierarchical chains
(member → formation → group → supergroup).
This allows multiple alternative or related hierarchies to be attached to one unit, if necessary.

- Use commas `,` to separate child and parent within a single chain.
- Use semicolons `;` to separate distinct name chains.
- Common rank indicators (e.g., "Member", "Formation") and/or shorthands (e.g., "Sandstone", "Shale") should be included for clarity.

#### Examples

- Single name: `Molas Formation`
- Name chain: `Alexandria Bay Gneiss, Piseco Group, Adirondack Supergroup`
- Multiple names: `Dry Creek Canyon Member, Dakota Sandstone; Burro Canyon Formation`
- Non-standard names: `Lower Member, Ubisis Formation; Bed A, Ubisis Formation`
- Macrostrat IDs: `1234; 5678`
- Other lexicon IDs: `usgs:22438, usgs:9876; Lower Member, gsc:5432`
  **Note:** Lexicon-specific prefixes are not yet implemented.

### Lithology

The lithology fields collectively describe the type of rock present in a unit.

- `lithology`: Primary lithology of the unit (single or list)
- `minor_lith`: Secondary lithology of the unit (optional; single or list).
- `grainsize`: Optional grain size description for the unit. This is a shorthand field
  that is used to set lithology attributes where not defined.
  **Examples:**
  - Lithology attributes of type "grains": `fine-grained`, `coarse-grained`
  - Common shorthands: `ms`, `s`, `vf`, `f`, `m`, `c`, `p` (**Not recommended**; use full terms where possible)
  - Numeric values, in _φ_ units
- `covered`: Boolean field to denote that the unit is present but unexposed. A covered unit keeps its place
  and thickness in the column, and time passes through it in the age model. Lithology and other descriptions
  given for a covered unit are treated as inferred. Ingested as `outcrop: covered` on the unit.
  Covered units on a depth axis raise a warning. Writing `covered` as the unit's `unit_name` or `lithology`
  does the same (see [Constraints](#constraints)).
- Lithology names are listed in [Macrostrat's lithology lexicon](https://dev.macrostrat.org/lex/lithologies).

#### Constraints and format

- The `lithology` and `minor_lith` fields should be formatted as `<attribute> <proportion>, <attribute> <lith> <proportion>; <attribute>, <attribute> <lith>`.
- `<lith>` is a standard lithology term (e.g., sandstone, shale, limestone). Lithologies should be present in
  [Macrostrat's lithology lexicon](https://dev.macrostrat.org/lex/lithologies), but new terms can also be added.
- `<attribute>` is an optional modifier (e.g., `fine-grained`, `arkosic`, `calcareous`). Lithologies should be present
  in [Macrostrat's lithology attribute lexicon](https://dev.macrostrat.org/lex/lith-atts), but other terms can also be added,
  which will be skipped with a warning on ingestion.
- `<proportion>` is an optional parenthetical containing a proportion of the lithology within the unit (or attribute within the lithology).
  It can be expressed as a number between 0 and 1, a percentage, or a qualitative proportion (`major` or `minor`). If omitted, all lithologies are assumed
  to be present in equal proportions.
- The `minor_lith` field is a shorthand to set lithologies with a `(minor)` proportion by default.

> **Preview how your text is parsed.** The [lithology matcher](https://dev.macrostrat.org/lex/lith-match)
> runs the ingester's own lithology parser over any `lithology` / `minor_lith`
> text and shows the lithologies, attributes and proportions it recognises — and
> flags any words it can't match — so you can refine your wording before you submit.

### Environment

- `environment`: Depositional environment interpretation; free text (e.g., "fluvial", "shallow marine") or [Macrostrat environment](https://dev.macrostrat.org/lex/environments)

### Facies

- `facies`: Comma- or semicolon- separated list of facies associated with this unit, with optional proportions. These should be referred
  to values of the `facies_id` field in the [**Facies** sheet](#facies) (if provided).

#### Constraints and format

- Multiple facies can be expressed as `<facies_name> (<proportion>)`, where `<proportion>` is a number
  between 0 and 1, a percentage, or a qualitative proportion (`major` or `minor`). Multiple facies are separated by semicolons `;` or commas `,`.
- If no proportion is provided, all facies are assumed to be present in equal proportions.

### Thickness

- `min_thickness`: Minimum thickness of the unit (in position units; e.g., meters)
- `max_thickness`: Maximum thickness of the unit (in position units; e.g., meters)

These fields are required for **Composite columns** only. For
[**Measured columns**](#column-position), they will be
inferred from the `b_pos` and `t_pos` fields to match the measured physical height of the unit.

### Misc. unit descriptors (_optional, experimental_)

These fields provide additional notes or clarifications about a unit's
relationship with adjacent units. They do not yet have a defined vocabulary and
are currently being evaluated for future use within Macrostrat.

- `basal_surface`: Description of the basal surface of the unit
  Examples: `conformable`, `disconformable`, `unconformable`, `fault`, `gradational`, `sharp`, `erosional`
- `lateral_relationship`: A description of how the unit relates laterally to adjacent units (only applicable
  when there are multiple overlapping units)
  Examples: `interfingering`, `transgressive`, `onlaps`, `erosional`, `gradational`

## The `columns` sheet

The **Columns** sheet contains metadata for each column in the project. Each row represents a single column, which should
be linked to units in the **Units** sheet via the `col_id` field. This sheet is required: units are only ingested for
columns listed here.

- `col_id`: Unique identifier for a column (string or integer; required if multiple columns per spreadsheet)
- `col_name`: Name for the column (required)
- `col_group`: Group of the column (optional)
- `date_collected`: Date or date range of collection (if applicable)
- `geom`: Primary geometry of the column
- `lng`,`lat`: Position of the column

#### Constraints and format

Either a `lng`,`lat` pair or a `geom` is required.

- `lng`,`lat`: decimal degrees (WGS84); longitudes west of Greenwich are negative. Use this for a point location.
- `geom`: a _Well-known text_ (e.g. drawn with [wktmap.com](https://wktmap.com/)) geometry:
  - `POLYGON` or `MULTIPOLYGON`, for a column that covers an area;
  - `LINESTRING` or `MULTILINESTRING`, for a measured traverse. The column is placed at a point on the line,
    and has no area.

  Points are rejected here; give a point location as `lng`,`lat` instead.
- If both are given, the geometry wins: the column's position is taken from inside the polygon, with a warning
  if the `lng`,`lat` point falls outside it. A point within 1 km of a traverse line is kept as the column's
  position.

### Column metadata fields

_All fields in this category are optional._

The following metadata fields set the type and spatial/temporal context of a column dataset.
These will override project-level defaults where provided.
See [Chronostratigrahic position](#chronostratigraphic-position) for more details.

- `ref_ids`: References (keyed to refs table); comma- or semicolon-separated list
- `axis_type` : `height`, `depth` or `age` (see [Column position](#column-position)); defaults to `age` for
  Composite Columns and `height` for Measured columns
- `col_type`: `measured` or `composite` (defaults to `composite`). The older names `section` and `column` are
  read the same way.
- `fill_values`: Whether to fill blank unit attributes along the axis (see [Attribute filling](#attribute-filling));
  overrides the **Metadata** default. Accepts the same values
- `rgeom`: Reference geometry of the column, its "area of influence" (optional; falls back to `geom` if not provided)
- `b_int`: Lowest interval considered during the drafting of the column (if applicable)
- `t_int`: Highest interval considered during the drafting of the column (if applicable)
- `b_prop`: Position within the lowest interval (if known; fraction between 0 and 1)
- `t_prop`: Position within the highest interval (if known; fraction between 0 and 1)

The `b_int`, `t_int`, `b_prop` and `t_prop` fields here are descriptive only; the age model is built from the
tie points in the **Units** sheet.

### Column location

For most columns, `rgeom` will not be set. This field handles cases where a column is assigned an "area of influence" beyond its
actual measured location. This is useful to denote that certain columns are representative of a study area. In most cases,
Macrostrat will automatically infer this information.

Column location fields (both `geom` and `rgeom`) can also be provided as layers (with `col_id` and/or `project_id`
fields to map  to specific columns) in an associated GIS file.

## The `metadata` sheet

The **Metadata** sheet contains high-level information about a stratigraphic
dataset, including the name, organization, compilers, and default settings for columns
within the project.

- __Unlike other sheets, this sheet is laid out as key-value pairs, with one field per row.__
- If the project cannot be identified (no `project_name` or `project_id`), ingestion fails.

### Basic compilation information

- `project_name` : Name of the project **(required, unless `project_id` identifies an existing project)**
- `organization` : Organization that originated the project
- `url` : URL to a landing page for the project, if applicable
- `project_id` : A unique identifier of the project (string or integer)
- `compiler_orcid` : ORCIDs
- `compile_date` : Date digitally compiled
- `compiler_name` : Name(s) of compilers, string; either `compiler_name` or `compiler_orcid` are required

### Column type defaults

- `col_type` : Default column type (`measured` or `composite`; the older `section` and `column` also work);
  defaults to `composite`
- `axis_type` : Default axis type: `height`, `depth` or `age` (see [Column position](#column-position)); defaults
  to `age` for Composite Columns and `height` for Measured columns
- `fill_values`: Default for whether to fill blank unit attributes along the axis
  (see [Attribute filling](#attribute-filling)). `y`, `yes` or `true` turns filling on; `n`, `no`, `false` or a
  missing row leaves it off. Any other value leaves it off, with a warning.

### Spatial and stratigraphic context

Optional fields to provide context for the scope of the project. They are descriptive only: the ingester
does not currently use them as defaults for column ages or locations.

- `b_int` : Lowest interval considered during the compilation effort (if applicable)
- `t_int` : Highest interval considered during the compilation effort (if applicable)
- `b_prop`: Position within the lowest interval (Default: 0)
- `t_prop`: Position within the highest interval (Default: 1)
- `rgeom` : Reference geometry of the project area, its "area of influence" (optional). Can be provided
  as a layer (with a `project_id` field) in an associated GIS file.


### Definitions

- `position_unit` : The unit that spatial positions are expressed in; default: meter
- `time_unit` : The unit that temporal positions are expressed in; default: meter
- `timescale` : Name or Macrostrat ID of default timescale for age intervals; default: ICS ages
- `srid` : The spatial reference frame that geometries are expressed in; default: EPSG:4326


## The `refs` sheet

The **References** sheet contains citation information for references used in the project. Each row represents a single reference, which should
be linked to columns in the **Columns** sheet via the `ref_id` field (if references differ between columns).
This sheet can also be provided as a BibTeX or BibJSON file alongside the spreadsheet.

## The `facies` sheet

The optional **Facies** sheet contains user-defined facies descriptions that can be linked to units in the **Units** sheet.
Each row represents a single facies, as part of a facies scheme for the project.
Facies are named categories that are analogous to map units, in that they describe a set of patterns observed in
field-based stratigraphy that are used to drive interpretations.

> [!NOTE]
> Facies are new and experimental in Macrostrat's ingestion system, and do not currently map to a specific
> data model within Macrostrat.

The sheet is entirely optional. In its simplest form, used by the templates, it is a string-keyed list of
lithologies and environments with a description:

| `facies_id` | `lithology` | `environment` | `description` |
|---|---|---|---|
| F1 | desiccation cracks, laminated, fine sandstone (10%); lime mudstone | peritidal | Mud-cracked lime mudstone with thin laminated sandstone beds. |
| F2 | hummocky cross stratification, gutter casts grainstone; lime mudstone (minor); shale (minor) | offshore ramp | Storm-reworked grainstone between lime mudstone and shale. |

- `facies_id`: Unique identifier for each facies (string or integer; required), given by units in their `facies` field
- `facies`: Name of the facies (optional)
- `facies_group`: Grouping of the facies (optional)
- `description`: Description of the facies
- `lithology`: Lithologies associated with the facies, formatted like the `lithology` field in the **Units** sheet
- `interpretation`: Interpretation of depositional environment or processes associated with the facies
- `environment`: Depositional environment associated with the facies; formatted like the `environment` field in the **Units** sheet

## The `images` sheet

The optional **Images** sheet contains information about images associated with columns in the project,
and optionally the images themselves (either pasted into the Excel sheet or as separate image files). The
templates' `images` tab is this sheet: paste the figure a column was captured from onto it, and describe it
in a row.
This is designed to allow the source material for column digitization to be carried alongside the data.

- `col_ids`: Column ID or comma-separated list of IDs (if image contains multiple columns)
- `image_name`: Name of image (should match the name of the Excel embed or associated file)
- `ref_id`: Reference this image was extracted from (keyed to the refs table)
- `page_no`: Page number within reference (optional)
- `fig_no`: Figure number within reference (optional)
- `description`: Description/caption for the image (optional)

## Column-linked data sheets

> [!NOTE]
> Column-linked data sheets are experimental and currently do not have defined behavior in Macrostrat system itself.
> However, this will be improved in future versions of the system, with plugins to load and link different data "facets".

Often, stratigraphic columns are packaged with attribute information that can be presented alongside the column, without
being part of a core unit definition. Examples include **geochemical data, fossil occurrences, geochronologic data**, or
notes and interpretations that are outside the scope of Macrostrat's core data models. This is most often the case
for **Measured columns**, but it can also apply to **Composite Columns**.

Ingested Excel templates can include any number of additional sheets beyond the core sheets defined above.

- All sheets that include the necessary positioning fields to link them to a column and heights will be treated as column-linked data.
- Beyond these positioning fields, attribute sheets can contain any number of additional fields.
- Column-linked data can also be loaded from GIS layers, provided that they contain the necessary positioning fields.

### Positioning relative to a column

A column attribute sheet must position each row relative to the column's
height/depth or age model. As such, attribute sheets must reference a specific column:

- `col_id`: Unique identifier for the column (string or integer; required)
- `section_id`: Optional unique identifier for the section within the column (string or integer; only required if multiple sections per column)

Attributes must also reference a height (or range of heights) in the column's reference frame. This can be done
by reusing the positioning fields from the [**Units** sheet](#the-units-sheet).
Like units, attributes can be positioned _absolutely_ (via measured positions, with `b_pos` and `t_pos`) or _relatively_ (via
intervals and proportions, with `b_int`, `t_int`, `b_prop`, and `t_prop`).
Additionally, since the unit sheet is separately defined, attributes can be positioned relative to specific stratigraphic units,
via `unit_id` (optionally, extended with `b_unit_id`, `t_unit_id`, `b_prop`, and `t_prop`).

### Spatial location

It is common for datasets that might be linkable to a column to have their own spatial information,
distinct from the column's geometry. To this end, attribute sheets can also include a `geom` or
`geometry` field to define the spatial location of each attribute record.


## Field aliases

Some fields have common synonyms that will be recognized during ingestion. Here is a partial index:

- `project_id`: `project_slug`
- `col_id`: `column_id`, `column_slug`, `col_slug`
- `lithology`: `major_lithology`, `major_lith`, `lith`
- `minor_lith`: `minor_lithology`
- `position`: `pos`, `height`, `depth` (the surface where the unit begins along the axis; see [Column position](#column-position))
- `b_pos`: `b_position`, `bottom_position`, `base_position`, `position_bottom`, `bottom`, `base`, `bottom_height`,
  `base_height`, `bottom_depth`, `base_depth`
- `t_pos`: `t_position`, `top_position`, `position_top`, `top`, `top_height`, `top_depth`
- `unit_name`: `name`
- `unit_description`: `description`
- `b_int`: `b_interval`, `interval`
- `t_int`: `top_interval`, `t_interval`
- `geom`: `geometry`
- `rgeom`: `ref_geometry`, `ref_geom`
- `min_thickness`: `min_thick`, `thickness`
- `max_thickness`: `max_thick`
- `facies`: `facies_id`, `facies_ids`



