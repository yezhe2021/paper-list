# 论文自动查找工具

这个工具会从 `papers/` 中的论文提取关键词，并自动查询最新相关论文与资料。

## 输出文件

`reports/` 只保留两类正式输出：

- `reports/YYYY-Www.md`：每周增量周报，例如 `2026-W22.md`。每日自动查询会把当天新增结果合并到本周文件；同一天重复运行会替换当天段落。
- `reports/all_papers_since_2026.md`：2026-01-01 以来的总集合，按研究方向分组、去重并排序。

不再生成每日 `YYYY-MM-DD.md` 或额外的 `latest.md`。

## 重点方向

当前分类体系：

- P1：KV cache 共享与通信，包括跨请求、跨用户、跨模型、多智能体、handoff、relay、KV/token communication
- P2：KV 服务系统与生命周期管理，包括 disaggregated serving、prefill/decode 分离、offloading、调度、分层存储、cache pool、生产运行时
- P3：KV 压缩、量化、驱逐算法，包括表示压缩、低比特量化、token retention、eviction、重构和近似
- P4：KV 驱动的应用加速，包括 prefix/prompt caching、cache reuse、RAG、agent、VLM/VLA、MoE、video、code 等任务优化
- P5/P6：一般 KV 或外围 cache/context/inference 参考，除非能反哺 KV cache 设计，否则不作为主目标

## 检索渠道

默认查询：

- arXiv：网页 advanced search 回溯与 recent 分类页
- OpenAlex
- Semantic Scholar
- Crossref
- GitHub

## 使用方式

把论文放到 `papers/` 目录。支持 `.txt`、`.md`，安装 `pypdf` 后支持 `.pdf`。

每日/手动增量查询：

```powershell
python .\paper_finder.py
```

生成 2026 年以来总集合：

```powershell
python .\query_related_papers.py
```

也可以指定日期和输出路径：

```powershell
python .\query_related_papers.py --since 2026-01-01 --output reports\all_papers_since_2026.md
```

## 可选依赖

PDF 提取需要：

```powershell
python -m pip install pypdf
```

不安装也可以使用 `.txt` 或 `.md` 文件。

## 配置

配置文件是 `paper_finder_config.json`。常用字段：

- `sources`：启用的检索渠道
- `seed_keywords`：手动固定的重点关键词
- `papers_dir`：输入论文目录
- `max_keywords`：最终检索关键词数
- `days_back`：每日增量查询最近多少天的新结果
- `max_results_per_source`：每个来源最多返回多少条
- `max_pdf_pages`：每篇 PDF 最多读取多少页用于提取关键词

## 每日自动查询

每日自动任务会在北京时间每天 09:00 于当前工作区运行：

```powershell
python .\paper_finder.py
```

结果会合并进当周的 `reports/YYYY-Www.md`。
