# Data Migration - Final Round

## Task 2

Set up the build html pipeline for SphinX repository using GitHub action.

## Requirements

Write a GitHub action pipeline to build Doc as Code project as html format.

## Evaluation

- `[✔]` GitHub action pipeline set up

- `[✔]` Html file got generated successfully

## Experiment

1, Create file workflow `documentation.yaml` in `.github/workflows` with this content here.

```yaml
name: Docs
on: [push, pull_request, workflow_dispatch]
permissions:
  contents: write
jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v3
      - name: Install dependencies
        run: |
          pip install sphinx sphinx_rtd_theme sphinxcontrib-plantuml sphinx_needs
      - name: Sphinx build
        run: |
          sphinx-build docs _build
      - name: Deploy
        uses: peaceiris/actions-gh-pages@v3
        if: ${{ github.event_name == 'push' && github.ref == 'refs/heads/main' }}
        with:
          publish_branch: gh-pages
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: _build/
          force_orphan: true
```

2, Turn on the Github pages

- Go to the repository store source code. Go to `Settings` > `Pages`

- Select `Deploy from a branch` in `Build and Development`.

- Select `gh-pages` in `Branch` if it exists. Branch `gh-pages` needs time to create when running the `Github Actions` workflow.

## Explain workflows

File `documentation.yaml` includes the rule for `Github action`. It will listen for action as `push`, `pull-request` to work the job.

- First, install the necessary dependencies package. It includes `sphinx`, `sphix-needs`, `sphinxcontrib.plantuml` to build as settings rule in `docs/conf.py`. It define in `Install dependencies` step

- Next, build the html resources by command line `sphinx-build docs _build`. It means it will build the html resources from `docs` directory to the `_build` directory. It define in `Sphinx build` step

- Finally, after build the html resources successfully. Pushing all content in the `_build` directory to branch `gh-pages`. It define in `Deploy` step

Github pages automatically look up the `index.html` file in the branch `gh-pages`. In base code html will render to web page
