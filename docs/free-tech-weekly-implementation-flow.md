# 免费科技周报第一版实施流程

## 1. 开发顺序

建议按“先本地跑通，再接自动化”的顺序实现，不要一上来先写 GitHub Actions。

原因：

- 自动化问题最难排查
- RSS、时间窗口、去重、渲染这几层只要本地没跑通，放到 CI 里只会更慢
- 本地先把输入和输出固定住，后面接 GitHub Actions 基本只是搬运

推荐顺序如下。

### 第一步：先定输入配置

先写配置文件：

- `scripts/tech_weekly/sources.yaml`
- `scripts/tech_weekly/tag_rules.yaml` 或直接放进代码

目标：

- 明确 RSS 白名单
- 明确标签映射规则
- 明确需要排除的栏目和关键词

这一阶段不碰 Hugo，不碰 GitHub Actions。

### 第二步：实现 RSS 抓取层

先写：

- `scripts/tech_weekly/fetch_rss.py`

职责：

- 读取 `sources.yaml`
- 抓取 RSS
- 统一输出原始条目结构

建议统一成这种内部数据结构：

```python
{
  "source": "TechCrunch",
  "feed_url": "...",
  "title": "...",
  "link": "...",
  "guid": "...",
  "published_at": "...",
  "summary": "...",
  "categories": [],
}
```

验收标准：

- 本地执行后能打印每个源抓到多少条
- 能拿到发布时间、标题、链接、描述
- 某个源失败不会导致整体中断

### 第三步：实现时间窗口过滤

接着写：

- `scripts/tech_weekly/filter_and_cluster.py`

先只做时间过滤，不急着做聚类。

职责：

- 把 RSS 发布时间统一转成 timezone-aware datetime
- 按 `Asia/Shanghai` 算出“前一天”的开始和结束时间
- 只保留窗口内新闻

验收标准：

- 传入固定 `--run-at` 时间时，结果可复现
- UTC、RFC822、ISO8601 等常见 RSS 时间格式都能处理

### 第四步：实现硬去重

在过滤后增加：

- `link` 去重
- `guid` 去重
- 标题标准化去重

建议把标题标准化独立成函数：

- 小写
- 去标点
- 折叠空白
- 去弱语义词

验收标准：

- 同一条新闻重复出现在多个源里时，只剩一条
- 同源重复条目可以被清掉

### 第五步：实现事件聚合与排序

这一阶段再加“软聚合”：

- 标题相似度
- 主体词命中
- 动作词命中
- 多源共现加分

产出结构建议：

```python
{
  "event_id": "...",
  "main_item": {...},
  "related_items": [...],
  "score": 12,
  "keywords": ["openai", "api"],
  "tags": ["AI", "Developer Tools"],
}
```

验收标准：

- 同一事件多源报道能合并成一个 cluster
- 最终能得到“当天推荐写入的前 N 条事件”

### 第六步：实现动态标签

写一个标签计算函数：

- 输入：当天或本周已收录的事件
- 输出：周报 front matter 使用的 tags

规则：

- 固定标签：`Tech News`、`Weekly`
- 动态标签：按事件关键词命中频次排序

验收标准：

- 同一周内容变化时，周报标签能跟着变化
- 不会出现过多零碎标签

### 第七步：实现周报内容渲染

写：

- `scripts/tech_weekly/render_weekly_post.py`

职责：

- 计算本周 slug
- 如果文章不存在则新建 `index.md`
- 如果文章已存在则追加当天 section
- 更新 front matter 中的 tags、description、date

建议把逻辑拆成：

- `ensure_weekly_post_exists()`
- `append_daily_section()`
- `update_front_matter()`

验收标准：

- 第一次运行会创建文章
- 第二次运行同一天不会重复追加
- 新的一天会追加一个新的日期 section

### 第八步：实现每周头图生成

写：

- `scripts/tech_weekly/generate_cover.py`

职责：

- 在周报首次创建时生成 `cover.svg`
- 根据主标签选择主题色
- 根据周次和日期范围生成封面文案

验收标准：

- 同一周只生成一次
- 文件落在 `content/post/<slug>/cover.svg`
- front matter 中 `image = 'cover.svg'`

### 第九步：实现总入口

写：

- `scripts/tech_weekly/run.py`

职责：

- 串联抓取、过滤、去重、聚合、渲染、封面生成
- 提供 CLI 参数，便于本地调试

建议支持：

```bash
python scripts/tech_weekly/run.py --run-at "2026-03-30T08:30:00+08:00"
python scripts/tech_weekly/run.py --dry-run
python scripts/tech_weekly/run.py --debug
```

验收标准：

- 一条命令能完整跑完
- 支持不写文件的 dry-run
- 支持输出调试日志

### 第十步：最后再接 GitHub Actions

只有当前 9 步本地都稳定后，再接 CI。

## 2. 建议的目录结构

```text
.github/workflows/daily-tech-weekly.yml
scripts/tech_weekly/
  fetch_rss.py
  filter_and_cluster.py
  generate_cover.py
  render_weekly_post.py
  run.py
  sources.yaml
  requirements.txt
docs/free-tech-weekly-plan-v1.md
docs/free-tech-weekly-implementation-flow.md
```

## 3. GitHub Actions 怎么配

建议用一个单文件 workflow：

文件：

`.github/workflows/daily-tech-weekly.yml`

### 3.1 触发条件

```yaml
name: Daily Tech Weekly

on:
  schedule:
    - cron: '30 0 * * *'
  workflow_dispatch:
```

说明：

- `schedule` 用于每天 `08:30 GMT+8`
- `workflow_dispatch` 用于手动调试

### 3.2 权限

```yaml
permissions:
  contents: write
```

因为 workflow 需要提交并 push 内容文件。

### 3.3 推荐 Job 结构

```yaml
jobs:
  update-weekly:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: pip install -r scripts/tech_weekly/requirements.txt

      - name: Run weekly updater
        run: python scripts/tech_weekly/run.py

      - name: Commit changes
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add content/post
          if git diff --cached --quiet; then
            echo "No changes to commit"
            exit 0
          fi
          git commit -m "Add/update tech weekly"
          git push
```

### 3.4 提交范围

只提交：

- `content/post/...`

不要自动提交：

- `public/`
- `resources/_gen/`

### 3.5 推荐环境变量

如果脚本里需要显式指定时区或调试模式，可以加：

```yaml
env:
  TZ: Asia/Shanghai
  PYTHONUNBUFFERED: "1"
```

不过即使设置了 `TZ`，脚本内部仍然应该显式使用 `ZoneInfo("Asia/Shanghai")`，不要依赖系统默认时区。

## 4. 调试阶段怎么调

调试必须分三层，不要直接把所有问题都留给 GitHub Actions。

### 4.1 第一层：本地纯逻辑调试

先在本地只跑 Python 脚本。

建议命令：

```bash
python scripts/tech_weekly/run.py --run-at "2026-03-30T08:30:00+08:00" --dry-run --debug
```

重点检查：

- 抓到了哪些源
- 时间窗口是否正确
- 过滤后剩多少条
- 聚合后有多少事件
- 每条事件最终分数是多少
- 预计生成哪些 tags

这一步不要写文件，先看日志。

### 4.2 第二层：本地文件输出调试

dry-run 没问题后，再测试真实写文件：

```bash
python scripts/tech_weekly/run.py --run-at "2026-03-30T08:30:00+08:00" --debug
```

重点检查：

- `content/post/<slug>/index.md` 是否正确生成
- `cover.svg` 是否生成
- front matter 是否合法
- 同一天重复运行是否不会追加重复 section

### 4.3 第三层：GitHub Actions 手动调试

本地确认后，再用 GitHub 的 `workflow_dispatch` 手动触发。

第一次上线时建议：

- 先把 schedule 注释掉，只保留手动触发
- workflow 跑通后再打开定时任务

检查重点：

- checkout 后是否有写权限
- Python 依赖是否装得起来
- RSS 拉取是否正常
- commit 步骤是否真的只提交目标内容

## 5. 调试时建议加的参数

建议 `run.py` 支持这些参数：

- `--run-at`
  - 指定模拟运行时间，便于复现实验
- `--dry-run`
  - 只输出结果，不写文件
- `--debug`
  - 打印详细日志
- `--limit-sources`
  - 只跑部分源，便于快速调试
- `--limit-items`
  - 限制每个源读取条数

例如：

```bash
python scripts/tech_weekly/run.py \
  --run-at "2026-03-30T08:30:00+08:00" \
  --limit-sources "OpenAI Blog,GitHub Blog" \
  --limit-items 10 \
  --dry-run \
  --debug
```

## 6. 调试阶段最常见的问题

### 6.1 RSS 发布时间格式不统一

问题：

- 有的 feed 用 RFC822
- 有的用 ISO8601
- 有的甚至没有明确时区

处理：

- 使用稳定的时间解析库
- 解析失败的条目直接跳过并打日志

### 6.2 同一事件没有被聚合

问题：

- 不同媒体标题写法差异很大

处理：

- 先允许保守聚合
- 不强行合并相似度边界不清的事件
- 一周观察后再调阈值

### 6.3 tags 太散

问题：

- 关键词过多导致标签太多

处理：

- 只保留前 2 到 4 个动态标签
- 统一标签字典，避免同义词重复

### 6.4 GitHub Actions 重复提交

问题：

- 同一天重复触发 workflow，导致重复写入

处理：

- 渲染前先检查当天 section 是否已存在
- commit 前检查 staged diff 是否为空

### 6.5 封面每次都重生成

问题：

- 每次运行都覆盖 `cover.svg`

处理：

- 仅在“首次创建周报目录时”生成封面
- 若文件已存在则跳过

## 7. 我建议的上线节奏

最稳的是四阶段上线：

1. 本地跑通 `dry-run`
2. 本地真实写入文章和封面
3. GitHub Actions 手动触发跑通
4. 打开每日 schedule

不要跳步骤。

## 8. 最终执行流程

实际运行顺序建议固定为：

1. 读取配置
2. 计算前一天 `GMT+8` 时间窗口
3. 拉取 RSS
4. 过滤无效条目
5. 执行硬去重
6. 执行事件聚合
7. 执行排序
8. 计算动态 tags
9. 检查本周周报是否存在
10. 不存在则创建目录、生成 `index.md`、生成 `cover.svg`
11. 存在则检查当天 section 是否已存在
12. 如不存在则追加当天 section
13. 更新 front matter
14. 退出并由 GitHub Actions 提交 push

## 9. 下一步实现建议

如果开始写代码，我建议按下面顺序提交：

1. 提交 `sources.yaml` 和基础抓取脚本
2. 提交过滤、去重、聚合逻辑
3. 提交周报渲染和动态 tags
4. 提交自动封面生成
5. 提交 GitHub Actions workflow

这样每一步都可验证，出了问题也容易回退和定位。
