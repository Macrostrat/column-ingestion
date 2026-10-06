# Build the guided Excel template from its YAML description.
#
#   make template    build Excel Templates/column-ingestion-template-new.xlsx from the YAML
#                    (the published template is left untouched), then check the quickstart guide
#   make promote     replace the published template with the -new copy, then run the tests
#   make quickstart  only check the quickstart guide against the YAML
#   make test        check that the promoted .xlsx matches the current YAML,
#                    and that the quickstart guide matches it
#   make install     (re)create the project's Python environment in .venv/
#   make clean       remove Python caches and the .venv/ environment
#
# Everything runs in a private environment in .venv/, created on first use, so nothing is
# installed into your system or Homebrew Python.

SYSTEM_PYTHON ?= python3
VENV := .venv
PYTHON := $(VENV)/bin/python
INSTALLED := $(VENV)/.installed
SPEC := Excel Templates/column-ingestion-template.yaml
PUBLISHED := Excel Templates/column-ingestion-template.xlsx
OUTPUT := Excel Templates/column-ingestion-template-new.xlsx

.PHONY: all install template promote quickstart test clean

all: template

# Recreated whenever pyproject.toml changes.
$(INSTALLED): pyproject.toml
	$(SYSTEM_PYTHON) -m venv $(VENV)
	$(PYTHON) -m pip install --quiet --upgrade pip
	$(PYTHON) -m pip install --quiet -e ".[test]"
	touch $(INSTALLED)

install:
	rm -f $(INSTALLED)
	$(MAKE) $(INSTALLED)

template: $(INSTALLED)
	$(PYTHON) -m column_template "$(SPEC)" -o "$(OUTPUT)"
	$(PYTHON) -m column_template.quickstart "$(SPEC)"

promote: $(INSTALLED)
	@test -f "$(OUTPUT)" || (echo "No new template to promote: run 'make template' first." && exit 1)
	cp "$(OUTPUT)" "$(PUBLISHED)"
	@echo "Replaced $(PUBLISHED) with the new build."
	$(MAKE) test

quickstart: $(INSTALLED)
	$(PYTHON) -m column_template.quickstart "$(SPEC)"

test: $(INSTALLED)
	$(PYTHON) -m pytest -q tests

clean:
	rm -rf $(VENV) .pytest_cache *.egg-info
	find . -name __pycache__ -type d -not -path "./.git/*" -prune -exec rm -rf {} +
