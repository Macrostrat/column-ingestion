"""Command line: `python -m column_template SPEC.yaml [-o OUTPUT.xlsx]`."""

import argparse

from .builder import build_template


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="column-template",
        description="Build the column ingestion Excel template from its YAML description.",
    )
    parser.add_argument("spec", help="Template description (.yaml)")
    parser.add_argument(
        "-o",
        "--output",
        help="Workbook to write (default: a -new copy beside the published template)",
    )
    args = parser.parse_args(argv)
    print(f"Wrote {build_template(args.spec, args.output)}")


if __name__ == "__main__":
    main()
