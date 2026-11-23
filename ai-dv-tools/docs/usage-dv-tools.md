# dv-tools 使用说明（Tool 01 + 06）

## 路径

- 代码仓库（本地 store，不入 git）：`/cursor/stores/self/dv-tools/`
- 规格说明：`docs/tools/01-regression-log-triage.md`、`docs/tools/06-waveform-less-debug-helper.md`

## 安装

```bash
cd /cursor/stores/self/dv-tools
pip install -e ".[dev]"
```

Python 3.11+。依赖：`typer`、`pyyaml`；可选 `datasketch`（MinHash，v1 默认精确哈希聚类）。

## Tool 01：回归日志分拣 `dv-triage`

扫描目录下全部 `*.log` 与 `*.log.gz`（含子目录），抽取 UVM 严重级、**Synopsys VCS** 原生消息（`Error-[...]` / `Warning-[...]`、`Error:`、断言 `offending`）、SVA、超时等事件，归一化指纹后聚类。

**默认仿真器为 VCS**（`--simulator vcs`）。旧版仅 UVM/通用行可用 `--simulator generic`。

```bash
dv-triage scan <日志目录> --out report.json
dv-triage scan <日志目录> --out report.json --markdown triage_report.md
dv-triage scan <日志目录> --out report.json --redact <层级前缀>
dv-triage scan <日志目录> --out report.json --baseline signatures.json
dv-triage scan <日志目录> --out report.json --include-warnings
dv-triage scan <日志目录> --out report.json --simulator generic
```

VCS 日志示例（会被识别为 `vcs_error` / `sva`）：

```
Error-[TCHK_TSETUP] tb.clk (Setup time check failed)
*** Error: Assertion tb.a failed at time 5000 ns
```

`Warning-[...]` 与 `UVM_WARNING` 默认不进入分拣；加 `--include-warnings` 可单独聚类（优先级较低）。

输出：

- `report.json`：簇 ID、标签、计数、测试名、owner 标签、`exemplar_snippet`
- 可选 Markdown 简报（含 Slack 摘要段）

示例数据：

```bash
dv-triage scan dv_triage/fixtures/sample_logs --out /tmp/report.json --simulator generic
dv-triage scan dv_triage/fixtures/sample_logs_vcs --out /tmp/report_vcs.json
```

## Tool 06：无波形调试清单 `dv-debug`

根据单日志或 Triage 簇摘录，匹配 `dv_debug/rules/default.yaml`（默认并上 VCS 规则 `vcs.yaml`）中的规则，生成 `debug_plan.md`（假设、非波形检查项、何时必须看波形）。

```bash
dv-debug plan --log <sim.log> --out debug_plan.md
dv-debug plan --from-triage report.json --cluster C1 --out debug_plan.md
```

`--llm` 在 v1 未配置，会报错提示。

## 推荐工作流

1. 夜间回归结束后对日志目录运行 `dv-triage scan`。
2. 从 JSON/Markdown 中按 `count` 或 delta 新簇选 `C*`。
3. 对该簇运行 `dv-debug plan --from-triage ... --cluster C*`。
4. 按清单做 config/verbosity/plusarg 检查；必要时再开波形。

## 测试

```bash
cd /cursor/stores/self/dv-tools
pytest -q
```