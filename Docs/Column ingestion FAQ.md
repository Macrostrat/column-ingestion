---
title: Column ingestion FAQ
---

Common questions about preparing a column spreadsheet for Macrostrat. For the
step-by-step guide, start with the [quickstart guide](./Quickstart.md); every sheet and field
is described in the [full specification](./Full%20specification.md).

## Getting started

> [!question] Where do I get the template?

There are two. The
[simple template](https://github.com/Macrostrat/column-ingestion/raw/main/Excel%20Templates/column-ingestion-template-simple.xlsx)
is a measured column with one `position` per unit and only the essential fields, and is
the one the quickstart walks through; the
[expanded template](https://github.com/Macrostrat/column-ingestion/raw/main/Excel%20Templates/column-ingestion-template-expanded.xlsx)
has every field. Both are read the same way on upload. Their tabs follow the steps of
the [quickstart guide](./Quickstart.md), their headers are
coloured by whether a field is required, and each data tab is followed by an
"(example)" tab showing what every field means, its format, and filled-in rows. A
[worked example](https://github.com/Macrostrat/column-ingestion/raw/main/Examples/hogan-2011-marble-mountains.xlsx)
(nine measured sections digitized from a published figure) shows a complete workbook.

> [!question] What is the difference between a column, a section and a unit?

A **column** is one outcrop or core site. A **section** is part of a column with one
continuous age model; you only need more than one where the age model breaks, for
example across a fault. A **unit** is one row of the `units` sheet: any interval of
rock you can describe as a single chunk, from one bed to a whole formation.

> [!question] Should I choose "measured" or "composite" for `col_type`?

Use `measured` for a measured section or core, where units are placed by measured
height. Use `composite` for a composite or chronostratigraphic column, where units are
placed in age order. Most field-measured data are measured columns. The older values
`section` and `column` are still read the same way.

> [!question] Can I put several columns in one workbook?

Yes. Give each a row on the `columns` sheet with its own `col_id`, and tag each unit
with the `col_id` of the column it belongs to.

## Units and positions

> [!question] Do I need to enter both `b_pos` and `t_pos` for every unit?

No. Every unit needs one position, the height of its base: `position` in the simple
template, `b_pos` in the expanded one. Every unit's top is taken from the base of the unit
above it. The topmost unit has nothing above it, so end the column with an empty closing
row: a row with only `col_id` and a position giving the height of the top of the column.
It is not a unit, but a `b_int` and `b_prop` on it date the top. In the expanded template, a
`t_pos` on the topmost unit works instead, and is also how overlapping units are given. Row order doesn't matter, because units are sorted by height.

> [!question] How small or large should a unit be?

As small or large as makes sense for your data. A unit can be a single bed or a whole
formation, as long as it can be described as one chunk. When in doubt, choose the
simpler option and note any generalizations in `comments`.

> [!question] How do I record a gap or a covered interval?

A covered interval (rock that is there but not exposed) is a unit like any other. Name
it `covered`, as its `unit_name` or in place of its `lithology`; or, if you can infer the
lithology, such as `shale` for a recessive interval, write that and set `covered` to `y`
(expanded template).
A gap (missing rock) is not a unit: add a row named `gap` (as its `unit_name`) at the
base of the missing interval, and no unit is created between it and the next row. Say
what the gap is in `comments`. A gap does not need a new `section_id` unless the age
model changes across it.

> [!question] Why are my units saved with the name "default"?

Each unit needs a `strat_name` (the formation or member), a `unit_name` (a local name
such as "upper carbonate"), or both. If `unit_name` is blank, the `strat_name` is used
as the unit's name; with neither, the unit is saved as "default". The template turns
both cells red when a row has neither.

## Lithology

> [!question] How do I write the lithology?

Descriptive words first, then the rock name: `cross-stratified sandstone`. Separate
several lithologies with `;`, and put lesser ones in `minor_lith` (expanded template). For a range, list
both end members: "light grey to black shale" becomes `light grey, black shale`.
Attributes need a rock name to attach to; "flute casts" on its own is not a lithology.

> [!question] How closely do I have to follow Macrostrat's lithology and environment terms?

Feel free to diverge a bit. Describe your rocks the way you would in a paper, using
Macrostrat's [lithology](https://dev.macrostrat.org/lex/lithologies) names where they fit.
Words the ingester can't match are left out of the parsed lithology, with a warning, rather
than stopping the upload. They are also how Macrostrat's lexicon gets better over time: they
show us which terms people actually use and are missing. To see how your wording will be
read before you submit, paste it into the
[lithology matcher](https://dev.macrostrat.org/lex/match/lithologies).
Interval names are the exception: they must match a Macrostrat interval exactly.

> [!question] I described my facies on the `facies` sheet. Do I still need to fill in `lithology`?

No. A unit that names a facies in its `facies` field takes the facies' lithologies when
it has no `lithology` of its own, and the facies' environments when it has no
`environment`. A unit's own cells always win, so fill them in only where a bed differs
from its facies.

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

Interval names must match Macrostrat's exactly. Look them up in
[Macrostrat's interval list](https://dev.macrostrat.org/lex/intervals).

## Locations and sources

> [!question] The paper does not give coordinates. What do I enter?

Estimate them from the paper's location map or satellite imagery, enter them as `lat`
and `lng` in decimal degrees (west is negative), and note how they were obtained and
how precise they are in the column's `comments`.

> [!question] Why was my `geom` rejected?

`geom` is for columns that cover an area (a `POLYGON` or `MULTIPOLYGON`) or follow
a measured traverse (a `LINESTRING` or `MULTILINESTRING`), in well-known text. For a
single location, use `lat` and `lng` instead; a `POINT` in `geom` is rejected.

> [!question] I digitized a column from a figure. What should I include?

Paste the original figure on the template's `images` tab, and name it there with its
figure number and source (the tab is ignored on upload). Say in the `metadata` sheet's
`comments` how heights were measured, for
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
