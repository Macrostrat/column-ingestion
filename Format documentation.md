# Macrostrat column ingestion format documentation

Version `0.1.1` - January 24, 2026

Macrostrat stratigraphic columns can be ingested from tabular formats (such as Excel spreadsheets)
that follow a defined template. Details on the required sheets and fields are provided below.

- See the [**Examples**](./Examples) folder for example datasets.
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
rock unit, with its boundaries defined by age intervals and proportions (for **Composite columns**)
or measured height/depth ranges (for **Measured sections**).

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
each unit. Positional fields help define the unit's vertical position within
the column.

- `b_pos`: Position of the bottom boundary of the unit (synonyms: `position`, `pos`)
- `t_pos`: Position of the top boundary of the unit

For **Measured sections** (`col_type: "section"`), these fields are expressed
in terms of measured heights/depths in physical units (e.g., meters). For
**Composite columns** (`col_type: "column"`), these fields should be a unitless ordination of surface positions (
see [thickness fields](#thickness) for entering approximate physical height for units in
Composite Columns).

#### Constraints

- In simple cases (when units do not overlap), only one of `b_pos` or `t_pos` is required
  to define a unit's position. If only one is provided, the other will be
  inferred from adjacent units. `position` can be used in these cases as a synonym for `b_pos`.
- All `b_pos`/`t_pos` pairs must have a consistent ordering (upwards or
  downwards, depending on whether the column is organized in terms of depth or
  height). Composite Columns can use either ordering, but it must be
  consistent within a column.
- Units that are unbounded at the top or bottom of a section are dropped during
  ingestion, but their `t_pos`,`b_pos` values are still used to infer the
  bounds of units above or below. In practice, this can allow a section to be
  defined with a single `position` column, if an unbounded unit is included at
  the top.
- Complex overlapping relationships can be described by units that share
  `b_pos`/`t_pos` values.
- For Composite Columns, these fields are optional but recommended. If neither
  `b_pos` nor `t_pos` is provided for a unit, positional ordering will be
  inferred from the order of rows in the sheet. This is not recommended, as it
  can easily lead to data loss if rows are reordered.

#### Attribute filling

For **Measured sections** (`col_type: "section"`), units are often defined at
small (meter- to sub-meter) scale, reflecting the scale of rock attributes
captured during field stratigraphic measurement or core logging. It can be
tedious to enter repeated values for attributes that change infrequently.

Unit description fields (`lithology`, `environment`, `grainsize`,
`strat_name`, etc.) can be automatically filled to subsequent units based on
the values of lower units. This allows gradually changing attributes within a wider grouping to be
entered intuitively. For instance, a single `strat_name` setting at the base
of a recognized unit can be applied to an entire set of stratigraphic
measurement within that unit.

- By default, attributes are filled according the numeric ordering of the
  positional axis of the column. That is, for height-based axes (e.g.,
  measured sections) attributes will be filled "up" to stratigraphically higher
  units, and for depth axes (e.g., cores), attributes are filled
  stratigraphically "down".
- The direction of filling can be controlled by the `fill_values` attribute in the
  **Column** or **Metadata** sheets.
- Descriptors that are referenced to an individual unit (`unit_name`,
  `unit_description`, `basal_surface`, `lateral relationship`) are not filled.
  Filling is also disabled if [Positional columns](#column-position) are not defined,
  as the lack of an explicit ordering field for sheets based on relative ages
  can easily lead to data loss.

### Chronostratigraphic position

Chronostratigraphic position columns are used to tie a column's positional axis
to geologic time. At least the top and bottom units of the column must be
defined in chronostratigraphic terms in order for an age model to be applied
This is essential for **Composite columns** (since the primary axis
of the column is based on age) but optional for **Measured sections**.

- `b_int` : Geologic interval at the bottom boundary of the unit. Name (e.g., "Devonian") or Macrostrat interval ID
- `t_int` : Geologic age at the top boundary of the unit. Name (e.g., "Devonian") or Macrostrat interval ID
- `b_prop` : Position of the bottom boundary of the unit, relative to its interval (optional)
- `t_prop` : Position of the top boundary of the unit, relative to its interval (optional)

Some additional approaches to chronostratigraphic compilation are described in the
[Future updates](./Future%20updates.md#future-chronostratigraphic-fields) document.

#### Constraints

- Only one of `b_int`/`t_int` is required; if only one is provided, the unit will be assumed to lie
  within the specified interval, with `b_prop` and `t_prop` defining its relative position.
- `b_int` must be older than `t_int` (if both provided)
- `b_prop` and `t_prop` must be between 0 and 1
- `b_prop` must be less than `t_prop` if provided

- Values of these fields that do not match ordering provided by `b_pos`/`t_pos`
  will raise warnings during ingestion.
- If chronostratigraphic information is not provided within the **Units**
  sheet, it will be inferred from column or project-level defaults in the
  **Columns** or **Metadata** sheets. This will yield highly generalized age
  models and is not recommended.

### Names and descriptions

- `unit_name`: Display name of the rock unit
- `unit_description`: Original description of the stratigraphic unit from stratigraphic chart or supplemental materials, if provided

These fields are generally important for Composite columns but optional for Measured sections.

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
- `covered`: Boolean field to denote whether the unit is covered (implying that any lithology information is uncertain).
  **Note:** This field is not currently used during ingestion

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
[**Measured sections**](#lithostratigraphic-columns), they will be
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
be linked to units in the **Units** sheet via the `col_id` field. If this sheet is not provided, a column can still be
imported, but it will be incomplete pending addition of metadata.

- `col_id`: Unique identifier for a column (string or integer; required if multiple columns per spreadsheet)
- `col_name`: Name for the column (required)
- `col_group`: Group of the column (optional)
- `date_collected`: Date or date range of collection (if applicable)
- `geom`: Primary geometry of the column
- `lng`,`lat`: Position of the column

#### Constraints and format

Either `geom` or a `lng`,`lat` pair are required. The `geom` field can be provided either as two comma-separated values (which
will be interpreted as a point location) or a _Well-known text_ (e.g. [[1]](https://wktmap.com/)) geometry value, which can be
a point, line, or polygon.

### Column metadata fields

_All fields in this category are optional._

The following metadata fields set the type and spatial/temporal context of a column dataset.
These will override project-level defaults where provided.
See [Chronostratigrahic position](#chronostratigraphic-position) for more details.

- `ref_ids`: References (keyed to refs table); comma- or semicolon-separated list
- `axis_type` : Default axis type; defaults to `age` for Composite Columns; filled from defaults if not given
- `col_type`: `section` or `column` (defaults to `column` for chronostratigraphy; `section` for lithostratigraphy)
- `rgeom`: Reference geometry of the column, its "area of influence" (optional; falls back to `geom` if not provided)
- `b_int`: Lowest interval considered during the drafting of the column (if applicable)
- `t_int`: Highest interval considered during the drafting of the column (if applicable)
- `b_prop`: Position within the lowest interval (if known; fraction between 0 and 1)
- `t_prop`: Position within the highest interval (if known; fraction between 0 and 1)

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
- If required metadata is not provided, the user will be prompted to provide it during ingestion.

### Basic compilation information

- `project_name` : Name of the project **(required)**
- `organization` : Organization that originated the project
- `url` : URL to a landing page for the project, if applicable
- `project_id` : A unique identifier of the project (string or integer)
- `compiler_orcid` : ORCIDs
- `compile_date` : Date digitally compiled
- `compiler_name` : Name(s) of compilers, string; either `compiler_name` or `compiler_orcid` are required

### Column type defaults

- `col_type` : Default column type (`section` or `column`); filled from project defaults if not given
- `axis_type` : Default axis type; defaults to `age` for Composite Columns; filled from defaults if not given
- `fill_values`: Default fill value. Whether to fill unit attribute values (strat_name, lithology, environment,
  and related fields) from lower units. Boolean, defaults to `f`, or direction to fill stratigraphically - `up` (default for height-based sections)
  or `down` (default for boreholes)

### Spatial and stratigraphic context

Optional fields to provide context for the scope of the project. These will be used as defaults for
age/spatial information if they are not provided at the column level.

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

- `facies_id`: Unique identifier for each facies (string or integer; required)
- `facies`: Name of the facies (required)
- `facies_group`: Grouping of the facies (optional)
- `description`: Description of the facies
- `lithology`: Lithologies associated with the facies, formatted like the `lithology` field in the **Units** sheet
- `interpretation`: Interpretation of depositional environment or processes associated with the facies
- `environment`: Depositional environment associated with the facies; formatted like the `environment` field in the **Units** sheet

## The `images` sheet

The optional **Images** sheet contains information about images associated with columns in the project,
and optionally the images themselves (either pasted into the Excel sheet or as separate image files).
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
for **Measured sections**, but it can also apply to **Composite Columns**.

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
- `b_pos`: `position`, `pos`, `height`, `depth`, `b_position`, `bottom_position`
- `t_pos`: `top_position`
- `b_int`: `b_interval`, `interval`
- `t_int`: `top_interval`, `t_interval`
- `geom`: `geometry`
- `rgeom`: `ref_geometry`, `ref_geom`
- `min_thickness`: `min_thick`, `thickness`
- `max_thickness`: `max_thick`
- `facies`: `facies_id`, `facies_ids`



