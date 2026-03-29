# 完全免费第一版技术方案：每周一篇科技周报，每天追加更新

## 1. 目标

在当前 Hugo 博客仓库中实现一套完全免费的自动化流程：

- 文章目录保持现状，使用 `content/post`
- 每周生成一篇科技周报文章
- 每天早上 8:30 按 `GMT+8` 运行一次
- 收集前一天的免费 RSS 科技新闻
- 对新闻做过滤、去重、事件聚合、排序
- 将当天结果追加到本周周报文章中
- 动态生成周报 `tags`
- 自动生成每周头图
- 生成中英双语标题和正文
- 自动提交并 push 到 GitHub
- 由 Netlify 检测 push 后自动发布

第一版目标是“稳定可用、零 API 成本、内容结构清晰”，不追求复杂的 AI 润色。

## 2. 非目标

第一版不包含以下能力：

- 不接入 OpenAI API 或任何付费模型 API
- 不接入 NewsAPI、SerpAPI 等付费新闻聚合服务
- 不追求全网最全、最实时的科技新闻覆盖
- 不自动生成高质量长篇评论型正文
- 不接入付费翻译或图像生成服务

## 3. 总体思路

使用 `GitHub Actions + 免费 RSS + Python 脚本 + Hugo 内容文件更新` 实现自动化。

执行链路如下：

1. GitHub Actions 每天定时触发
2. 脚本拉取白名单 RSS
3. 过滤前一天 `GMT+8` 的新闻条目
4. 执行去重与事件聚合
5. 选出当天值得收录的新闻
6. 新建或更新本周周报文章
7. 提交并 push 到仓库默认分支
8. Netlify 自动构建并发布

## 4. 为什么选择这个方案

- 免费：不依赖任何付费 API
- 稳定：不依赖本地机器开机
- 兼容现有仓库：继续使用 `content/post/<slug>/index.md`
- 对博客干扰小：一周只保留一篇周报文章，每天增量更新
- 视觉统一：每周文章自动带头图
- 后续可升级：未来可无缝加上 AI 摘要和润色

## 5. 时间规则

### 5.1 定时执行时间

- 目标执行时间：每天 `08:30 GMT+8`
- GitHub Actions cron 使用 UTC
- 对应 cron：`30 0 * * *`

### 5.2 新闻时间窗口

每天运行时，抓取“前一天 `GMT+8`”的新闻，而不是前一天 UTC。

例如：

- 运行时间：`2026-03-30 08:30 +08`
- 抓取范围：`2026-03-29 00:00:00 +08` 到 `2026-03-29 23:59:59 +08`

### 5.3 周报归档规则

建议采用 ISO 周：

- 周报标题：`科技周报 | 2026 W14`
- 文章目录：`content/post/2026-w14-tech-weekly/index.md`

每天运行时：

- 如果本周周报不存在，则新建
- 如果本周周报已存在，则在文末追加当天 section
- 周报首次创建时自动生成本周头图

## 6. 新闻源策略

### 6.1 目标

免费前提下，尽量保证新闻的权威性和相关性。

### 6.2 新闻源类型

仅使用公开可访问的 RSS，不使用付费 API。

建议第一版白名单包括：

- TechCrunch
- The Verge
- Ars Technica
- Hacker News
- OpenAI Blog
- Anthropic News / Blog
- Google Blog
- Google DeepMind Blog
- GitHub Blog
- AWS News Blog
- Cloudflare Blog

### 6.3 白名单原则

- 优先官方源
- 其次是一线科技媒体
- 源数量保持在 8 到 15 个之间，避免噪声过多
- 后续可以逐步增减源，而不是一开始铺太大

## 7. “重要新闻”定义

RSS 不能天然告诉我们“全网最重要新闻”，所以第一版使用规则排序逼近这个目标。

第一版中，“重要”由以下信号综合判断：

- 是否来自官方源
- 是否涉及重点主题
- 是否被多个白名单源同时报道
- 标题中是否出现重要实体或关键动作
- 是否与博客定位相关

### 7.1 重点主题

建议优先保留以下主题：

- AI 模型、AI 产品、AI 平台
- 开发工具与工程效率
- 云平台与基础设施
- 开源项目与开发者生态
- 大厂技术战略、并购、发布会、重大事故

### 7.2 弱相关内容直接降权或丢弃

例如：

- 消费电子评测
- 招聘信息
- 活动预告
- 视频播客
- 纯观点文章
- 促销与营销稿

## 8. 去重与整合逻辑

这一部分是第一版的核心。

### 8.1 第 1 层：源级过滤

每条 RSS 条目先做基础过滤：

- 发布时间必须落在前一天 `GMT+8` 窗口内
- 分类或标题需命中科技相关主题
- 链接不能是视频页、播客页、活动页、广告页
- 标题长度和描述长度不能过短

### 8.2 第 2 层：硬去重

对候选新闻执行直接去重：

- `link` 完全相同，去重
- `guid/id` 相同，去重
- 标题标准化后完全相同，去重

标题标准化建议包括：

- 转小写
- 去除标点
- 去除多余空格
- 去掉弱语义词，例如 `opinion`、`review`、`live`、`analysis`

### 8.3 第 3 层：事件级聚合

不同媒体可能用不同标题报道同一事件，因此需要按事件聚类。

第一版不做复杂 NLP，使用规则聚合：

- 比较标准化标题的相似度
- 提取实体词，如公司名、产品名、模型名
- 提取动作词，如 `launch`、`release`、`acquire`、`open-source`、`raise`
- 若实体和动作高度重合，则归为同一事件

可用的简单规则：

- 标题相似度超过阈值则视为同一事件
- 两条新闻出现相同主体和相同动作时视为同一事件
- 若发布时间很接近且关键词高度重合，则优先聚合

### 8.4 第 4 层：选主来源

每个事件 cluster 只在周报中输出一条。

优先级建议：

1. 官方原始发布源
2. 一线科技媒体
3. 二手转述或聚合站

输出时保留：

- 主标题
- 主链接
- 来源名
- 补充来源列表

### 8.5 第 5 层：周内防重复

因为是“每天更新同一篇周报”，所以每天追加前必须检查本周文章中是否已经记录过类似事件。

判断依据：

- 主链接是否已存在
- 标题标准化结果是否已存在
- 事件关键词组合是否已存在

若匹配已收录事件，则当天跳过该条，避免同一周重复出现。

## 9. 排序逻辑

经过聚合后，对事件进行排序，决定当天写入哪些新闻。

第一版可采用简单打分：

- 官方源：+5
- 一线科技媒体：+3
- 被多个源报道：每多 1 个源 +2
- 命中重点实体：+3
- 命中重点动作：+2
- 标题含明显营销词：-2
- 弱相关主题：-3

最终：

- 取得分前 3 到 8 条写入周报
- 如果有效事件少于 3 条，则当天不更新

## 10. 摘要生成策略

因为第一版完全免费，不调用模型 API，所以摘要采用“规则摘要”。

### 10.1 规则摘要来源

按优先级取字段：

1. RSS `summary` 或 `description`
2. 标题本身
3. 补充来源的简短描述

### 10.2 摘要清洗规则

- 去 HTML 标签
- 截断过长描述
- 去掉“阅读全文”“继续阅读”“sponsored”类噪声
- 去掉明显模板化尾巴

### 10.3 最终输出风格

每条新闻只生成简短结构，不写强主观评论：

- 标题
- 来源
- 1 到 2 句摘要
- 原文链接
- 可选的补充来源链接

这样虽然文风没有 AI 版自然，但稳定、零成本、可控。

## 11. Hugo 文章格式建议

### 11.1 目录结构

沿用当前仓库风格：

`content/post/2026-w14-tech-weekly/index.md`

文章目录下同时包含自动生成的头图：

`content/post/2026-w14-tech-weekly/cover.svg`

### 11.2 front matter 示例

建议继续使用 TOML：

```toml
+++
date = '2026-03-30T08:30:00+08:00'
draft = false
title = '科技周报 | Tech Weekly | 2026 W14'
description = '2026 年第 14 周科技新闻周报，按日更新。 Weekly tech digest for 2026 W14.'
categories = ['Tech Digest']
tags = ['Tech News', 'Weekly', 'AI', 'Engineering']
image = 'cover.svg'
+++
```

### 11.3 正文结构示例

```md
本周整理前一天公开 RSS 中值得关注的科技新闻，按日追加。
This weekly post collects notable tech news from public RSS feeds and is updated daily.

## 2026-03-29

### OpenAI 发布某项新能力
### OpenAI Launches a New Capability

来源 / Source: OpenAI Blog

**中文摘要：**
OpenAI 发布了某项新能力，重点在于 xxx。该更新主要面向 xxx，意味着 xxx。

**English Summary:**
OpenAI announced a new capability focused on xxx. The update is mainly aimed at xxx and implies xxx.

原文链接 / Source:
https://...

补充来源 / Related:
https://...

### GitHub 发布某项更新
### GitHub Releases an Update

来源 / Source: GitHub Blog

**中文摘要：**
GitHub 宣布 xxx，重点变化包括 xxx。对开发者的直接影响是 xxx。

**English Summary:**
GitHub announced xxx, with the key changes including xxx. The direct impact on developers is xxx.

原文链接 / Source:
https://...
```

### 11.4 双语输出规则

第一版采用“结构化双语”：

- 周报标题使用中英混合标题
- 每天 section 日期只保留一份
- 每条新闻输出中英文双标题
- 每条新闻输出中文摘要和英文摘要
- 链接字段统一写成 `来源 / Source`

英文部分优先使用原 RSS 标题和描述清洗后的结果。

中文部分使用规则式处理：

- 对标题做关键词映射和模板翻译
- 对描述做截断、清洗、重组
- 不追求文学化润色，优先可读和稳定

## 12. 动态标签策略

周报文章的 `tags` 不应写死，而应根据本周事件动态生成。

### 12.1 基础标签

每篇周报固定包含：

- `Tech News`
- `Weekly`

### 12.2 动态标签来源

根据本周已收录新闻的标题、来源和关键词命中结果生成。

示例映射：

- `openai`、`anthropic`、`gpt`、`llm`、`gemini` -> `AI`
- `github`、`vscode`、`sdk`、`cli` -> `Developer Tools`
- `aws`、`cloudflare`、`kubernetes`、`gcp` -> `Cloud`
- `open source`、`apache`、`linux foundation` -> `Open Source`
- `security`、`breach`、`vulnerability` -> `Security`

### 12.3 生成规则

- 先收集本周所有事件命中的标签
- 统计频次
- 选取频次最高的前 2 到 4 个动态标签
- 与基础标签合并后写入 front matter

这样每周周报的标签会随内容变化，而不是固定不变。

## 13. 每周头图生成策略

第一版头图必须自动生成，并且完全免费。

### 13.1 生成时机

仅在“本周周报首次创建”时生成一次头图。

后续本周内每天更新文章正文，不重复生成封面。

### 13.2 生成方式

优先使用程序化生成的 `SVG`：

- 不依赖外部服务
- 不需要付费图像 API
- 文本清晰
- 文件体积小
- 直接适配 Hugo Page Bundle

### 13.3 封面内容

头图建议包含：

- 主标题：`科技周报 | Tech Weekly`
- 周次：如 `2026 W14`
- 日期范围：如 `2026-03-30 to 2026-04-05`
- 可选主题色：按本周主标签决定

### 13.4 配色建议

根据主标签动态选色：

- `AI`：青绿系
- `Cloud`：蓝色系
- `Security`：橙红系
- `Open Source`：深绿系
- 默认：灰蓝系

### 13.5 文件路径

封面保存到：

`content/post/<slug>/cover.svg`

front matter 写入：

```toml
image = 'cover.svg'
```

## 14. 仓库内建议的文件结构

第一版建议新增以下内容：

```text
.github/workflows/daily-tech-weekly.yml
scripts/tech_weekly/
scripts/tech_weekly/fetch_rss.py
scripts/tech_weekly/filter_and_cluster.py
scripts/tech_weekly/generate_cover.py
scripts/tech_weekly/render_weekly_post.py
scripts/tech_weekly/run.py
scripts/tech_weekly/sources.yaml
docs/free-tech-weekly-plan-v1.md
```

说明：

- `fetch_rss.py`：抓取 RSS
- `filter_and_cluster.py`：过滤、去重、事件聚合、排序
- `generate_cover.py`：生成每周封面 `cover.svg`
- `render_weekly_post.py`：新建或更新周报文章
- `run.py`：总入口
- `sources.yaml`：新闻源配置

## 15. GitHub Actions 设计

### 13.1 触发方式

- 每天定时执行
- 允许手动触发，便于调试

建议：

```yaml
on:
  schedule:
    - cron: '30 0 * * *'
  workflow_dispatch:
```

### 13.2 任务步骤

1. checkout 仓库
2. 配置 Python 运行环境
3. 安装免费依赖
4. 运行 `scripts/tech_weekly/run.py`
5. 检查是否产生内容变更
6. 若有变更则自动 commit 和 push
7. Netlify 自动发布

### 13.3 依赖建议

尽量只用轻量免费库，例如：

- `feedparser`
- `python-dateutil`
- `pytz` 或标准库 `zoneinfo`
- `PyYAML`
- `beautifulsoup4`

## 16. 提交策略

自动化任务只提交内容层文件，不提交构建产物。

建议提交范围：

- `content/post/...`
- 未来如有缓存文件，建议不要入库

不建议自动提交：

- `public/`
- `resources/_gen/`

理由：

- 这些由 Netlify 构建即可
- 能避免提交噪声
- 能减少与本地已有未提交改动的冲突

## 17. 失败与兜底策略

第一版需要明确“不发也比乱发好”。

建议规则：

- RSS 拉取失败但仍有其他源可用，则继续
- 某个源格式异常，则跳过该源
- 有效事件少于 3 条，则当天不更新
- 如果当天 section 已存在，则不重复写入
- 如果本周文章不存在且当天事件不足阈值，则不创建空周报

## 18. 可观测性

第一版至少需要日志，便于后续排查。

建议在 GitHub Actions 日志中输出：

- 本次运行时间窗口
- 每个 RSS 源抓取条数
- 过滤后条数
- 硬去重后条数
- 聚合后事件数
- 最终写入条数
- 是否创建新周报
- 是否生成新封面
- 是否追加成功

## 19. 已知边界

这套免费方案有明确边界：

- 无法保证“全网最重要新闻”全覆盖
- 对突发事件敏感度不如社交平台或付费聚合服务
- 规则摘要的可读性不如模型生成摘要
- 规则双语的自然度不如模型翻译或人工润色
- 事件聚合准确率不会像带 NLP 或大模型那样高

但它足以作为个人博客的第一版自动周报系统。

## 20. 第二阶段可升级方向

第一版跑稳后，可以逐步升级：

### 18.1 低成本升级

- 增加更多高质量 RSS
- 优化关键词和打分规则
- 增加更稳的周内防重
- 增加一个“本周观察”占位段落，供手动补充
- 优化双语标题和双语摘要模板
- 丰富封面模板和视觉样式

### 18.2 付费升级

- 接入 OpenAI API 生成中文摘要与更自然的整合段落
- 对事件做更准确的实体抽取和聚类
- 自动生成标题与描述
- 自动给出简短评论
- 自动生成更丰富的双语文案和封面创意

## 21. 实施步骤建议

建议按以下顺序落地：

1. 新增 `sources.yaml`，先确认 RSS 白名单
2. 实现 RSS 抓取与时间窗口过滤
3. 实现硬去重和简单聚合
4. 实现动态 `tags` 计算
5. 实现周报文件的新建与追加逻辑
6. 实现每周 `cover.svg` 自动生成
7. 本地手动跑通一轮
8. 接入 GitHub Actions 定时任务
9. 观察一周，再调规则

## 22. 最终建议

第一版应把目标定得保守：

- 免费
- 稳定
- 不重复
- 不喧宾夺主
- 支持中英双语
- 每周自动生成头图
- 与博客现有目录和发布流程兼容

因此建议采用：

- `content/post` 保持不变
- 每周一篇周报
- 每天 8:30 按 `GMT+8` 追加前一天新闻
- 免费 RSS 白名单抓取
- 规则去重、事件聚合、规则摘要
- 动态生成 `tags`
- 周报首次创建时自动生成 `cover.svg`
- 标题到正文采用结构化中英双语
- GitHub Actions 自动提交
- Netlify 自动发布

这是一套成本最低、可维护性最好、最适合作为第一版上线的方案。
