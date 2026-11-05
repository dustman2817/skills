# lark-doc-design

> 属于 [dustman2817/skills](../../README.md) 技能合集。

飞书云文档／知识库页面的写作与排版规范，打包成一个 Agent 技能（Skill）：一份规范、两个脚本、一组回归样例。

目标：任何会话、任何 Agent 写飞书文档时，都按同一套规范来写，并且有脚本兜底检查。

## 目录

```
SKILL.md                    技能入口：触发说明 + 工作流程 + 硬约束
references/
  style-guide.md            规范全文（唯一权威源）
  xml-cookbook.md           已实测的 XML 写法、组件可用性、已知的坑
  examples.md               改写例子
scripts/
  spacing.py                自动加留白（重复运行结果不变）
  lint.py                   发布前检查：错误必须改，警告逐条判断
tests/
  bad.xml / good.xml        回归样例
  check.py                  回归检查：bad 的每条规则都要被报出来，good 不能有错误和警告
CHANGELOG.md                规范变更记录
```

## 用法

```
# Git Bash 或 PowerShell（需要 Python 3）
python scripts/spacing.py draft-raw.xml draft.xml
python scripts/lint.py draft.xml
python scripts/lint.py fetched.xml --json
python tests/check.py
```

`lint.py` 能直接检查 `lark-cli docs +fetch` 回读的线上 XML（带 id 属性也可以）。

## 安装

- **CC Switch**：在“Skills → 发现 → 管理技能仓库”添加 `dustman2817/skills`（分支 `main`），在发现列表里找到 `lark-doc-design` 安装。
- **手动**：把 `skills/lark-doc-design/` 整个目录复制到 `%USERPROFILE%\.claude\skills\lark-doc-design\`。
- **其他读 AGENTS.md 的 Agent**：在 AGENTS.md 里加一行指针：
  > 写或改飞书云文档前，先读 `<安装路径>/lark-doc-design/SKILL.md`，按其中的流程和 references 执行；发布前运行 `scripts/lint.py`。

装好后，开一个新对话让它写一页飞书文档，检查它是否按本技能执行、能否通过 lint。

## 维护规则

- 规范只在 `references/style-guide.md` 里改。改完在 `CHANGELOG.md` 记一条，再同步到飞书镜像。
- 新踩到的坑写进 `xml-cookbook.md`。能机械判断的，同时在 `lint.py` 里加一条检查，在 `tests/bad.xml` 里加一个反例，然后跑 `tests/check.py`。
- 只放通用规则。项目专属的内容（人员 open_id、具体页面清单、业务术语）留在各自项目里。
