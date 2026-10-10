# Column ingestion quickstart

## Start with the [Simple template](https://github.com/Macrostrat/column-ingestion/raw/main/Excel%20Templates/column-ingestion-template-simple.xlsx)

This guide walks through the simplest case: a measured section logged by height. Download it and fill it in as you read. The **[expanded template](https://github.com/Macrostrat/column-ingestion/raw/main/Excel%20Templates/column-ingestion-template-expanded.xlsx)** offers every field of the format; it has the same tabs and is read the same way on upload to Macrostrat

## Concepts

**Measured and composite columns.** A *measured* column (`col_type: measured`) places units by physical position, as in a measured section or a core. A *composite* column (`col_type: composite`) is a chronostratigraphic chart, which places units by age alone. This guide deals with measured columns; composite columns are described in the [full specification](./Full%20specification.md).

**Height and depth.** A measured column's positions run along one axis: *height*, measured up from the base of an outcrop section, or *depth*, measured down from the top of a core or borehole. Composite columns have no such axis. This guide uses height.

**Surfaces and units.** Each row of the `units` sheet describes two things. Its position marks a *surface*, the base of a unit, and ages are pinned to surfaces at tie points. The rest of the row gives the *attributes* of the unit above that surface, up to the next one: its names, lithology and facies.

**Extensibility.**

- Any format that includes the minimum columns is valid, and you can add detail as needed: the simple template has the essential fields, the expanded template adds more, and the [full specification](./Full%20specification.md) describes every option.
- Unrecognized values (e.g., detailed lithologies not in our dictionaries) are skipped
- The ingester skips columns it doesn't know and ignores extra sheets, so you can add _whatever extra columns or sheets you want_. For example, the [Zebra River Group measured sections](https://github.com/Macrostrat/column-ingestion/raw/main/Examples/Zebra-River-Group-Measured-sections-full.xlsx) carry chemostratigraphic (carbon isotope) measurements, samples, notes and sequence-stratigraphic surfaces on extra sheets, positioned within the same columns.

## Workbook sheets

- **Metadata**: project information
- **Columns**: location and general information: _multiple columns per workbook are allowed_
- **Units**: The core sheet: position, unit, surface information, and age model information
- **Refs**: where the columns came from

...and `facies`, `images`, and other height-keyed samples you might add.

## Filling the workbook

One `.xlsx` workbook per project. The template's tabs are in the same order as the steps below, and each header has a note you can see by hovering over it. Each data tab is followed by an **"(example)" tab** showing what every field means, its format, and filled-in rows. Type your data on the plain tabs; the example tabs are ignored on upload. Header colours: 🟥 required · 🟧 required, one of a pair (`strat_name` / `unit_name`) · 🟨 recommended · 🟦 age tie point · ⬜ optional.

Fill the sheets in this order. **Bold** = required; the ingester rejects the workbook without it.

Rule of thumb: when in doubt, do the least complicated thing, and write your assumptions in `comments`.

Every sheet, field, and option is described in the [full specification](./Full%20specification.md). Interval and lithology names are listed in Macrostrat's lexicon: [intervals](https://dev.macrostrat.org/lex/intervals) and [lithologies](https://dev.macrostrat.org/lex/lithologies).

## 1. `metadata`: the project (two columns: key | value)

| Key | Notes |
|---|---|
| **`project_name`** (or `project_id`) | At least one is required. |
| `col_type` | `measured`, for a measured section. The template starts as `measured`. |
| `axis_type` | `height` (metres up from the base). |
| `position_unit` | `meters` |
| `comments` | How heights were obtained, e.g. "digitized from Fig. 11". |

The `fill_values` key is explained with the `units` sheet below.

## 2. `columns`: where each column is

One row per column. A column is one outcrop or core site.

| Field | Notes |
|---|---|
| **`col_id`** | Short ID, e.g. `MM1`. The units sheet uses it. |
| `col_name`, `name` | Name of the column |
| **Location** | Either **`lat` + `lng`** (decimal degrees, west is negative) **or** `geom`: a `POLYGON(...)` for an area, or a `LINESTRING(...)` for a measured traverse. `geom` does **not** accept a `POINT`. |
| `ref_ids` | One or more `ref_id`s from the `refs` sheet. |

## 3. `units`: core column information

A unit is any chunk you can describe, from a single bed up to a whole formation. Row order doesn't matter, because the ingester sorts by height.

### Height

| Field                                | Notes |
|--------------------------------------|---|
| **`col_id`**                         | Must match a row on the `columns` sheet. |
| **`position`** (synonym of `b_pos`) | Height of the unit's **base**. Each unit runs up to the next row's position, so end the column with an **empty closing row**: just `col_id` and the height of the top. |

**Step B: what the rock is**

| Field | Notes                                                                                                                                                                                                                                                                           |
|---|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **`strat_name`** or **`unit_name`** | **At least one per unit.** `strat_name` is a formal stratigraphic name, of any rank. `unit_name` is a locally defined name (e.g. "upper carbonate"). If `unit_name` is blank, `strat_name` becomes the unit's name.                                                             |
| `lithology` | e.g. `cross-stratified sandstone`. Attributes go before the rock name. Separate several lithologies with `;`. For a range ("grey to black shale"), list both end members. Names are listed at [dev.macrostrat.org/lex/lithologies](https://dev.macrostrat.org/lex/lithologies). |
| `facies` | Optional: a `facies_id` from the `facies` tab (below). A unit takes its facies' lithology and environment wherever it leaves its own blank.                                                                                                                                     |
| `comments` | Generalizations you made, gaps.                                                                                                                                                                                                                                                 |


- **Gaps:** where rock is missing (e.g., missing core), add a row named `gap` (as its `unit_name`). An empty row with a position terminates the column and is equivalent.
- **Covered intervals:** `covered` in the `unit_name` or `lithology` field, or a separate `covered` = `y/n` column.
- **Repeated values:** set `fill_values` to `y` on the `metadata` sheet to copy lithology, strat_name, etc. **up** into blank cells above, so enter a value at the base of the interval it applies to. Type `none` in a cell to stop it.

> **Tip:** the ingester parses `lithology` text into Macrostrat lithologies, attributes and proportions. Paste your wording into the **[lithology matcher](https://dev.macrostrat.org/lex/match/lithologies)** to see exactly what it recognises — and which words it can't match — before you submit.

> **How closely do I have to match Macrostrat's terms?** Not exactly: feel free to diverge a bit and describe your rocks in your own words. Words the ingester can't match are left out of the parsed lithology, with a warning, rather than stopping the upload, and they show us where Macrostrat's lexicon needs to grow. The same goes for environments. Interval names (`b_int`) are the exception: they must match exactly.

**Step C: ages (surfaces)**

You only fill these in at **tie points**. The ingester interpolates between them.

| Field | Notes                                                                                                                                                                                                |
|---|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `b_int` | Interval name at the unit's base. Must match a Macrostrat interval name exactly, e.g. `Terreneuvian`; look names up at [dev.macrostrat.org/lex/intervals](https://dev.macrostrat.org/lex/intervals). |
| `b_prop` | Where that base sits in the interval: 0 = base, 1 = top. No value is read as 0                                                                                                                       |
| `age_model_notes` | Any extra info                                                                                                                                                                                       |

- **Tie points:** you need at least **2 per column**, typically near/at both the base and top surfaces.
- **Correlations:** give correlated horizons (e.g. a datum bed) the **same `b_int` and `b_prop` in every column**. If a correlation falls inside a unit, split the unit at that height.
- **Notes:** write every age assumption in `age_model_notes`.

**Optional: the `facies` tab**

Totally optional. A facies is a named list of lithologies and environments, with a description: for example `F1` = `desiccation cracks, laminated, fine sandstone (10%); lime mudstone`, `peritidal`. A unit can give a facies by its `facies_id` in its `facies` field. Wherever the unit leaves its own `lithology` or `environment` blank, it takes the facies'; its own cells always win.

## 4. `refs`: where the data came from

One row per source.

| Field | Notes |
|---|---|
| **`ref_id`** | Your own short ID, e.g. `Hogan_2011`. Must be unique. |
| **`authors`** | |
| **`title`** | |
| **`date`** | Publication year as a number (`2011`). |
| `publication`, `doi`, `url` | Fill in if known. |

## 5. Check before submitting

The template's README tab has the same checklist, with a box to tick for each item.

**`metadata`**

- [ ] `project_name` (or `project_id`) is filled in.
- [ ] `col_type` and `axis_type` match the data (`measured` and `height` for a measured section).

**`columns`**

- [ ] Every column has a location (`lat`/`lng`, a polygon or a traverse line).
- [ ] Every column lists its sources in `ref_ids`.

**`units`**

- [ ] Every `col_id` exists on `columns`.
- [ ] Every column ends with an empty closing row (only `col_id` and `position`).
- [ ] Every column has at least 2 age tie points.
- [ ] Every unit has a `strat_name` or a `unit_name` (the template turns both cells red when neither is filled).
- [ ] Every interval name is spelled as in [Macrostrat's interval list](https://dev.macrostrat.org/lex/intervals).
- [ ] Spot-check your `lithology` wording in the [lithology matcher](https://dev.macrostrat.org/lex/match/lithologies) — it shows the lithologies, attributes and proportions the ingester will read, and flags words it doesn't recognise.
- [ ] Covered intervals are units named `covered`, and missing rock is a row named `gap`.

**`refs`**

- [ ] Every `ref_id` cited on `columns` is here, with `authors`, `title` and a year. A reference without a year is left out, with a warning.

**`images`**

- [ ] If you worked from a figure, it is pasted on the `images` tab, and the metadata `comments` say how the heights were measured.

**Upload**

- [ ] Upload with **dry run** checked first. It runs the full ingest and then undoes it, so it reports errors without saving anything. Read its warnings too: an unknown interval, lithology or environment, or an incomplete reference, is left out rather than stopping the upload.

Worked example: [`hogan-2011-marble-mountains.xlsx`](https://github.com/Macrostrat/column-ingestion/raw/main/Examples/hogan-2011-marble-mountains.xlsx) (9 measured sections from Hogan et al. 2011, Fig. 11).

Common questions are answered in the [FAQ](./Column%20ingestion%20FAQ.md).
