# 论文自动查找工具

这个工具会从 `papers/` 中的论文提取关键词，并每天自动查询最新相关论文与资料。

## 检索渠道

默认查询：

- arXiv：预印本论文
- OpenAlex：开放学术索引
- Semantic Scholar：论文与引用索引
- Crossref：DOI 与出版物索引
- GitHub：相关代码仓库、复现项目、论文列表和研究资料

GitHub 结果不一定是论文正文，会单独放在 `New GitHub/resources` 部分。

## 使用方式

1. 把论文放到 `papers/` 目录。支持 `.txt`、`.md`，安装 `pypdf` 后支持 `.pdf`。
2. 运行：

```powershell
python .\paper_finder.py --init
python .\paper_finder.py
```

3. 查看输出：

- `reports/latest.md`：最新一次查询结果
- `reports/YYYY-Www.md`：按 ISO 周合并保存的查询结果，例如 `2026-W22.md`
- `.paper_finder_state.json`：已见结果记录，避免每日重复刷屏

同一天重复运行会替换本周文件中的当天段落，不会重复追加。

## 关注方向和排序

当前配置重点关注 KV cache：

- P1：KV cache 共享、跨请求、跨模型、多智能体、通信、解耦传输
- P2：KV cache 本身研究，例如压缩、量化、驱逐、管理
- P3：利用 KV cache 优化某个任务或系统，例如 prefix caching、cache reuse、推理加速
- P4/P5：更泛的 cache、context、inference 相关内容

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
- `days_back`：查询最近多少天的新结果
- `max_results_per_source`：每个来源最多返回多少条
- `max_pdf_pages`：每篇 PDF 最多读取多少页用于提取关键词

## 每日自动查询

每日自动任务会在北京时间每天 09:00 于当前工作区运行：

```powershell
python .\paper_finder.py
```

结果会更新到 `reports/latest.md`，并合并进当周的 `reports/YYYY-Www.md`。
