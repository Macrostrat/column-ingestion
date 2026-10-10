"""Command line: `python -m column_template SPEC.yaml [-t NAME [-o OUTPUT.xlsx]] [--promote]`."""

import argparse

from .builder import build_template, build_templates, promote_templates


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="column-template",
        description="Build the column ingestion Excel templates from their YAML description.",
    )
    parser.add_argument("spec", help="Template description (.yaml)")
    parser.add_argument(
        "-t", "--template", help="Build only this template (default: all of them)"
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Workbook to write, with --template (default: a -new copy beside the published one)",
    )
    parser.add_argument(
        "--promote",
        action="store_true",
        help="Replace each published template with its -new copy instead of building",
    )
    args = parser.parse_args(argv)
    if args.promote:
        for path in promote_templates(args.spec):
            print(f"Replaced {path}")
        return
    if args.template is not None:
        written = [build_template(args.spec, args.output, args.template)]
    else:
        written = build_templates(args.spec)
    for path in written:
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
