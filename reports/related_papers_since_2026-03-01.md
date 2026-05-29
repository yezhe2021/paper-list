# KV Cache Related Papers Since 2026-03-01

- Generated: 2026-05-29
- Date range: 2026-03-01 to 2026-05-29
- Total results: 64
- Keywords: kv cache sharing, cross model kv cache sharing, multi agent kv cache communication, kv cache reuse, kv cache compression, kv cache quantization, long context inference, llm inference acceleration, cache compression, llm inference

## Priority Definition

- P1: KV cache sharing, cross-request, cross-model, multi-agent, communication, or disaggregated transfer.
- P2: Core KV cache research, including compression, quantization, eviction, offloading, and management.
- P3: Systems or tasks optimized by KV cache reuse, prefix caching, or inference acceleration.
- P4/P5: Broader cache, context, inference, or agent-memory related work.

## P1: Shared / Multi-Model / Multi-Agent KV Cache

| Date | Fit | Priority | Title | Source | Why it matches |
|---|---:|---|---|---|---|
| 2026-05-13 | 13 | P1 multi-model/multi-agent/shared KV cache | [KVServe: Service-Aware KV Cache Compression for Communication-Efficient Disaggregated LLM Serving](https://openalex.org/W7161354758) | OpenAlex | explicit KV cache sharing/reuse/communication or cross-request/cross-model signal; core KV-cache mechanisms: compression, disaggregated; system/task optimization: inference, serving, latency, bandwidth |
| 2026-05-22 | 11 | P1 multi-model/multi-agent/shared KV cache | [CachePrune: Privacy-Aware and Fine-Grained KV Cache Sharing for Efficient LLM Inference](https://arxiv.org/abs/2605.23640) | arXiv | explicit KV cache sharing/reuse/communication or cross-request/cross-model signal; system/task optimization: inference |
| 2026-04-21 | 10 | P1 multi-model/multi-agent/shared KV cache | [PolyKV: Shared Asymmetric TurboQuant-Compressed KV Memory for Multi-Agent LLMs](https://doi.org/10.5281/zenodo.19686729) | OpenAlex | explicit KV cache sharing/reuse/communication or cross-request/cross-model signal; core KV-cache mechanisms: compression, quantization; system/task optimization: inference, memory, agent |
| 2026-05-16 | 7 | P1 multi-model/multi-agent/shared KV cache | [ObjectCache: Layerwise Object-Storage Retrieval for KV Cache Reuse](https://arxiv.org/abs/2605.22850) | OpenAlex + arXiv | explicit KV cache sharing/reuse/communication or cross-request/cross-model signal; system/task optimization: inference, serving, latency, memory |
| 2026-05-05 | 4 | P1 multi-model/multi-agent/shared KV cache | [QKVShare: Quantized KV-Cache Handoff for Multi-Agent On-Device LLMs](https://openalex.org/W7160565216) | OpenAlex | explicit KV cache sharing/reuse/communication or cross-request/cross-model signal; core KV-cache mechanisms: quantization, prefill; system/task optimization: latency, agent |
| 2026-04-19 | 3 | P1 multi-model/multi-agent/shared KV cache | [Hive: A Multi-Agent Infrastructure for Algorithm- and Task-Level Scaling](https://openalex.org/W7155247049) | OpenAlex | explicit KV cache sharing/reuse/communication or cross-request/cross-model signal; system/task optimization: inference, agent |
| 2026-05-03 | 2 | P1 multi-model/multi-agent/shared KV cache | [Efficient Multi-Lora Deployment via Shared KV-Cache with Task-Adaptive Tokens](https://doi.org/10.1109/icassp55912.2026.11463477) | Crossref | explicit KV cache sharing/reuse/communication or cross-request/cross-model signal |
| 2026-04-07 | 2 | P1 multi-model/multi-agent/shared KV cache | [ForkKV: Scaling Multi-LoRA Agent Serving via Copy-on-Write Disaggregated KV Cache](https://openalex.org/W7153670755) | OpenAlex | explicit KV cache sharing/reuse/communication or cross-request/cross-model signal; core KV-cache mechanisms: management, disaggregated; system/task optimization: serving, throughput, memory, agent |

## P2: Core KV Cache Research

| Date | Fit | Priority | Title | Source | Why it matches |
|---|---:|---|---|---|---|
| 2026-05-26 | 12 | P2 core KV cache research | [Hurwitz Quaternion Multiplicative Quantization for KV Cache Compression](https://arxiv.org/abs/2605.27646) | arXiv | core KV-cache mechanisms: compression, quantization |
| 2026-05-26 | 12 | P2 core KV cache research | [NestedKV: Nested Memory Routing for Long-Context KV Cache Compression](https://arxiv.org/abs/2605.26678) | arXiv | core KV-cache mechanisms: compression; system/task optimization: memory, long-context |
| 2026-05-24 | 12 | P2 core KV cache research | [Polynomial Context-Truncation Sensitivity in Autoregressive Language Models: Sequential Wyner-Ziv Bounds for KV Cache Compression](https://arxiv.org/abs/2605.25085) | arXiv | core KV-cache mechanisms: compression |
| 2026-05-28 | 11 | P2 core KV cache research | [Moment- KV : Momentum-Based Decode-Time KV Cache Compression for Long Generation](https://arxiv.org/abs/2605.29873) | arXiv | core KV-cache mechanisms: compression |
| 2026-05-22 | 11 | P2 core KV cache research | [A Simple Plug-in for Improving Eviction-Based KV Cache Compression](https://arxiv.org/abs/2605.23258) | arXiv | core KV-cache mechanisms: compression, eviction |
| 2026-05-21 | 11 | P2 core KV cache research | [MuKV: Multi-Grained KV Cache Compression for Long Streaming Video Question-Answering](https://arxiv.org/abs/2605.22269) | arXiv | core KV-cache mechanisms: compression |
| 2026-05-14 | 11 | P2 core KV cache research | [KVCapsule: Efficient Sequential KV Cache Compression for Vision-Language Models with Asymmetric Redundancy](https://arxiv.org/abs/2605.16439) | arXiv | core KV-cache mechanisms: compression |
| 2026-05-10 | 11 | P2 core KV cache research | [Forcing-KV: Hybrid KV Cache Compression for Efficient Autoregressive Video Diffusion Models](https://arxiv.org/abs/2605.09681) | arXiv | core KV-cache mechanisms: compression; system/task optimization: memory |
| 2026-05-03 | 11 | P2 core KV cache research | [SemantiCache: Efficient KV Cache Compression Via Semantic Chunking and Clustered Merging](https://doi.org/10.1109/icassp55912.2026.11464823) | Crossref | core KV-cache mechanisms: compression |
| 2026-05-04 | 9 | P2 core KV cache research | [BUZZ: Beehive-structured Sparse KV Cache with Segmented Heavy Hitters for Efficient LLM Inference](https://doi.org/10.1145/3810942) | Crossref | core KV-cache mechanisms: compression; system/task optimization: inference, serving, memory, long-context |
| 2026-05-20 | 8 | P2 core KV cache research | [Adaptive KV Cache Reuse for Fast Long-Context LLM Serving](https://arxiv.org/abs/2605.24022) | arXiv | core KV-cache mechanisms: prefill; system/task optimization: inference, serving, latency, long-context |
| 2026-05-19 | 8 | P2 core KV cache research | [OScaR: The Occam's Razor for Extreme KV Cache Quantization in LLMs and Beyond](https://arxiv.org/abs/2605.19660) | arXiv | core KV-cache mechanisms: quantization; system/task optimization: memory, long-context |
| 2026-05-18 | 8 | P2 core KV cache research | [KVDrive: A Holistic Multi-Tier KV Cache Management System for Long-Context LLM Inference](https://arxiv.org/abs/2605.18071) | arXiv | core KV-cache mechanisms: management; system/task optimization: inference, memory, long-context |
| 2026-05-18 | 8 | P2 core KV cache research | [KVD rive: A Holistic Multi-Tier KV Cache Management System for Long-Context LLM Inference](https://doi.org/10.1145/3802077) | Crossref | core KV-cache mechanisms: offloading, management; system/task optimization: inference, serving, latency, throughput |
| 2026-05-03 | 8 | P2 core KV cache research | [Compressing Kv Cache for Long-Context LLM Inference with Inter-Layer Attention Similarity](https://doi.org/10.1109/icassp55912.2026.11464826) | Crossref | system/task optimization: inference, long-context |
| 2026-04-23 | 8 | P2 core KV cache research | [SparKV: Overhead-Aware KV Cache Loading for Efficient On-Device LLM Inference](https://openalex.org/W7155654182) | OpenAlex | core KV-cache mechanisms: prefill; system/task optimization: inference, latency |
| 2026-05-23 | 7 | P2 core KV cache research | [CONF- KV : Confidence-Aware KV Cache Eviction with Mixed-Precision Storage for Long-Horizon LLM](https://arxiv.org/abs/2605.24786) | arXiv | core KV-cache mechanisms: eviction; system/task optimization: inference |
| 2026-05-03 | 6 | P2 core KV cache research | [ShrinKV: Key-Value Cache Compression with Progressive Hidden States Shrinking to Mitigate Prefilling Latency](https://doi.org/10.1109/icassp55912.2026.11463859) | Crossref | core KV-cache mechanisms: compression, prefill; system/task optimization: latency |
| 2026-05-13 | 5 | P2 core KV cache research | [SPHERICAL KV: Angle-Domain Attention and Rate-Distortion Retention for Efficient Long-Context Inference](https://openalex.org/W7162045077) | OpenAlex | core KV-cache mechanisms: quantization, eviction, offloading; system/task optimization: inference, serving, memory, bandwidth |
| 2026-05-13 | 4 | P2 core KV cache research | [Attention Once Is All You Need: Efficient Streaming Inference with Stateful Transformers](https://arxiv.org/abs/2605.13784) | arXiv | core KV-cache mechanisms: prefill; system/task optimization: inference |
| 2026-05-21 | 3 | P2 core KV cache research | [ArborKV: Structure-Aware KV Cache Management for Scaling Tree-based LLM Reasoning](https://arxiv.org/abs/2605.22106) | arXiv | core KV-cache mechanisms: management; system/task optimization: inference |
| 2026-05-20 | 3 | P2 core KV cache research | [OCTOPUS: Optimized KV Cache for Transformers via Octahedral Parametrization Under optimal Squared error quantization](https://arxiv.org/abs/2605.21226) | arXiv | core KV-cache mechanisms: quantization |
| 2026-05-10 | 3 | P2 core KV cache research | [Make Each Token Count: Towards Improving Long-Context Performance with KV Cache Eviction](https://arxiv.org/abs/2605.09649) | arXiv | core KV-cache mechanisms: eviction; system/task optimization: long-context |
| 2026-04-16 | 3 | P2 core KV cache research | [Prefill-as-a-Service: KVCache of Next-Generation Models Could Go Cross-Datacenter](https://openalex.org/W7154865342) | OpenAlex | core KV-cache mechanisms: offloading, prefill; system/task optimization: serving, latency, throughput, bandwidth |
| 2026-03-15 | 3 | P2 core KV cache research | [OxyGen: Unified KV Cache Management for VLA Inference under Multi-Task Parallelism](https://openalex.org/W7139147858) | OpenAlex | core KV-cache mechanisms: management, prefill; system/task optimization: inference, throughput, memory, agent |
| 2026-05-20 | 2 | P2 core KV cache research | [Runtime-Certified Bounded-Error Quantized Attention](https://arxiv.org/abs/2605.20868) | arXiv | broader cache/context/inference relation |
| 2026-05-18 | 2 | P2 core KV cache research | [Protection Is (Nearly) All You Need: Structural Protection Dominates Scoring in Globally Capped KV Eviction](https://arxiv.org/abs/2605.18053) | arXiv | core KV-cache mechanisms: eviction |
| 2026-05-03 | 2 | P2 core KV cache research | [MIDAS: A Dynamic Cross-GPU KV Cache Offloading Framework for LLM on GPU Cluster Systems](https://doi.org/10.1109/icassp55912.2026.11461518) | Crossref | core KV-cache mechanisms: offloading |

## P3: KV-Cache-Enabled Optimization

| Date | Fit | Priority | Title | Source | Why it matches |
|---|---:|---|---|---|---|
| 2026-05-17 | 7 | P3 KV-cache-enabled optimization | [VeriCache: Turning Lossy KV Cache into Lossless LLM Inference](https://arxiv.org/abs/2605.17613) | arXiv | system/task optimization: inference |
| 2026-05-11 | 7 | P3 KV-cache-enabled optimization | [Continuous Discovery of Vulnerabilities in LLM Serving Systems with Fuzzing](https://arxiv.org/abs/2605.11202) | arXiv | system/task optimization: inference, serving |
| 2026-05-28 | 3 | P3 KV-cache-enabled optimization | [Future Forcing: Future-aware Training-free KV Cache Policy for Autoregressive Video Generation](https://arxiv.org/abs/2605.30083) | arXiv | system/task optimization: inference |
| 2026-04-03 | 3 | P3 KV-cache-enabled optimization | [FluxMoE: Decoupling Expert Residency for High-Performance MoE Serving](https://openalex.org/W7151672830) | OpenAlex | system/task optimization: inference, serving, throughput, memory |
| 2026-05-28 | 2 | P3 KV-cache-enabled optimization | [VideoMLA: Low-Rank Latent KV Cache for Minute-Scale Autoregressive Video Diffusion](https://arxiv.org/abs/2605.30351) | arXiv | broader cache/context/inference relation |
| 2026-05-13 | 2 | P3 KV-cache-enabled optimization | [BlockVLA: Accelerating Autoregressive VLA via Block Diffusion Finetuning](https://arxiv.org/abs/2605.13382) | arXiv | system/task optimization: inference, latency |
| 2026-05-16 | 1 | P3 KV-cache-enabled optimization | [Prefix -Adaptive Block Diffusion for Efficient Document Recognition](https://arxiv.org/abs/2605.16861) | arXiv | broader cache/context/inference relation |

## P4/P5: Broader Related Work

| Date | Fit | Priority | Title | Source | Why it matches |
|---|---:|---|---|---|---|
| 2026-05-26 | 2 | P4 general KV cache | [Echo: KV-Cache-Free Associative Recall with Spectral Koopman Operators](https://doi.org/10.1145/3786335.3813146) | Crossref | broader cache/context/inference relation |
| 2026-05-11 | 10 | P5 related cache/context/inference | [FibQuant: Universal Vector Quantization for Random-Access KV- Cache Compression](https://arxiv.org/abs/2605.11478) | arXiv | core KV-cache mechanisms: compression, quantization; system/task optimization: inference, memory, long-context |
| 2026-05-25 | 8 | P5 related cache/context/inference | [IndexMem: Learned KV - Cache Eviction with Latent Memory for Long-Context LLM Inference](https://arxiv.org/abs/2605.25475) | arXiv | core KV-cache mechanisms: eviction; system/task optimization: inference, memory, long-context |
| 2026-05-25 | 7 | P5 related cache/context/inference | [Quantized Keys Steal Attention: Bias Correction for KV - Cache Compression in Video Diffusion](https://arxiv.org/abs/2605.26266) | arXiv | core KV-cache mechanisms: compression |
| 2026-03-29 | 7 | P5 related cache/context/inference | [Probabilistic Language Tries: A Unified Framework for Compression, Decision Policies, and Execution Reuse](https://openalex.org/W7153671329) | OpenAlex | core KV-cache mechanisms: compression; system/task optimization: inference |
| 2026-05-28 | 6 | P5 related cache/context/inference | [RTP-LLM: High-Performance Alibaba LLM Inference Engine](https://arxiv.org/abs/2605.29639) | arXiv | core KV-cache mechanisms: prefill; system/task optimization: inference, serving, memory |
| 2026-05-27 | 6 | P5 related cache/context/inference | [BlockBatch: Multi-Scale Consensus Decoding for Efficient Diffusion Language Model Inference](https://arxiv.org/abs/2605.29233) | arXiv | system/task optimization: inference |
| 2026-05-27 | 6 | P5 related cache/context/inference | [SiDP: Memory-Efficient Data Parallelism for Offline LLM Inference](https://arxiv.org/abs/2605.28095) | arXiv | system/task optimization: inference, throughput, memory |
| 2026-05-09 | 6 | P5 related cache/context/inference | [ProxyKV: Cross-Model Proxy Pruning for Efficient Long-Context LLM Inference](https://arxiv.org/abs/2605.16360) | arXiv | system/task optimization: inference, long-context |
| 2026-05-21 | 5 | P5 related cache/context/inference | [ModeSwitch-LLM: A Lightweight Phase-Aware Controller for Cross-Mode LLM Inference on a Single GPU](https://arxiv.org/abs/2605.23057) | arXiv | system/task optimization: inference, serving |
| 2026-04-24 | 5 | P5 related cache/context/inference | [Network Edge Inference for Large Language Models: Principles, Techniques, and Opportunities](https://doi.org/10.1145/3809166) | OpenAlex | core KV-cache mechanisms: management; system/task optimization: inference, memory |
| 2026-03-19 | 5 | P5 related cache/context/inference | [I/O for LLM Inference: A Survey of Storage and Memory Bottlenecks](https://doi.org/10.21203/rs.3.rs-9036613/v1) | OpenAlex | system/task optimization: inference, memory |
| 2026-05-12 | 4 | P5 related cache/context/inference | [KV-Fold: One-Step KV- Cache Recurrence for Long-Context Inference](https://arxiv.org/abs/2605.12471) | arXiv | system/task optimization: inference, long-context |
| 2026-05-27 | 3 | P5 related cache/context/inference | [Gamma-World: Generative Multi-Agent World Modeling Beyond Two Players](https://arxiv.org/abs/2605.28816) | arXiv | system/task optimization: inference, agent |
| 2026-05-27 | 3 | P5 related cache/context/inference | [Augmenting Attention with Exponentially Decaying Memory Improves Query-Aware KV Sparsity](https://arxiv.org/abs/2605.28640) | arXiv | system/task optimization: inference, memory, long-context |
| 2026-05-26 | 3 | P5 related cache/context/inference | [UNIQUE: Universal Top-k Sparse Attention for Training-free Inference and Sparsity-aware Training](https://arxiv.org/abs/2605.27740) | arXiv | system/task optimization: inference, long-context |
| 2026-05-25 | 3 | P5 related cache/context/inference | [A Token/ KV - Cache Communication Media Selection and Resource Allocation Strategy for Multi-Agent Collaboration](https://arxiv.org/abs/2605.25422) | arXiv | system/task optimization: inference, latency, agent |
| 2026-05-21 | 3 | P5 related cache/context/inference | [Adaptive Mass-Segmented KV Compression for Long-Context Reasoning](https://arxiv.org/abs/2605.23200) | arXiv | core KV-cache mechanisms: compression; system/task optimization: long-context |
| 2026-05-21 | 3 | P5 related cache/context/inference | [FPCache: A Fingerprint-Rectified Learned Index Cache for Disaggregated Memory](https://doi.org/10.3390/electronics15102210) | Crossref | core KV-cache mechanisms: compression, disaggregated; system/task optimization: throughput, memory |
| 2026-05-19 | 3 | P5 related cache/context/inference | [PEEK: Context Map as an Orientation Cache for Long-Context LLM Agents](https://openalex.org/W7162045062) | OpenAlex | system/task optimization: inference, long-context, agent |
| 2026-03-23 | 3 | P5 related cache/context/inference | [LLM Agent Memory: A Survey from a Unified Representation–Management Perspective](https://doi.org/10.20944/preprints202603.0359.v2) | OpenAlex | core KV-cache mechanisms: management; system/task optimization: inference, memory, long-context, agent |

## Search Errors

- semantic_scholar: HTTP 429 rate limited; wait before retrying this source
