"""Build the column-ingestion Excel template from its YAML description.

The YAML holds the content (tabs, fields, notes, examples, dropdowns); this module
holds the layout and styling, so the two can change independently.
"""

from pathlib import Path

import yaml
from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

BOLD = Font(bold=True)
WRAP = Alignment(wrap_text=True, vertical="top")
CENTER = Alignment(horizontal="center")
_THIN = Side(style="thin", color="999999")
BOX = Border(left=_THIN, right=_THIN, top=_THIN, bottom=_THIN)

EXAMPLE_FILL = "F2F2F2"
MEANING_FILL = "FFFFFF"
FORMAT_FILL = "F7F7F7"
GUIDE_TEXT = "404040"
WARNING_TEXT = "C00000"
LABEL_TEXT = "7F7F7F"
# Header columns narrower than this are widened so the header text fits.
MIN_WIDTH = 12
# Paragraphs on the START HERE tab are given a taller row to fit wrapped text.
PARAGRAPH_HEIGHT = 32
# A step longer than this wraps onto a second line.
STEP_WRAP_LENGTH = 95


def _fill(color: str) -> PatternFill:
    return PatternFill("solid", fgColor=color)


def _note(text: str) -> Comment:
    comment = Comment(text, "Macrostrat")
    comment.width = 320
    comment.height = 150
    return comment


def load_spec(path) -> dict:
    """Read a template description from YAML."""
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


#: Appended to the published template's name for a freshly built copy.
DRAFT_SUFFIX = "-new"


def published_path(spec_path) -> Path:
    """The published template: the spec's `output`, next to the YAML file."""
    spec_path = Path(spec_path)
    return spec_path.parent / load_spec(spec_path)["output"]


def draft_path(spec_path) -> Path:
    """Where a new build goes by default, so the published template is never overwritten."""
    published = published_path(spec_path)
    return published.with_name(f"{published.stem}{DRAFT_SUFFIX}{published.suffix}")


def build_template(spec_path, output=None) -> Path:
    """Build the workbook described by `spec_path` and save it.

    Writes to `output`, or by default to a `-new` copy beside the published template
    (`draft_path`). Returns the path written.
    """
    spec_path = Path(spec_path)
    spec = load_spec(spec_path)
    workbook = TemplateBuilder(spec, spec_path.parent).build()
    out = Path(output) if output is not None else draft_path(spec_path)
    workbook.save(out)
    return out


class TemplateBuilder:
    """Turns a loaded template description into an openpyxl `Workbook`."""

    def __init__(self, spec: dict, base_dir: Path):
        self.spec = spec
        self.kinds = spec["kinds"]
        self.max_rows = spec["max_rows"]
        self.example_text = spec["example_tabs"]
        # List sheets are read first: dropdowns on earlier tabs need their length.
        self.lists = {
            sheet["name"]: _read_lines(base_dir / sheet["values_file"])
            for sheet in spec["sheets"]
            if sheet.get("layout") == "list"
        }
        self.wb = Workbook()

    def build(self) -> Workbook:
        self._start_here(self.spec["start_here"])
        for sheet in self.spec["sheets"]:
            layout = sheet.get("layout", "fields")
            if layout == "key_value":
                self._key_value_sheet(sheet)
            elif layout == "list":
                self._list_sheet(sheet)
            else:
                self._field_sheet(sheet)
        return self.wb

    # ------------------------------------------------------------ START HERE

    def _start_here(self, page: dict):
        ws = self.wb.active
        ws.title = page["name"]
        ws.sheet_properties.tabColor = page["tab_color"]
        for column, width in (("A", 6), ("B", 30), ("C", 95)):
            ws.column_dimensions[column].width = width

        ws.cell(1, 2, page["title"]).font = Font(bold=True, size=16)
        row = 2
        for block in page["blocks"]:
            row = self._start_block(ws, row, block)

    def _start_block(self, ws, row: int, block: dict) -> int:
        """Write one START HERE block at `row`; return the next free row."""
        if "heading" in block:
            row += 1
            ws.cell(row, 2, block["heading"]).font = Font(bold=True, size=12)
            return row + 1
        if "paragraph" in block:
            ws.cell(row, 2, block["paragraph"]).alignment = WRAP
            ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=3)
            ws.row_dimensions[row].height = PARAGRAPH_HEIGHT
            return row + 1
        if "legend" in block:
            for name in block["legend"]:
                kind = self.kinds[name]
                cell = ws.cell(row, 2, kind["label"])
                cell.fill = _fill(kind["color"])
                cell.font = BOLD
                cell.border = BOX
                ws.cell(row, 3, kind["description"])
                row += 1
            return row
        if "steps" in block:
            for number, sheet, text in block["steps"]:
                ws.cell(row, 1, str(number)).font = BOLD
                ws.cell(row, 2, sheet).font = BOLD
                ws.cell(row, 3, text).alignment = WRAP
                height = PARAGRAPH_HEIGHT if len(text) > STEP_WRAP_LENGTH else None
                ws.row_dimensions[row].height = height
                row += 1
            return row
        if "checklist" in block:
            for item in block["checklist"]:
                ws.cell(row, 1, "☐")
                ws.cell(row, 2, item)
                ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=3)
                row += 1
            return row
        raise ValueError(f"Unknown START HERE block: {block}")

    # ------------------------------------------------------------ field tabs

    def _header(self, ws, fields: list[dict], tab_color: str, first_column=1):
        ws.sheet_properties.tabColor = tab_color
        for i, field in enumerate(fields, first_column):
            cell = ws.cell(1, i, field["name"])
            cell.font = BOLD
            cell.fill = _fill(self.kinds[field["kind"]]["color"])
            cell.border = BOX
            cell.alignment = CENTER
            cell.comment = _note(f"{field['meaning']}\nFormat: {field['format']}")
            width = max(field["width"], MIN_WIDTH)
            ws.column_dimensions[cell.column_letter].width = width

    def _field_sheet(self, sheet: dict):
        fields = sheet["fields"]
        ws = self.wb.create_sheet(sheet["name"])
        self._header(ws, fields, sheet["tab_color"])
        ws.freeze_panes = "A2"

        for i, field in enumerate(fields, 1):
            if "validation" in field:
                self._validate(ws, get_column_letter(i), field["validation"])
        if "highlight_missing" in sheet:
            self._highlight_missing(ws, fields, sheet["highlight_missing"])
        if "example" in sheet:
            self._field_example(sheet["name"], fields, sheet["example"])

    def _validate(self, ws, column: str, rule: dict):
        kind = rule["type"]
        options = {}
        if kind == "list" and "sheet" in rule:
            last_row = len(self.lists[rule["sheet"]]) + 1
            formula1 = f"={rule['sheet']}!$A$2:$A${last_row}"
        elif kind == "list":
            formula1 = f"={rule['range']}"
        else:
            formula1 = str(rule["value"])
            options["operator"] = rule["operator"]
            if "max" in rule:
                options["formula2"] = str(rule["max"])
        # A non-strict rule warns about an unlisted value but still accepts it.
        error_style = "stop"
        if rule.get("strict") is False:
            error_style = "warning"
        validation = DataValidation(
            type=kind,
            formula1=formula1,
            allow_blank=True,
            showErrorMessage=True,
            errorStyle=error_style,
            prompt=rule["prompt"],
            showInputMessage=True,
            **options,
        )
        validation.add(f"{column}2:{column}{self.max_rows}")
        ws.add_data_validation(validation)

    def _highlight_missing(self, ws, fields: list[dict], rule: dict):
        letters = {f["name"]: get_column_letter(i) for i, f in enumerate(fields, 1)}
        targets = sorted(letters[name] for name in rule["fields"])
        trigger = letters[rule["when_filled"]]
        blanks = ",".join(f'${letter}2=""' for letter in targets)
        formula = f'AND(${trigger}2<>"",{blanks})'
        cells = f"{targets[0]}2:{targets[-1]}{self.max_rows}"
        ws.conditional_formatting.add(
            cells, FormulaRule(formula=[formula], fill=_fill(rule["color"]))
        )

    def _field_example(self, name: str, fields: list[dict], example: dict):
        text = self.example_text
        ws = self.wb.create_sheet(f"{name} (example)")
        ws.sheet_properties.tabColor = example["tab_color"]
        ws.column_dimensions["A"].width = 13
        ws.cell(1, 1, "").border = BOX
        self._header(ws, fields, example["tab_color"], first_column=2)

        guide_rows = ((text["meaning_label"], "meaning"), (text["format_label"], "format"))
        for row, (label, key) in enumerate(guide_rows, 2):
            label_cell = ws.cell(row, 1, label)
            label_cell.font = BOLD
            label_cell.alignment = WRAP
            is_meaning = key == "meaning"
            background = FORMAT_FILL
            if is_meaning:
                background = MEANING_FILL
            for i, field in enumerate(fields, 2):
                cell = ws.cell(row, i, field[key])
                cell.alignment = WRAP
                cell.border = BOX
                cell.font = Font(italic=is_meaning, size=9, color=GUIDE_TEXT)
                cell.fill = _fill(background)
        ws.row_dimensions[2].height = 95
        ws.row_dimensions[3].height = 30

        rows = example["rows"]
        for row, values in enumerate(rows, 4):
            ws.cell(row, 1, text["row_label"]).font = Font(bold=True, color=LABEL_TEXT)
            for i, field in enumerate(fields, 2):
                value = values.get(field["name"])
                cell = ws.cell(row, i, value)
                cell.fill = _fill(EXAMPLE_FILL)
                cell.border = BOX
                long_text = isinstance(value, str) and len(value) > 30
                cell.alignment = Alignment(vertical="top", wrap_text=long_text)
        footer = ws.cell(len(rows) + 5, 1, text["footer"])
        footer.font = Font(italic=True, color=WARNING_TEXT)
        ws.freeze_panes = "B4"

    # ------------------------------------------------------------ key/value tab

    def _key_value_sheet(self, sheet: dict):
        rows = sheet["rows"]
        ws = self.wb.create_sheet(sheet["name"])
        ws.sheet_properties.tabColor = sheet["tab_color"]
        for i, row in enumerate(rows, 1):
            key = ws.cell(i, 1, row["key"])
            key.font = BOLD
            key.comment = _note(f"{row['meaning']}\nFormat: {row['format']}")
            key.border = BOX
            value = ws.cell(i, 2, row.get("default"))
            value.fill = _fill(self.kinds[row["kind"]]["color"])
            value.border = BOX
        ws.column_dimensions["A"].width = 18
        ws.column_dimensions["B"].width = 60
        for i, row in enumerate(rows, 1):
            if "choices" in row:
                choices = ",".join(row["choices"])
                validation = DataValidation(type="list", formula1=f'"{choices}"')
                validation.add(f"B{i}")
                ws.add_data_validation(validation)
        if "example" in sheet:
            self._key_value_example(sheet["name"], rows, sheet["example"])

    def _key_value_example(self, name: str, rows: list[dict], example: dict):
        ws = self.wb.create_sheet(f"{name} (example)")
        ws.sheet_properties.tabColor = example["tab_color"]
        for j, (title, width) in enumerate(example["columns"], 1):
            cell = ws.cell(1, j, title)
            cell.font = BOLD
            cell.border = BOX
            ws.column_dimensions[cell.column_letter].width = width
        for i, row in enumerate(rows, 2):
            key = ws.cell(i, 1, row["key"])
            key.font = BOLD
            key.fill = _fill(self.kinds[row["kind"]]["color"])
            key.border = BOX
            for j, value in enumerate((row["example"], row["meaning"], row["format"]), 2):
                cell = ws.cell(i, j, value)
                cell.alignment = WRAP
                cell.border = BOX
                if j == 2:
                    cell.fill = _fill(EXAMPLE_FILL)
                else:
                    cell.font = Font(italic=(j == 3), size=9, color=GUIDE_TEXT)
        footer = ws.cell(len(rows) + 3, 1, example["footer"])
        footer.font = Font(italic=True, color=WARNING_TEXT)
        ws.freeze_panes = "A2"

    # ------------------------------------------------------------ list tab

    def _list_sheet(self, sheet: dict):
        ws = self.wb.create_sheet(sheet["name"])
        ws.sheet_properties.tabColor = sheet["tab_color"]
        ws["A1"] = sheet["header"]
        ws["A1"].font = BOLD
        ws.column_dimensions["A"].width = sheet["width"]
        for i, value in enumerate(self.lists[sheet["name"]], 2):
            ws.cell(i, 1, value)


def _read_lines(path: Path) -> list[str]:
    # Only line breaks are stripped: some interval names carry trailing spaces.
    with open(path, encoding="utf-8") as f:
        return [line.rstrip("\n") for line in f if line.rstrip("\n") != ""]
