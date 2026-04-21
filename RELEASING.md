# Releasing Integrations

This repository hosts multiple integrations for `oxidize-pdf`, each with its own release cycle. This document defines how releases are versioned, tagged, built, and published so the process stays consistent as new integrations are added.

## Integration Layout

Each integration lives in its own top-level directory:

```
oxidize-pdf-integrations/
├── claude-code/        # Claude Code plugin (self-hosted marketplace)
├── llamaindex/         # LlamaIndex reader (PyPI: llama-index-readers-oxidize-pdf)
├── <future>/           # e.g. langchain/, haystack/
├── RELEASING.md        # this file
└── ...
```

Each sub-directory has its own manifest (`plugin.json`, `pyproject.toml`, ...) and publishes to whatever channel makes sense for that ecosystem. They do **not** share version numbers.

## Tag Convention

Tags are the single source of truth for releases. Every integration uses a **prefixed tag** so the release workflows know which sub-package to build.

| Integration | Tag pattern | Example | Channel |
|---|---|---|---|
| Claude Code plugin | `claude-code-v<X.Y.Z>` | `claude-code-v1.0.2` | Self-hosted marketplace (GitHub) |
| LlamaIndex reader | `llamaindex-v<X.Y.Z>` | `llamaindex-v0.1.0` | PyPI (`llama-index-readers-oxidize-pdf`) |
| Future integrations | `<slug>-v<X.Y.Z>` | `langchain-v0.1.0` | Ecosystem-specific |

### Grandfathered tags

The current `v1.0.0` and `v1.0.1` tags refer to the Claude Code plugin. They are left untouched for backward compatibility with the marketplace manifest. **Starting with the next plugin release, use `claude-code-v1.0.2`.** Do not create new unprefixed `vX.Y.Z` tags in this repo.

## Cross-Repo Dependency Pattern

Integrations depend on the `oxidize-pdf` PyPI package (published from the [`oxidize-python`](https://github.com/bzsanti/oxidize-python) repo). This is the standard way LlamaIndex / LangChain / etc. integrations declare upstream deps.

Example (`llamaindex/pyproject.toml`):

```toml
dependencies = [
    "llama-index-core>=0.13.0,<0.15",
    "oxidize-pdf>=0.4.2",
]
```

### Version coupling gotcha

When `oxidize-pdf` ships a **breaking** release (e.g. `0.x` → `1.0`, or an API removal inside `0.x`), every integration that depends on it must:

1. Test against the new version locally.
2. Update the `dependencies` pin in its `pyproject.toml` / manifest.
3. Cut a new patch or minor release of the integration.

This is deliberate — integrations pin a version range so users get a known-good combination, not a surprise upgrade. Keep an eye on this when we release new `oxidize-pdf` majors.

## PyPI Trusted Publisher Setup (one-time per integration)

Any integration that publishes a Python package (LlamaIndex, future LangChain, etc.) needs a PyPI trusted publisher configured once, before the first release. OIDC — no API tokens stored in GitHub secrets.

1. Go to https://pypi.org/manage/account/publishing/
2. Add a new **pending publisher** with:
   - **PyPI project name**: the exact package name (e.g. `llama-index-readers-oxidize-pdf`)
   - **Owner**: `bzsanti`
   - **Repository name**: `oxidize-pdf-integrations`
   - **Workflow name**: the file that builds this integration (e.g. `release-llamaindex.yml`)
   - **Environment name**: `pypi`
3. In GitHub → repository **Settings → Environments** → create `pypi` environment (can be shared across all sub-packages). Optionally add required reviewers for manual approval before each publish.

`oxidize-python` already has its own trusted publisher configured for the `oxidize-pdf` project; **it is not reused here** (different repo, different PyPI project).

## Release Workflow per Integration

Each integration gets its own GitHub Actions workflow under `.github/workflows/`, named `release-<slug>.yml`. The workflow triggers on tags matching that integration's prefix.

Minimum responsibilities:

- Trigger on `push: tags: ['<slug>-v*']`
- `cd` into the integration directory
- Build the artifact (`uv build`, `python -m build`, zip the plugin, ...)
- Publish to the target channel (PyPI trusted publisher, GitHub release, ...)
- Fail loudly on tag/manifest version mismatch

### Pre-flight checklist (before tagging any release)

1. Manifest version (`plugin.json` / `pyproject.toml`) matches the tag you are about to push.
2. `CHANGELOG.md` has a section for the new version.
3. Cross-repo deps pinned to released PyPI versions (not local paths, not git URLs).
4. Tests passing locally for the integration sub-package.
5. Trusted publisher configured on PyPI (first release only).

Only then: `git tag <slug>-v<X.Y.Z> && git push origin <slug>-v<X.Y.Z>`.

## Changelog

`CHANGELOG.md` at repo root uses section headers scoped per integration:

```markdown
## [claude-code-v1.0.1] - 2026-04-21
### Fixed
- ...

## [llamaindex-v0.1.0] - 2026-MM-DD
### Added
- Initial release of `llama-index-readers-oxidize-pdf`.
```

Keep the sections ordered by release date (newest first), regardless of integration.
