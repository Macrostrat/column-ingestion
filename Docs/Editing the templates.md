# Editing the guided templates

The guided templates are generated from one human-readable description,
[`Excel Templates/column-ingestion-template.yaml`](https://github.com/Macrostrat/column-ingestion/blob/main/Excel%20Templates/column-ingestion-template.yaml): every tab, field,
header colour, hover note, dropdown and example row is defined there, and anything marked `only: [<template>]`
appears only in that template (`simple` or `expanded`). To change the templates, edit the YAML and build them with the
`column_template` Python package in this repository:

```bash
make template     # build a -new copy of each template from the YAML, then check the quickstart guide
make promote      # replace the published templates with the -new copies, then run the tests
make quickstart   # only check the quickstart guide
make test         # check the published Excel files and the quickstart guide all match the YAML
```

`make template` never touches the published templates in `Excel Templates/`: it writes a `-new` copy beside each
(e.g. `column-ingestion-template-expanded-new.xlsx`), so the original and the new version can be compared. The `-new` copies
are local review files and are ignored by git. Once they look right, `make promote` moves them over the published
templates, so no `-new` copies are left behind; commit those together with the YAML.

`make test` builds a fresh copy from the YAML and compares it with the published `.xlsx`. It fails after the YAML is
edited until the new version is promoted, as a reminder that the template people download is out of date (it also
catches the published `.xlsx` being edited by hand).

The first command you run creates a private Python environment in `.venv/` and installs the package into it, so
nothing is installed into your system Python (this also avoids the "externally-managed-environment" error from
Homebrew's Python). `make clean` deletes it; `make install` rebuilds it.

The environment is created with `python3` (3.10 or newer); pass `SYSTEM_PYTHON=...` to use another
(e.g. `make template SYSTEM_PYTHON=python3.12`).

## Keeping the quickstart in step

The [quickstart guide](./Quickstart.md) is written by hand, so it is checked rather than
regenerated. It walks through the simple template (`quickstart.template` in the YAML), so fields only in the
expanded template are left out of it. `make template`, `make quickstart` and `make test` fail if:

- a field of the simple template isn't named in the guide's section for its tab;
- the guide's tables list a field that no longer exists on that tab.

Mark a field `quickstart: false` in the YAML if the guide should leave it out.
