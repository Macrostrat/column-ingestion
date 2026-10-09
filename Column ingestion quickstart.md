# Building a column spreadsheet for Macrostrat ingestion

One `.xlsx` workbook per project. Start from **[`column-ingestion-template.xlsx`](https://github.com/Macrostrat/column-ingestion/raw/main/Excel%20Templates/column-ingestion-template.xlsx)**: its tabs are in the same order as the steps below, and each header has a note you can see by hovering over it. Each data tab is followed by an **"(example)" tab** showing what every field means, its format, and filled-in rows. Type your data on the plain tabs; the example tabs are ignored on upload. Header colours: 🟥 required · 🟧 required, one of a pair (`strat_name` / `unit_name`) · 🟨 recommended · 🟦 age tie point · ⬜ optional.

Fill the sheets in this order. **Bold** = required; the ingester rejects the workbook without it.

Rule of thumb: when in doubt, do the least complicated thing, and write your assumptions in `comments`.

This guide covers the essentials. Every sheet, field, and option is described in the [full specification](./Full%20specification.md).

## 1. `refs`: where the data came from

One row per source.

| Field | Notes |
|---|---|
| **`ref_id`** | Your own short ID, e.g. `Hogan_2011`. Must be unique. |
| **`authors`** | |
| **`title`** | |
| **`date`** | Publication year as a number (`2011`). |
| `publication`, `doi`, `url` | Fill in if known. |

## 2. `metadata`: the project (two columns: key | value)

| Key | Notes |
|---|---|
| **`project_name`** (or `project_id`) | At least one is required. |
| `col_type` | `section` (a measured section) or `column` (a composite). |
| `axis_type` | `height` (metres up from the base). |
| `position_unit` | `meters` |
| `fill_values` | `y` copies lithology, strat_name, etc. **up** into blank cells above, so enter a value at the base of the interval it applies to. Type `none` in a cell to stop it. |
| `comments` | How heights were obtained, e.g. "digitized from Fig. 11". |

## 3. `columns`: where each column is

One row per column. A column is one outcrop or core site.

| Field | Notes |
|---|---|
| **`col_id`** | Short ID, e.g. `MM1`. The units sheet uses it. |
| `col_name`, `col_group` | `col_group` groups related columns together. |
| **Location** | Either **`lat` + `lng`** (decimal degrees, west is negative) **or** `geom` as a `POLYGON(...)`. `geom` does **not** accept a `POINT`. |
| `ref_ids` | One or more `ref_id`s from the `refs` sheet. |

## 4. `units`: the rocks, one row per unit

A unit is any chunk you can describe, from a single bed up to a whole formation. Row order doesn't matter, because the ingester sorts by height.

**Step A: heights**

| Field | Notes |
|---|---|
| **`col_id`** | Must match a row on the `columns` sheet. |
| **`b_pos`** | Height of the unit's **base**. |
| **`t_pos`** | **Only on the topmost unit**, or on a unit below a gap. Every other top is taken from the base of the unit above. Instead of a `t_pos` on the topmost unit, you can end the column with an **empty closing row** above it: just `col_id` and a `b_pos` at the top of the column. |
| `section_id` | Leave blank if the column is one continuous section. Start a new ID only where the age model breaks, e.g. at a fault. A gap in the rock alone does not need a new section. |

**Step B: what the rock is**

| Field | Notes                                                                                                                                                                                                                                                           |
|---|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `lithology` | e.g. `cross-stratified sandstone`. Attributes go before the rock name. Separate several lithologies with `;`. For a range ("grey to black shale"), list both end members.                                                                                       |
| `minor_lith` | Subordinate lithologies, written the same way.                                                                                                                                                                                                                  |
| `covered` | `y` for a covered interval: present but not exposed. Inferred lithology (e.g. `shale` for a recessive interval) or blank/none is fine.                                                                                                                          |
| **`strat_name`** or **`unit_name`** | **At least one per unit.** `strat_name` is meant to be a formal name, of any rank. `unit_name` is a locally defined name (e.g. "upper carbonate"). If `unit_name` is blank, `strat_name` becomes the unit's name. |
| `facies` | Optional shortcut to rows on the `facies` sheet. **Note: the ingester does not read the `facies` sheet yet, so put the lithology on each unit as well.**                                                                                                        |
| `basal_surface` | e.g. `nonconformity`, `conformable`, `sharp`, `gradational`, `erosive`. Optional and experimental.                                                                                                                                                              |
| `comments` | Generalizations you made, gaps.                                                                                                                                                                                                                                 |

> **Tip:** the ingester parses `lithology` / `minor_lith` text into Macrostrat lithologies, attributes and proportions. Paste your wording into the **[lithology matcher](https://dev.macrostrat.org/lex/lith-match)** to see exactly what it recognises — and which words it can't match — before you submit.

**Step C: ages (surfaces)**

You only fill these in at **tie points**. The ingester interpolates between them.

| Field | Notes |
|---|---|
| `b_int` | Interval name at the unit's base. Must match a Macrostrat interval name exactly, e.g. `Terreneuvian`. |
| `b_prop` | Where that base sits in the interval: 0 = oldest end, 1 = youngest end. **Blank is read as 0**, so make an educated guess. |
| `t_int`, `t_prop` | Usually leave blank: they are copied from the unit above. Fill in only on the top unit if you know its age, or give the empty closing row a `b_int` and `b_prop` instead. |

- **Tie points:** you need at least **2 per column**, typically the base plus one horizon, with more only where the sedimentation rate changes. Ages are not extrapolated past the outermost tie points: units above the highest one (or below the lowest) get that tie point's age.
- **Correlations:** give correlated horizons (e.g. a datum bed) the **same `b_int` and `b_prop` in every column**. If a correlation falls inside a unit, split the unit at that height.
- **Notes:** write every age assumption in an `age_model_notes` column.
- **Gaps:** where rock is missing (e.g., missing core), enter a blank row with only a position to signify the top of the package, or give the unit below the gap its own `t_pos`.
- **Covered intervals:** Add a unit with `covered` = `y`.

## 5. Check before submitting

- [ ] Every `col_id` on `units` exists on `columns`.
- [ ] Every column has a location (`lat`/`lng` or a polygon).
- [ ] Every column has a top (a `t_pos` on its topmost unit, or an empty closing row with only a `b_pos`), plus at least 2 age tie points.
- [ ] Every unit has a `strat_name` or a `unit_name` (the template turns both cells red when neither is filled).
- [ ] Every interval name is spelled as in Macrostrat.
- [ ] Spot-check your `lithology` / `minor_lith` wording in the [lithology matcher](https://dev.macrostrat.org/lex/lith-match) — it shows the lithologies, attributes and proportions the ingester will read, and flags words it doesn't recognise.
- [ ] Every `ref_id` cited exists on `refs`, with `authors`, `title` and a year.
- [ ] If you worked from a figure, add a sheet with the original image and note how the heights were measured.
- [ ] Upload with **dry run** checked first. It runs the full ingest and then undoes it, so it reports errors without saving anything.

Worked example: [`hogan-2011-marble-mountains.xlsx`](https://github.com/Macrostrat/column-ingestion/raw/main/Examples/hogan-2011-marble-mountains.xlsx) (9 measured sections from Hogan et al. 2011, Fig. 11).
