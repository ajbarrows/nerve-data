# NERVE Lab Data Sets

See [the documentation](https://ajbarrows.github.io/nerve-data/) for details.

## Rendering the documentation

The Quarto site in `quarto/` runs its code through a Jupyter kernel named `nervedata`, which points to this project's uv-managed `.venv` (set in `quarto/_quarto.yml`). Run Quarto via `uv run` so it finds Jupyter in `.venv` rather than the system Python.

```bash
uv sync                                    # build/update .venv
# One-time (or after recreating .venv): register the kernel
uv run python -m ipykernel install --user --name nervedata --display-name nervedata

cd quarto
uv run quarto preview             # live preview
uv run quarto render              # build to quarto/_site/
uv run quarto publish gh-pages    # deploy to GitHub Pages
```
