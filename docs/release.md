# Release

## Validation

Run from the repository root:

```bash
python3 -m pip install --upgrade pip
python3 -m pip install pytest pytest-asyncio ruff voluptuous aiohttp PyYAML Jinja2 'numpy>=1.26.0' Pillow
python3 -m compileall custom_components/diva tests/custom_components/diva
ruff check custom_components/diva tests/custom_components/diva
pytest -q tests/custom_components/diva
npm ci
npm run check
npm run build
```

## Release assets

GitHub releases publish only:

- `diva-hacs.zip`
- `diva-editor-panel.js`

`package.json` and `package-lock.json` are CI/frontend tooling files and are not included in the HACS zip.

## GitHub workflows

- `build.yml`
- `validate.yaml`
- `release-please.yml`
- `release.yml`
- `pages.yml`
