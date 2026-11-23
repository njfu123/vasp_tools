# dv-tools (Tools 01 + 06)

Monorepo for **regression log triage** (`dv-triage`) and **waveform-less debug plans** (`dv-debug`).

## Workflow

1. **Triage** a regression drop (directory of logs):

   ```bash
   pip install -e ".[dev]"
   dv-triage scan <log_dir> --out report.json --markdown triage_report.md
   # Default simulator: Synopsys VCS; use --simulator generic for UVM-only logs
   ```

2. Pick a cluster id from the report (e.g. `C1` with highest count or a new delta cluster).

3. **Debug plan** without opening waves first:

   ```bash
   dv-debug plan --from-triage report.json --cluster C1 --out debug_plan.md
   ```

   Or use a single log:

   ```bash
   dv-debug plan --log path/to/sim.log --out debug_plan.md
   ```

4. Work through **Non-wave checks** in `debug_plan.md`; open waves only if **Escalate to waves if** applies.

## Packages

| Package    | CLI        | Spec                                              |
|-----------|------------|---------------------------------------------------|
| `dv_triage` | `dv-triage` | `/cursor/stores/self/docs/tools/01-regression-log-triage.md` |
| `dv_debug`  | `dv-debug`  | `/cursor/stores/self/docs/tools/06-waveform-less-debug-helper.md` |

## Fixtures end-to-end

```bash
cd /cursor/stores/self/dv-tools
pip install -e ".[dev]"
dv-triage scan dv_triage/fixtures/sample_logs --out /tmp/report.json --markdown /tmp/triage.md
dv-debug plan --from-triage /tmp/report.json --cluster C1 --out /tmp/debug_plan.md
pytest -q
```

User guide (中文): `/cursor/stores/self/docs/usage-dv-tools.md`.