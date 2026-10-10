# Ingesting columns

Ingestion of this format is now available, as part of the **Macrostrat v2** effort:

- **Upload on the Macrostrat website** at `/columns/new` ("Upload data"). Any signed-in user can run a **dry run**,
  which performs the full ingest and then undoes it, reporting errors without saving anything; a successful dry run
  opens the parsed columns in the column editor. Saving columns to the database is limited to administrators.
- **Command line**, for maintainers: `macrostrat columns ingest <file> [--dry-run]`.

Not every field in this spec is used yet. In particular, the **Images** sheet, column-linked data
sheets, column- and project-level age defaults, and the alternate formats (GIS layers, BibTeX) are accepted in a
workbook but not yet read by the ingester; see the [full specification](./Full%20specification.md) for details.

Planned workflows include:

- Offline validation and visualization
- Creation of Geopackage-based relational datasets for offline use and editing (using a prototype
  `.mcol` Macrostrat column exchange format)

These tools
will allow progressive enhancement of an in-progress stratigraphic dataset and eventual
inclusion into the Macrostrat database for broader use.

This spec will be refined as it is used by the community. Potential improvements are described in the [**Future updates**](./Future%20updates.md) document.
