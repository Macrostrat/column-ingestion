# Macrostrat column ingestion format documentation

Version `0.1.0` - January 21, 2026

Macrostrat stratigraphic columns can be ingested from tabular formats (such as Excel spreadsheets)
that follow a defined template. Details on the required sheets and fields are provided below.

- See the [**Examples**](./Examples) folder for example datasets.
- The [**Future updates**](./Future%20updates.md) documents collects features that may be included in future versions of this format.

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
- Column images are not required and can be provided as separate image files

All tables can include `comments` and/or `notes` for additional notes or clarifications.

## The `units` sheet

The core table for defining units within a column. Each row represents a
rock unit, with its boundaries defined by age intervals and proportions (for **Chronostratigraphic Columns**)
or measured height/depth ranges (for **Lithostratigraphic Columns**).

### Unique identifiers

- `unit_id`: Unique identifier for each stratigraphic unit
  Not usually required, but useful to track changes between versions or reference in other tables
  At a minimum, units must be unique within a column
- `col_id`: Unique identifier linking stratigraphic unit to a specific column
  Required if multiple columns are provided in the same spreadsheet
- `section_id`: Unique identifier for each section (packages of units bounded by age gaps)
  Required only if there are multiple sections per column

### Lithostratigraphic position

Lithostratigraphic position can be expressed in terms of measured heights/depths. This is the primary
height representation for [**Lithostratigraphic Columns**](#lithostratigraphic-columns); for chronostratigraphic
columns, these fields are optional and can be used instead of [thickness fields](#thickness).

- `b_pos`: Measured position of the bottom boundary of the unit (synonyms: `position`, `pos`)
- `t_pos`: Measured position of the top boundary of the unit

#### Constraints

- In simple cases, one of `b_pos` or `t_pos` can often be inferred from adjacent units
- All `b_pos` and `t_pos` pairs must have a consistent ordering (upwards or downwards, depending on whether the column is organized
  in terms of depth or height).
- Units that are unbounded at the top or bottom of a column are dropped during ingestion, but their `t_pos`,`b_pos` values are still used to infer
  the bounds of units above or below. In practice, this can allow a column to be defined with a single `position` column, if an unbounded unit is
  included at the top.

### Chronostratigraphic position

For [**Chronostratigraphic Columns**](#chronostratigraphic-columns), this is the primary height representation.
For [**Lithostratigraphic Columns**](#lithostratigraphic-columns), these fields are optional and can be used
to provide age constraints on units, which will be interpolated during the age modeling process. If chronostratigraphic information is not provided within the **Units** sheet,
it will be inferred from column or project-level defaults in the **Columns** or **Metadata** sheets.

- `b_int` : Geologic interval at the bottom boundary of the unit. Name (e.g., "Devonian") or Macrostrat interval ID
- `t_int` : Geologic age at the top boundary of the unit. Name (e.g., "Devonian") or Macrostrat interval ID
- `b_prop` : Position of the bottom boundary of the unit, relative to its interval (Default: 0)
- `t_prop` : Position of the top boundary of the unit, relative to its interval (Default: 1)

Some additional approaches to chronostratigraphic compilation are described in the
[Future updates](./Future%20updates.md#future-chronostratigraphic-fields) document.

#### Constraints

- Only one of `b_int`/`t_int` is required; if only one is provided, the unit will be assumed to lie
  within the specified interval, with `b_prop` and `t_prop` defining its relative position.
- `b_prop` and `t_prop` must be between 0 and 1
- `b_prop` must be less than `t_prop`
- `b_int` must be older than `t_int` (if both provided)

### Names and descriptions

- `unit_name`: Display name of the rock unit
- `unit_description`: Original description of the stratigraphic unit from stratigraphic chart or supplemental materials, if provided

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

- Lithologies should be formatted as `<attribute> <proportion>, <attribute> <lith> <proportion>; <attribute>, <attribute> <lith>`.
- `<lith>` is a standard lithology term (e.g., sandstone, shale, limestone). Ideally it would be present in
  [Macrostrat's lithology lexicon](https://dev.macrostrat.org/lex/lithologies), but new terms can also be added.
- `<attribute>` is an optional modifier (e.g., `fine-grained`, `arkosic`, `calcareous`). Ideally, it would be present
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

### Thickness (_optional_)

- `min_thickness`: Minimum thickness of the unit (in position units; e.g., meters)
- `max_thickness`: Maximum thickness of the unit (in position units; e.g., meters)

These fields are for chronostratigraphic columns only.
For [**Lithostratigraphic Columns**](#lithostratigraphic-columns), they are overwritten by the `b_pos` and `t_pos` fields.

### Misc. unit descriptors (_optional, experimental_)

These fields provide additional notes or clarifications about a unit, and are currently being evaluated for future
use within Macrostrat.

- `basal_surface`: Description of the basal surface of the unit
  Examples: `conformable`, `disconformable`, `unconformable`, `fault`, `gradational`, `sharp`, `erosional`
- `lateral_relationship`: A description of how the unit relates laterally to adjacent units (only applicable
  when there are multiple overlapping units)
  Examples: `interfingering`, `transgressive`, `onlaps`, `erosional`, `transitional`

## The `columns` sheet

The **Columns** sheet contains metadata for each column in the project. Each row represents a single column, which should
be linked to units in the **Units** sheet via the `col_id` field. If this sheet is not provided, a column can still be
imported, but it will be incomplete pending addition of metadata.

- `col_id`: Unique identifier for a column (string or integer; required if multiple columns per spreadsheet)
- `col_name`: Name for the column (required)
- `col_group`: Group of the column (optional)
- `date_collected`: Date or date range of collection (if applicable)
- `geom`: Primary geometry of the column

### Column metadata fields

_All fields in this category are optional._

The following metadata fields set the type and spatial/temporal context of a column dataset.
These will override project-level defaults where provided.
See [Chronostratigrahic position](#chronostratigraphic-position) for more details.

- `ref_ids`: References (keyed to refs table); comma- or semicolon-separated list
- `axis_type` : Default axis type; defaults to `age` for chronostratigraphic columns; filled from defaults if not given
- `col_type`: `section` or `column` (defaults to `column` for chronostratigraphy; `section` for lithostratigraphy)
- `rgeom`: Reference geometry of the column, its "area of influence" (optional; falls back to `geom` if not provided)
- `b_int`: Lowest interval considered during the drafting of the column (if applicable)
- `t_int`: Highest interval considered during the drafting of the column (if applicable)
- `b_prop`: Position within the lowest interval (Default: 0)
- `t_prop`: Position within the highest interval (Default: 1)

### Column geometry format

The separation of the `geom` and `rgeom` fields handle cases where a column is assigned an "area of influence" beyond its
actual measured location. This is useful to denote that certain columns are representative of a study area. At least
one of these fields must be provided. These fields can also be provided as layers (with `col_id` and/or `project_id`
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
- `axis_type` : Default axis type; defaults to `age` for chronostratigraphic columns; filled from defaults if not given
- `fill_values`: Default fill value. Whether to fill unit attribute values (strat_name, lithology, environment,
  and related fields) from lower units. Boolean, defaults to `f` .

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

The **References** sheet contains reference information for citations used in the project. Each row represents a single reference, which should
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
for lithostratigraphic columns, but can also apply to chronostratigraphic columns.

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



