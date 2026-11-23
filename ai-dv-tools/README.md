# ai-dv-tools

DV regression log triage (`dv-triage`) and VCS-oriented debug helper (`dv-debug`), plus Project documentation.

## Get the bundle (Windows)

**Option A — git clone** (recommended; installs repo under `D:\work\tools\vasp_tools`):

```powershell
git clone https://github.com/njfu123/vasp_tools.git -b ai-dv-tools-export --single-branch D:\work\tools\vasp_tools
```

Then copy or install from `D:\work\tools\vasp_tools\ai-dv-tools` to `D:\work\tools` (see script below).

**Option B — browser ZIP**

1. Download: https://github.com/njfu123/vasp_tools/archive/refs/heads/ai-dv-tools-export.zip
2. Unzip and move the `ai-dv-tools` folder to `D:\work\tools\ai-dv-tools` (or run the install script from inside that folder).

## Install to `D:\work\tools`

From PowerShell, in the folder that contains this `README.md`:

```powershell
.\install-to-D-work-tools.ps1
```

Default target is `D:\work\tools` with `dv-tools\` and `docs\` as siblings (same layout as the Cursor Project bundle).

## Python setup

```powershell
cd D:\work\tools\dv-tools
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
dv-triage --help
dv-debug --help
```

See `docs/usage-dv-tools.md` for usage.

## Contents

| Path | Description |
|------|-------------|
| `dv-tools/` | Installable package (`pyproject.toml`); VCS presets/rules |
| `docs/` | Usage, roadmap, tool specs |