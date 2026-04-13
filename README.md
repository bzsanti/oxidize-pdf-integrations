# oxidize-pdf Integrations

Platform integrations for [oxidize-pdf](https://pypi.org/project/oxidize-pdf/), a high-performance PDF library powered by Rust.

## Claude Code Plugin

A plugin that gives Claude full PDF manipulation capabilities: read, create, analyze, manipulate, secure, and transform PDF documents.

### Install

Add the marketplace and install:

```shell
/plugin marketplace add bzsanti/oxidize-pdf-integrations
/plugin install oxidize-pdf@oxidize-pdf
```

### What's included

- **6 skills**: `/oxidize-pdf:read-pdf`, `/oxidize-pdf:extract-text`, `/oxidize-pdf:create-pdf`, `/oxidize-pdf:analyze-pdf`, `/oxidize-pdf:secure-pdf`, `/oxidize-pdf:manipulate-pdf`
- **1 agent**: `oxidize-pdf:pdf-specialist` — orchestrates all PDF tools for complex workflows
- **MCP server**: 12 tools, 6 resources for complete PDF manipulation

### Requirements

- Python 3.10+
- `oxidize-pdf` is auto-installed if not found in your environment

## Other Integrations

Future integrations (VS Code, JetBrains, Cursor) will live in separate subdirectories.

## License

MIT
