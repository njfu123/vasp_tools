# dv_triage (Tool 01)

Regression log triage: parse `*.log` / `*.log.gz`, fingerprint failures, cluster by normalized signature.

## Install

From `dv-tools` root:

```bash
cd /cursor/stores/self/dv-tools
pip install -e ".[dev]"
```

## Usage

```bash
dv-triage scan ./my_logs --out report.json --markdown triage_report.md
dv-triage scan ./my_logs --out report.json --redact ../../customer_tb/
dv-triage scan ./my_logs --out report.json --baseline signatures.json
dv-triage export-signatures report.json --out signatures.json
```

## Example (fixtures)

```bash
dv-triage scan dv_triage/fixtures/sample_logs --out /tmp/report.json --markdown /tmp/triage_report.md
```

Example JSON cluster entry:

```json
{
  "cluster_id": "C1",
  "label": "UVM_ERROR ../../tb/uvm_test_top.env.sb [ADDR] mismatch ...",
  "count": 4,
  "owner_tag": "uvm",
  "test_names": ["uart_rand_001", "uart_rand_002"]
}
```

## Tests

```bash
pytest dv_triage/tests -q
```