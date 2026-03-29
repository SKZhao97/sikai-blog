# GitHub Actions 配置清单：科技周报自动更新

## 1. 当前状态

仓库里的 workflow 目前已经调整为“手动触发调试版”：

- 文件：`.github/workflows/daily-tech-weekly.yml`
- 当前只开启：`workflow_dispatch`
- 当前未开启：`schedule`

这样做的目的是先在 GitHub Actions 环境里把抓取、生成、提交整条链路跑通，再决定是否开启每天自动执行。

## 2. 需要确认的 GitHub 仓库设置

### 2.1 Actions 权限

进入：

- `GitHub 仓库`
- `Settings`
- `Actions`
- `General`

确认以下设置：

- `Actions permissions`
  - 选 `Allow all actions and reusable workflows`
  - 或至少允许官方 `actions/*`

- `Workflow permissions`
  - 选 `Read and write permissions`

原因：

- 这个 workflow 需要 `git commit` 和 `git push`
- 如果只给只读权限，最后一步会失败

### 2.2 默认分支

确认 workflow 提交的目标分支就是你的发布分支，通常是：

- `main`

进入：

- `Settings`
- `Branches`

检查默认分支是否正确。

### 2.3 分支保护规则

如果你给 `main` 配了 branch protection，需要确认以下一点：

- GitHub Actions bot 是否允许直接 push

否则 workflow 虽然能生成文章，但 push 会被拒绝。

如果当前有严格保护规则，有两种处理方式：

1. 临时放开，允许 Actions 直接提交
2. 后续改成提 PR，而不是直接 push

第一版建议先用直接 push，先把链路跑通。

## 3. 如何手动测试

### 3.1 提交代码到 GitHub

先把本地改动 push 到仓库。

### 3.2 进入 Actions 页面

进入：

- `GitHub 仓库`
- `Actions`
- 选择 `Daily Tech Weekly`

### 3.3 手动触发

点击：

- `Run workflow`

如果后续你想加参数化触发，再扩展 `workflow_dispatch.inputs`；目前第一版直接用默认脚本执行即可。

## 4. 手动测试时重点检查什么

第一次手动跑，重点看 4 件事：

### 4.1 依赖安装是否正常

检查：

- `pip install -r scripts/tech_weekly/requirements.txt`

是否成功。

### 4.2 RSS 抓取是否正常

检查日志中是否出现类似：

- `Fetched 20 entries from TechCrunch`
- `Fetched 15 entries from OpenAI Blog`

如果大部分源都为 0 或报错，再回头调抓取层。

### 4.3 生成文件是否正确

检查 workflow 日志里的输出路径，确认生成了：

- `content/post/<slug>/index.md`
- `content/post/<slug>/cover.svg`

### 4.4 commit 范围是否正确

当前 workflow 里是：

```bash
git add content/post
```

所以理论上只会提交：

- `content/post/...`

要确认不会把 `public/` 或别的文件误带进去。

## 5. 如果手动测试失败，先看哪里

按这个顺序查：

1. `Install dependencies`
2. `Run updater`
3. `Commit changes`

最常见问题：

- Python 依赖没装好
- RSS 网络或解析异常
- 分支写权限不足
- 工作流生成了内容，但没有 diff 可提交

## 6. 手动测试通过后，怎么切到定时执行

等你确认手动跑稳定后，再把 workflow 改回定时版：

```yaml
on:
  schedule:
    - cron: '30 0 * * *'
  workflow_dispatch:
```

解释：

- `00:30 UTC = 08:30 GMT+8`

建议保留 `workflow_dispatch`，这样以后出问题还能手动补跑。

## 7. 推荐上线节奏

建议按这个顺序：

1. 本地调试脚本
2. 提交到 GitHub
3. 手动跑 Actions
4. 检查生成内容和 push 结果
5. 观察 2 到 3 次手动运行
6. 再开启 `schedule`

不要直接跳到自动定时。

## 8. 当前你最需要做的事

1. 把本地改动提交并 push
2. 在 GitHub 仓库里确认 `Workflow permissions = Read and write`
3. 手动运行一次 `Daily Tech Weekly`
4. 检查生成的 commit 和 Netlify 发布结果

这四步都通过后，再开每日定时。
