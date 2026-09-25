"""Launcher dependency checks must reject a base-only installation."""
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ROOT / 'claude-code/bin/launch-mcp'


def test_base_only_is_not_ready(tmp_path):
    # Fake interpreter has the PDF library but cannot import the MCP server.
    python = tmp_path / 'python3'
    python.write_text('#!/bin/sh\ncase "$*" in\n  *oxidize_pdf.mcp.server*) exit 1;;\n  *"import oxidize_pdf"*) exit 0;;\n  *) exit 1;;\nesac\n')
    python.chmod(0o755)
    env = {**os.environ, 'PATH': f'{tmp_path}:/usr/bin:/bin', 'OXIDIZE_PLUGIN_DATA': '', 'CLAUDE_PLUGIN_DATA': ''}
    result = subprocess.run(['bash', str(LAUNCHER), 'check'], env=env, text=True, capture_output=True)
    assert result.returncode == 1
    assert 'oxidize-pdf[mcp]' in result.stdout


def test_install_and_upgrade_use_mcp_extra(tmp_path):
    log = tmp_path / 'pip.log'
    bindir = tmp_path / 'bin'
    bindir.mkdir()
    python = bindir / 'python3'
    python.write_text('#!/bin/sh\nexit 1\n')
    python.chmod(0o755)
    venv = tmp_path / 'plugin' / 'venv' / 'bin'
    venv.mkdir(parents=True)
    py = venv / 'python'
    py.write_text('#!/bin/sh\nexit 0\n')
    py.chmod(0o755)
    pip = venv / 'pip'
    pip.write_text(f'#!/bin/sh\nprintf "%s\\n" "$@" >> "{log}"\n')
    pip.chmod(0o755)
    env = {**os.environ, 'PATH': f'{bindir}:/usr/bin:/bin', 'OXIDIZE_PLUGIN_DATA': str(tmp_path / 'plugin'), 'OXIDIZE_SKIP_UPGRADE': '0'}
    result = subprocess.run(['bash', str(LAUNCHER), 'check'], env=env, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    assert 'oxidize-pdf[mcp]>=0.20,<0.21' in log.read_text().splitlines()
    log.write_text('')
    result = subprocess.run(['bash', str(LAUNCHER), 'check'], env=env, text=True, capture_output=True)
    assert result.returncode == 0
    assert log.read_text() == ''  # A fresh timestamp respects the upgrade interval.
    env['OXIDIZE_SKIP_UPGRADE'] = '1'
    result = subprocess.run(['bash', str(LAUNCHER), 'check'], env=env, text=True, capture_output=True)
    assert result.returncode == 0
    assert log.read_text() == ''


def test_registry_requests_mcp_extra():
    import json
    data = json.loads((ROOT / 'mcp/server.json').read_text())
    package = data['packages'][0]
    source = next((a['value'] for a in package.get('runtimeArguments', []) if a.get('name') == '--from'), None)
    assert source == f"oxidize-pdf[mcp]=={data['version']}"
    assert package['version'] == data['version']
    assert package['packageArguments'] == [{'type': 'positional', 'value': 'oxidize-mcp'}]


def test_serve_failure_uses_stderr(tmp_path):
    python = tmp_path / 'python3'
    python.write_text('#!/bin/sh\nexit 1\n')
    python.chmod(0o755)
    env = {**os.environ, 'PATH': f'{tmp_path}:/usr/bin:/bin', 'OXIDIZE_PLUGIN_DATA': '', 'CLAUDE_PLUGIN_DATA': ''}
    result = subprocess.run(['bash', str(LAUNCHER), 'serve'], env=env, text=True, capture_output=True)
    assert result.returncode == 1
    assert result.stdout == ''
    assert 'oxidize-pdf[mcp]' in result.stderr


def test_upgrade_repairs_fastmcp_package_split(tmp_path):
    """pip can remove shared fastmcp files while replacing v3 with v4/slim."""
    bindir = tmp_path / 'bin'
    bindir.mkdir()
    system_py = bindir / 'python3'
    system_py.write_text('#!/bin/sh\nexit 1\n')
    system_py.chmod(0o755)
    venv = tmp_path / 'plugin' / 'venv' / 'bin'
    venv.mkdir(parents=True)
    ready = tmp_path / 'repaired'
    py = venv / 'python'
    py.write_text(f'''#!/bin/sh
case "$*" in
  *oxidize_pdf.mcp.server*) test -f "{ready}";;
  *) echo 4.0.9;;
esac
''')
    py.chmod(0o755)
    pip = venv / 'pip'
    pip.write_text(f'''#!/bin/sh
case "$*" in
  *--force-reinstall*fastmcp-slim==4.0.9*) touch "{ready}";;
esac
exit 0
''')
    pip.chmod(0o755)
    env = {**os.environ, 'PATH': f'{bindir}:/usr/bin:/bin', 'OXIDIZE_PLUGIN_DATA': str(tmp_path / 'plugin')}
    result = subprocess.run(['bash', str(LAUNCHER), 'check'], env=env, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    assert ready.exists(), 'A successful pip exit is not proof that the server imports'
