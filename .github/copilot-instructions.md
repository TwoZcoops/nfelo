# GitHub Copilot Instructions for nfelo

Purpose
- Give AI coding agents immediate context to work productively on the nfelo repository.
- Focus: how the data pipeline, model, and output flow together, where to run the code, and project-specific conventions.

Quick start (run locally) ✅
- Create environment (Linux):
  - conda env create -f environment.yml
  - conda activate nfelo
  - (Optional) faster: conda install -n base -c conda-forge mamba; mamba env create -f environment.yml
- Run the main update pipeline from the repo root:
  - python -c "from nfelo.scripts import update_nfelo; update_nfelo()"
  - Or run helper scripts like: python scripts/extract_week20_payload.py
- Check outputs:
  - Intermediate: `nfelo/Data/Intermediate Data/current_file.csv`, `market_data.csv`
  - Model output: `nfelo/Data/Intermediate Data/current_file_w_nfelo.csv`
  - Public payloads: `output_data/*.csv`, `output_data/*.json`

Architecture & key components 🔧
- Data ingestion: `nfelo/Data/DataLoader.py`
  - Uses `nfelodcm` to pull upstream datasets and writes intermediate CSVs.
  - Produces `current_file` (merged games + market + dvoa + wepa + qbs + hfa, etc.)
- Core model: `nfelo/Model/Nfelo.py`
  - `Nfelo` encapsulates ELO logic: `project_game`, `process_game`, `apply_nfelo`, `run`.
  - Config-driven: uses `config.json` under `models.nfelo.nfelo_config` for hyperparameters.
- Formatting & outputs: `nfelo/Formatting/NfeloFormatter.py`
  - Creates final user-facing CSVs and site payloads.
- Validation & grading: `nfelo/Performance/NfeloGrader.py` and `NfeloGraderModel.py`:
  - Computes scoring metrics and sanity checks used in output pipelines.
- Utilities: `nfelo/Utilities/*`
  - Small helper functions (market regression, spread translation, clv, etc.).
- Entry point script: `nfelo/scripts.py::update_nfelo()`
  - Loads config, runs DataLoader -> Nfelo -> Formatter -> Grader and writes outputs.

Data flow (high level) →
- nfelodcm (live data pulls) → DataLoader.format_* → DataLoader.gen_current_file → `current_file` → Nfelo.run() → `current_file_w_nfelo.csv` → Formatter → `output_data/` files

Project conventions and patterns 🧭
- Column naming: consistent `home_` / `away_` prefixes (e.g., `home_line_open`, `home_margin`, `home_nfelo_elo`). Follow these when adding merges/columns.
- Team codes: 3-letter uppercase (see `config.json: models.nfelo.teams`).
- Config-first design: model behavior is driven by `config.json`. Prefer changing model behavior via config updates or `Nfelo.update_config()` for experiments rather than hardcoding values.
- No dedicated test suite or CI detected: local validation is done by running the pipeline on real/intermediate CSVs.
- Logging: functions print helpful messages and save intermediate CSVs — use these files to debug data issues.

Developer workflows & debugging tips 💡
- Fast iterative runs: work with existing CSVs in `nfelo/Data/Formatted Data/` and `nfelo/Data/Intermediate Data/` to avoid network pulls.
- Reproducible experiments: change `models.nfelo.nfelo_config` values in `config.json` or call `update_config` on a `Nfelo` instance.
- To debug merges or missing columns: inspect `market_data.csv` and `current_file.csv` in Intermediate Data.
- To reproduce week-specific payloads: run `scripts/extract_week20_payload.py` from repo root (it expects `output_data/*.csv` and the intermediate files).
- Avoid running the full pipeline in quick PRs; run a targeted subset (e.g., generate `current_file` then call `Nfelo.project_week` manually).

PR & instruction guidance for AI agents 🤖
- Make minimal, well-scoped changes and run `python -c "from nfelo.scripts import update_nfelo; update_nfelo()"` to validate effects.
- When changing numeric model parameters, include a short script demonstrating the change via `Nfelo.update_config()` and output the new `current_file_w_nfelo.csv` for review.
- If adding or renaming columns, update the places that select columns explicitly (e.g., `scripts/extract_week20_payload.py`) and ensure helper scripts tolerate missing columns (pattern already used in that script).
- Add a small reproducible example (a short script or notebook that uses sample CSVs) when suggesting algorithmic changes.

Files to inspect for context (start here):
- `nfelo/Data/DataLoader.py` (data merge rules)
- `nfelo/Model/Nfelo.py` (core model logic)
- `nfelo/Formatting/NfeloFormatter.py` (final payload formatting)
- `nfelo/Performance/NfeloGrader.py` (scoring)
- `config.json` (model hyperparameters & data paths)
- `requirements.txt` / `environment.yml` (install/runtime)

Notes & limitations ⚠️
- No automated tests or CI were found — add small test fixtures (CSV snapshots + smoke tests) before larger refactors.
- Network pulls are performed via `nfelodcm`; for reproducible test runs prefer using saved CSVs under `nfelo/Data/Formatted Data/`.

Questions for you
- Do you want this to emphasize any specific agent behaviors (e.g., auto-create tests, avoid touching live data, or add notebooks for experiments)?

---
If you'd like, I can open a PR with this file added and iterate on phrasing or more specific examples (e.g., exact config keys to change for reversion or k).