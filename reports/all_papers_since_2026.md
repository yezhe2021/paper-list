# KV Cache Related Papers Since 2026-01-01

- Generated: 2026-09-21
- Date range: 2026-01-01 to 2026-09-21
- Total results: 6
- Keywords: kv cache sharing, cross model kv cache sharing, multi agent kv cache communication, kv cache reuse, kv cache compression, kv cache quantization, long context inference, llm inference acceleration, cache compression, llm inference

## Priority Definition

- P1: KV cache sharing and communication. Cross-request, cross-user, cross-model, multi-agent, handoff, relay, or explicit KV/token communication.
- P2: KV compression, quantization, eviction, and mechanism analysis. Representation-level, token-level, or theory/diagnostic work on how KV is stored, retained, approximated, reconstructed, or why compression works.
- P3: KV-enabled application acceleration. Workloads that use prefix/prompt caching, cache reuse, or KV-aware execution to speed up RAG, agents, VLM/VLA, MoE, video, code, or other tasks.
- P4: General KV cache research. Relevant KV work that is not primarily about sharing, algorithms, or application acceleration.
- P5: Serving systems and peripheral references. Disaggregated serving, scheduling, offloading, memory tiers, general inference systems, and background references; kept for context, not a primary target.

## P1: KV Cache Sharing and Communication

No results.

## P2: KV Compression, Quantization, Eviction, and Mechanism Analysis

| Date | Fit | Priority | Title | Source | Why it matches |
|---|---:|---|---|---|---|
|  | 9 | P2 KV compression, quantization, eviction, and mechanism analysis | [Reasoning-Aware Error-Bounded KV-Cache Compression and Sparse Attention for Long-Context LLMs](https://doi.org/10.21203/rs.3.rs-10952127/v1) | Crossref | proposes KV representation, retention, compression, quantization, eviction, or mechanism analysis; mechanisms: compression; context: inference, serving, latency, memory |
| 2026-09-08 | 2 | P2 KV compression, quantization, eviction, and mechanism analysis | [To Keep or Not to Keep: Learning KV Cache Retention in Disaggregated LLM Serving Systems](https://doi.org/10.1145/3793230.3837769) | Crossref | proposes KV representation, retention, compression, quantization, eviction, or mechanism analysis; mechanisms: disaggregated; context: serving |

## P3: KV-Enabled Application Acceleration

| Date | Fit | Priority | Title | Source | Why it matches |
|---|---:|---|---|---|---|
| 2026-09-16 | 3 | P3 KV-enabled application acceleration | [Review of: "Towards More Economical Context-Augmented LLM Generation by Reusing Stored KV Cache"](https://doi.org/10.32388/f2fnb3) | Crossref | uses KV/cache behavior to accelerate a workload or task |

## P4: General KV Cache Research

No results.

## P5: Serving Systems and Peripheral References

| Date | Fit | Priority | Title | Source | Why it matches |
|---|---:|---|---|---|---|
|  | 3 | P5 serving systems and peripheral references | [Does Linguistic Register Affect Faithfulness in Spanish Cache-Augmented Generation? An Exploratory Study with Open-Source LLMs](https://doi.org/10.20944/preprints202609.0733.v1) | Crossref | broader cache/context/inference relation |
| 2026-09-08 | 1 | P5 serving systems and peripheral references | [Peer-to-Peer Key-Value Cache Offload](https://doi.org/10.1145/3793230.3840405) | Crossref | serving architecture, disaggregation, scheduling, offloading, or lifecycle management |
| 2026-09-01 | 1 | P5 serving systems and peripheral references | [Co-Optimizing Request Scheduling and KV Caching for Edge LLM Serving](https://doi.org/10.1109/jiot.2026.3709703) | Crossref | serving architecture, disaggregation, scheduling, offloading, or lifecycle management; context: serving |

## Search Errors

- openalex: <urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1000)>
- semantic_scholar: HTTP 429 rate limited; wait before retrying this source
