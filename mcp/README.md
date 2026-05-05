# MCP Server Manifest

This directory holds the canonical `server.json` manifest for the oxidize-pdf MCP server registered at the [Model Context Protocol Registry](https://registry.modelcontextprotocol.io) under `io.github.bzsanti/oxidize-pdf-mcp`.

The server itself ships as part of the [`oxidize-pdf`](https://pypi.org/project/oxidize-pdf/) PyPI package (entry point `oxidize-mcp`); this directory only owns the registry manifest.

## How to publish a new version

1. Publish the corresponding `oxidize-pdf` PyPI release first (handled by `oxidize-python/.github/workflows/release.yml`).
2. From the GitHub Actions UI of `oxidize-pdf-integrations` (or via `gh` CLI), trigger the **Publish MCP Server** workflow:

   ```bash
   gh workflow run publish-mcp.yml -f version=0.5.0
   ```

The workflow patches the `version` field in this `server.json` for both the server and the package descriptor, validates the manifest against the registry schema, then publishes via `mcp-publisher` authenticated with GitHub OIDC (no secrets required).

## Authentication model

`mcp-publisher login github-oidc` consumes the OIDC token GitHub Actions provides automatically when `id-token: write` is granted to the job. The MCP Registry validates the token against the `bzsanti` GitHub identity, which owns the `io.github.bzsanti/*` namespace.

No PAT, no client secret, no manual token rotation.
