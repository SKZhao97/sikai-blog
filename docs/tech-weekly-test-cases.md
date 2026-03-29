# 科技周报测试用例

## 目标

验证两个关键行为：

1. 同一周的第二天运行时，会向同一篇周报追加内容
2. 下一周开始时，会新建一篇新的周报文章

## 前置条件

- 已安装依赖：`pip3 install -r scripts/tech_weekly/requirements.txt`
- 使用 `--force-rewrite-date` 便于重复验证
- 优先使用“已经过去且新闻源确实有数据”的日期做测试，不要把未来窗口作为主要验证样本

## Case 1：第二天追加内容

### 场景

- 第一次运行时间：`2026-03-29T08:30:00+08:00`
- 第二次运行时间：`2026-03-30T08:30:00+08:00`

根据当前规则：

- 第一次抓取窗口：`2026-03-28 08:30` 到 `2026-03-29 08:30`
- 第二次抓取窗口：`2026-03-29 08:30` 到 `2026-03-30 08:30`

两次运行都应写入同一篇周报：

- `content/post/2026-w13-tech-weekly/index.md`

### 本地测试命令

```bash
python3 -m scripts.tech_weekly.run --run-at "2026-03-29T08:30:00+08:00" --force-rewrite-date --debug
python3 -m scripts.tech_weekly.run --run-at "2026-03-30T08:30:00+08:00" --force-rewrite-date --debug
```

### 预期结果

- 周报目录仍然是 `2026-w13-tech-weekly`
- `index.md` 中包含两个 section：
  - `## 2026-03-29`
  - `## 2026-03-30`
- `cover.svg` 不应重复生成

## Case 2：下一周新建新文章

### 场景

- 上一周运行时间：`2026-03-30T08:30:00+08:00`
- 下一周运行时间：`2026-04-06T08:30:00+08:00`

如果第二次运行已跨入新的 ISO 周，则应创建新的文章目录。

### 本地测试命令

```bash
python3 -m scripts.tech_weekly.run --run-at "2026-03-30T08:30:00+08:00" --force-rewrite-date --min-events 1 --debug
python3 -m scripts.tech_weekly.run --run-at "2026-04-06T08:30:00+08:00" --force-rewrite-date --min-events 1 --debug
```

### 预期结果

- 第一篇文章：
  - `content/post/2026-w13-tech-weekly/index.md`
- 第二篇文章：
  - `content/post/2026-w14-tech-weekly/index.md`

也就是说：

- 同周追加
- 跨周新建

## GitHub Actions 手动测试

现在 workflow 已支持手动输入：

- `run_at`
- `dry_run`
- `min_events`
- `force_rewrite_date`

你可以在 GitHub Actions 页面分别手动运行这两个时间点来验证相同行为，而不必依赖当天真实时间。
