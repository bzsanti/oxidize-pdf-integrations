# MCP Server Manifest

This directory holds the canonical `server.json` manifest for the oxidize-pdf MCP server registered at the [Model Context Protocol Registry](https://registry.modelcontextprotocol.io) under `io.github.bzsanti/oxidize-pdf-mcp`.

The server itself ships as part of the [`oxidize-pdf`](https://pypi.org/project/oxidize-pdf/) PyPI package (entry point `oxidize-mcp`); this directory only owns the registry manifest.

## How to publish a new version

1. Publish the corresponding `oxidize-pdf` PyPI release first (handled by `oxidize-python/.github/workflows/release.yml`).
2. Update both `version` and `packages[0].version` in `mcp/server.json` and record the release in `CHANGELOG.md`. Merge those changes after the compatibility checks pass so the canonical manifest matches the release.
3. From the GitHub Actions UI of `oxidize-pdf-integrations` (or via `gh` CLI), trigger the **Publish MCP Server** workflow:

   ```bash
   gh workflow run publish-mcp.yml -R bzsanti/oxidize-pdf-integrations -f version=0.19.0
   ```

The workflow changes only its temporary checkout; it does not commit version updates back to this repository.

Changing `mcp/server.json` triggers the LangChain, LlamaIndex and Haystack test
matrices on Python 3.10–3.13. Each installs the exact bridge version declared in
the manifest, so the corresponding PyPI package must exist before CI can pass.

The workflow patches the `version` field in this `server.json` for both the server and the package descriptor, validates the manifest against the registry schema, then publishes via `mcp-publisher` authenticated with GitHub OIDC (no secrets required).

## Authentication model

`mcp-publisher login github-oidc` consumes the OIDC token GitHub Actions provides automatically when `id-token: write` is granted to the job. The MCP Registry validates the token against the `bzsanti` GitHub identity, which owns the `io.github.bzsanti/*` namespace.

No PAT, no client secret, no manual token rotation.
