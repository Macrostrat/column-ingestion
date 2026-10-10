"""Build the Macrostrat column ingestion Excel templates from a YAML description."""

from .builder import (
    TemplateBuilder,
    build_template,
    build_templates,
    draft_path,
    included,
    load_spec,
    promote_templates,
    published_path,
    template_names,
)

__all__ = [
    "TemplateBuilder",
    "build_template",
    "build_templates",
    "draft_path",
    "included",
    "load_spec",
    "promote_templates",
    "published_path",
    "template_names",
]
