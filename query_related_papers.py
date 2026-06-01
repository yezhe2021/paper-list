from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path
from typing import Any

import paper_finder as pf


DEFAULT_SINCE = dt.date(2026, 1, 1)
DEFAULT_OUTPUT = Path("reports") / "all_papers_since_2026.md"


def collect_related_papers(since: dt.date, max_results_per_source: int) -> tuple[list[str], list[dict[str, str]], list[str]]:
    config = pf.load_config()
    config["days_back"] = max(1, (dt.date.today() - since).days)
    config["max_results_per_source"] = max_results_per_source

    texts: dict[Path, str] = {}
    for path in pf.paper_paths(Path(config["papers_dir"])):
        try:
            texts[path] = pf.read_paper(path, config)
        except Exception:
            continue

    keywords = pf.extract_keywords(texts, config)
    items: list[dict[str, str]] = []
    errors: list[str] = []
    for name, search in pf.enabled_searches(config):
        try:
            source_limit = max(max_results_per_source, 5000) if name == "arxiv" else max_results_per_source
            items.extend(search(keywords, source_limit, since))
        except Exception as exc:
            errors.append(f"{name}: {exc}")

    items = [
        item
        for item in pf.dedupe_items(items)
        if pf.within_date_window(item, since) and pf.relevant_enough(item, keywords, config)
    ]
    return keywords, dedupe_by_title(pf.sort_items(items, keywords), keywords), errors


def normalize_title(value: str) -> str:
    value = pf.strip_html(value).lower()
    value = value.replace("kv-cache", "kv cache").replace("key-value", "key value")
    return " ".join(part for part in value.split() if part)


def dedupe_by_title(items: list[dict[str, str]], keywords: list[str]) -> list[dict[str, str]]:
    merged: dict[str, dict[str, str]] = {}
    source_rank = {"arXiv": 0, "OpenAlex": 1, "Semantic Scholar": 2, "Crossref": 3}
    for item in items:
        key = normalize_title(item.get("title", ""))
        if not key:
            continue
        existing = merged.get(key)
        if not existing:
            merged[key] = item.copy()
            continue

        sources = set(existing.get("source", "").split(" + ")) | {item.get("source", "")}
        existing["source"] = " + ".join(sorted(sources))
        if item.get("source") == "arXiv" or source_rank.get(item.get("source", ""), 9) < source_rank.get(existing.get("source", ""), 9):
            existing["url"] = item.get("url", existing.get("url", ""))
        if not existing.get("published") and item.get("published"):
            existing["published"] = item["published"]
        if int(item.get("rank_score", "0") or 0) > int(existing.get("rank_score", "0") or 0):
            for field in ["rank_score", "rank_priority", "rank_category", "fit_reason", "abstract"]:
                existing[field] = item.get(field, existing.get(field, ""))
        pf.rank_item(existing, keywords)
    return pf.sort_items(list(merged.values()), keywords)


def render_markdown(since: dt.date, keywords: list[str], items: list[dict[str, str]], errors: list[str]) -> str:
    today = dt.date.today()
    lines = [
        f"# KV Cache Related Papers Since {since.isoformat()}",
        "",
        f"- Generated: {today.isoformat()}",
        f"- Date range: {since.isoformat()} to {today.isoformat()}",
        f"- Total results: {len(items)}",
        f"- Keywords: {', '.join(keywords)}",
        "",
        "## Priority Definition",
        "",
        "- P1: KV cache sharing and communication. Cross-request, cross-user, cross-model, multi-agent, handoff, relay, or explicit KV/token communication.",
        "- P2: KV compression, quantization, eviction, and mechanism analysis. Representation-level, token-level, or theory/diagnostic work on how KV is stored, retained, approximated, reconstructed, or why compression works.",
        "- P3: KV-enabled application acceleration. Workloads that use prefix/prompt caching, cache reuse, or KV-aware execution to speed up RAG, agents, VLM/VLA, MoE, video, code, or other tasks.",
        "- P4: General KV cache research. Relevant KV work that is not primarily about sharing, algorithms, or application acceleration.",
        "- P5: Serving systems and peripheral references. Disaggregated serving, scheduling, offloading, memory tiers, general inference systems, and background references; kept for context, not a primary target.",
        "",
    ]

    groups = [
        ("P1: KV Cache Sharing and Communication", lambda item: item.get("rank_priority") == "1"),
        ("P2: KV Compression, Quantization, Eviction, and Mechanism Analysis", lambda item: item.get("rank_priority") == "2"),
        ("P3: KV-Enabled Application Acceleration", lambda item: item.get("rank_priority") == "3"),
        ("P4: General KV Cache Research", lambda item: item.get("rank_priority") == "4"),
        ("P5: Serving Systems and Peripheral References", lambda item: item.get("rank_priority") == "5"),
    ]
    for title, predicate in groups:
        grouped = [item for item in items if predicate(item)]
        lines.extend(render_table(title, grouped))

    if errors:
        lines.extend(["## Search Errors", ""])
        lines.extend(f"- {error}" for error in errors)
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_table(title: str, items: list[dict[str, str]]) -> list[str]:
    lines = [f"## {title}", ""]
    if not items:
        lines.extend(["No results.", ""])
        return lines

    lines.extend(
        [
            "| Date | Fit | Priority | Title | Source | Why it matches |",
            "|---|---:|---|---|---|---|",
        ]
    )
    for item in items:
        title_text = pf.strip_html(item.get("title", "Untitled")).replace("|", "/")
        url = item.get("url", "")
        linked_title = f"[{title_text}]({url})" if url else title_text
        lines.append(
            "| "
            + " | ".join(
                [
                    item.get("published", ""),
                    item.get("rank_score", ""),
                    item.get("rank_category", ""),
                    linked_title,
                    item.get("source", ""),
                    item.get("fit_reason", "").replace("|", "/"),
                ]
            )
            + " |"
        )
    lines.append("")
    return lines


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a Markdown report for KV-cache related papers since a date.")
    parser.add_argument("--since", default=DEFAULT_SINCE.isoformat(), help="Start date in YYYY-MM-DD format.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Markdown output path.")
    parser.add_argument("--max-results-per-source", type=int, default=100)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    since = dt.date.fromisoformat(args.since)
    output = Path(args.output)
    keywords, items, errors = collect_related_papers(since, args.max_results_per_source)
    output.parent.mkdir(exist_ok=True)
    output.write_text(render_markdown(since, keywords, items, errors), encoding="utf-8")
    print(f"Report written: {output}")
    print(f"Results: {len(items)}")
    if errors:
        print("Errors:")
        for error in errors:
            print(f"- {error}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
