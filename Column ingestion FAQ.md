---
title: Column ingestion FAQ
---

Common questions about preparing a column spreadsheet for Macrostrat. For the
step-by-step guide, start with the [quickstart guide](./Column%20ingestion%20quickstart.md); every sheet and field
is described in the [full specification](./Full%20specification.md).

## Getting started

> [!question] Where do I get the template?

Download the
[guided template](https://github.com/Macrostrat/column-ingestion/raw/main/Excel%20Templates/column-ingestion-template.xlsx).
Its tabs follow the steps of the [quickstart guide](./Column%20ingestion%20quickstart.md), its headers are
coloured by whether a field is required, and each data tab is followed by an
"(example)" tab showing what every field means, its format, and filled-in rows. A
[worked example](https://github.com/Macrostrat/column-ingestion/raw/main/Examples/hogan-2011-marble-mountains.xlsx)
(nine measured sections digitized from a published figure) shows a complete workbook.

> [!question] What is the difference between a column, a section and a unit?

A **column** is one outcrop or core site. A **section** is part of a column with one
continuous age model; you only need more than one where the age model breaks, for
example across a fault. A **unit** is one row of the `units` sheet: any interval of
rock you can describe as a single chunk, from one bed to a whole formation.

> [!question] Should I choose "section" or "column" for `col_type`?

Use `section` for a measured section or core, where units are placed by measured
height. Use `column` for a composite or chronostratigraphic column, where units are
placed by age. Most field-measured data are sections.

> [!question] Can I put several columns in one workbook?

Yes. Give each a row on the `columns` sheet with its own `col_id`, and tag each unit
with the `col_id` of the column it belongs to.

## Units and positions

> [!question] Do I need to enter both `b_pos` and `t_pos` for every unit?

No. Every unit needs a `b_pos`, the height of its base. Only the topmost unit of each
column, and any unit below a gap, needs a `t_pos`; every other unit's top is taken from
the base of the unit above it. Instead of a `t_pos` on the topmost unit, you can end the
column with an empty closing row: a row with only `col_id` and a `b_pos` giving the height
of the top of the column. It is not a unit, but a `b_int` and `b_prop` on it date the top. Row order doesn't matter, because units are sorted by height.

> [!question] How small or large should a unit be?

As small or large as makes sense for your data. A unit can be a single bed or a whole
formation, as long as it can be described as one chunk. When in doubt, choose the
simpler option and note any generalizations in `comments`.

> [!question] How do I record a gap or a covered interval?

A covered interval (rock that is there but not exposed) is a unit like any other: set
`covered` to `y`, and give your best inference of its lithology, such as `shale` for a
recessive interval. A gap (missing rock) is not a unit: give the unit below it its own
`t_pos`, so its top does not meet the base of the unit above, and say what it is in
`comments`. A gap does not need a new `section_id` unless the age model changes across it.

> [!question] Why are my units saved with the name "default"?

Each unit needs a `strat_name` (the formation or member), a `unit_name` (a local name
such as "upper carbonate"), or both. If `unit_name` is blank, the `strat_name` is used
as the unit's name; with neither, the unit is saved as "default". The template turns
both cells red when a row has neither.

## Lithology

> [!question] How do I write the lithology?

Descriptive words first, then the rock name: `cross-stratified sandstone`. Separate
several lithologies with `;`, and put lesser ones in `minor_lith`. For a range, list
both end members: "light grey to black shale" becomes `light grey, black shale`.
Attributes need a rock name to attach to; "flute casts" on its own is not a lithology.

> [!question] I described my facies on the `facies` sheet. Do I still need to fill in `lithology`?

Yes. The `facies` sheet is useful for your own bookkeeping, but it is not read on
upload yet, so a unit's lithology comes only from its own `lithology` and `minor_lith`
cells.

> [!question] Do I have to repeat the same value down a long column?

No. Set `fill_values` to `y` on the `metadata` sheet and blank cells take the value of
the nearest unit **below** them (lithology, `strat_name`, `unit_name`, environment,
facies and a few others). Enter a value at the base of the interval it applies to, and
type `none` in a cell to stop it filling further up. In a core logged by depth, values
fill downward instead, from the top of each interval.

## Ages

> [!question] How do I give my column ages if I only know roughly how old it is?

Enter ages only at **tie points**: a unit's `b_int` (a geologic interval, such as
`Terreneuvian`) and `b_prop` (where its base falls in that interval, from 0 at the
oldest end to 1 at the youngest). Each section needs at least two tie points at
different heights; ages in between are interpolated by height. Write your reasoning in
an `age_model_notes` column.

> [!question] What happens if I leave `b_prop` blank?

It is read as 0, the oldest end of the interval. If you know the interval but not the
position within it, an educated guess is better than a blank.

> [!question] How are ages assigned above my highest tie point, or below my lowest?

They are not extrapolated: units beyond the outermost tie points take the age of the
nearest one. Add a tie point near the top and base of a section if their ages matter.

> [!question] How do I correlate several columns?

Give the correlated horizon, such as a datum bed, the **same** `b_int` and `b_prop` in
every column. If a correlation falls inside a unit, split the unit at that height.

> [!question] Can I enter absolute (radiometric) ages?

Not yet: ages are entered as intervals and proportions. Record dated horizons in
`comments` or `age_model_notes`, and use them to choose your tie points.

> [!question] My interval name was not recognized.

Interval names must match Macrostrat's exactly. Pick them from the dropdown on the
`b_int` and `t_int` columns of the template.

## Locations and sources

> [!question] The paper does not give coordinates. What do I enter?

Estimate them from the paper's location map or satellite imagery, enter them as `lat`
and `lng` in decimal degrees (west is negative), and note how they were obtained and
how precise they are in the column's `comments`.

> [!question] Why was my `geom` rejected?

`geom` is only for columns that cover an area, and must be a `POLYGON` or
`MULTIPOLYGON` in well-known text. For a single location, use `lat` and `lng`
instead; a `POINT` in `geom` is rejected.

> [!question] I digitized a column from a figure. What should I include?

Paste the original figure on an extra tab of the workbook (extra tabs are ignored on
upload), and say in the `metadata` sheet's `comments` how heights were measured, for
example "digitized from Fig. 11a with WebPlotDigitizer". This lets others see what was
generalized.

## Uploading

> [!question] How do I check my spreadsheet without saving anything?

Upload it on the [new column page](/columns/new) ("Upload data") with **dry run**
ticked. A dry run performs the whole ingest and then undoes it, so it reports errors
without saving. Any signed-in user can run one; saving columns is limited to
administrators.

> [!question] Can I see my column before it is saved?

Yes. A successful dry run opens the parsed column in the column editor, unsaved. If
the workbook has several columns, each gets an "Open" button and an "Open in new tab"
button, so you can look at them side by side. Edits made there stay in the page until
you export them.
