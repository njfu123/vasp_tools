"""Cluster failures by normalized signature."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

from dv_triage.normalizer import FailureRecord, owner_tag_from_signature, redact_hierarchy


def signature_hash(normalized: str) -> str:
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


@dataclass
class Cluster:
    cluster_id: str
    label: str
    count: int
    test_names: list[str] = field(default_factory=list)
    owner_tag: str = "other"
    signature_hash: str = ""
    exemplar_snippet: str = ""
    member_sources: list[str] = field(default_factory=list)


def cluster_records(
    records: list[FailureRecord],
    redact_prefix: str | None = None,
    max_clusters: int = 50,
) -> list[Cluster]:
    buckets: dict[str, list[FailureRecord]] = {}
    for rec in records:
        norm = redact_hierarchy(rec.normalized, redact_prefix)
        key = signature_hash(norm)
        buckets.setdefault(key, []).append(rec)

    clusters: list[Cluster] = []
    for idx, (sig_hash, members) in enumerate(
        sorted(buckets.items(), key=lambda kv: -len(kv[1]))
    ):
        if idx >= max_clusters:
            break
        cid = f"C{idx + 1}"
        exemplar = members[0]
        snippet = redact_hierarchy(exemplar.raw_excerpt, redact_prefix)
        lines = snippet.strip().splitlines()
        if len(lines) > 20:
            snippet = "\n".join(lines[:20])
        label = _cluster_label(exemplar, members)
        tests = sorted({m.source_file.split("@")[0] for m in members})
        tag = owner_tag_from_signature(exemplar.normalized, exemplar.kind)
        clusters.append(
            Cluster(
                cluster_id=cid,
                label=label,
                count=len(members),
                test_names=tests,
                owner_tag=tag,
                signature_hash=sig_hash,
                exemplar_snippet=snippet,
                member_sources=[m.source_file for m in members],
            )
        )
    return clusters


def _cluster_label(exemplar: FailureRecord, members: list[FailureRecord]) -> str:
    first_line = ""
    for ln in exemplar.raw_excerpt.splitlines():
        if ln.strip():
            first_line = ln.strip()[:120]
            break
    if len(first_line) > 80:
        first_line = first_line[:77] + "..."
    return first_line or f"{exemplar.kind} ({len(members)} hits)"


def delta_vs_baseline(
    clusters: list[Cluster], baseline_sigs: set[str]
) -> dict[str, list[str]]:
    current = {c.signature_hash for c in clusters}
    new_hashes = current - baseline_sigs
    gone = baseline_sigs - current
    new_ids = [c.cluster_id for c in clusters if c.signature_hash in new_hashes]
    return {
        "new_cluster_ids": new_ids,
        "new_signature_count": [str(len(new_hashes))],
        "gone_signature_count": [str(len(gone))],
    }