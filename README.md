# skills

dustman2817 的 Agent 技能合集。每个技能一个目录，可以通过 CC Switch 订阅，也可以手动复制安装。

## 技能清单

| 技能 | 用途 | 版本 |
|---|---|---|
| [lark-doc-design](skills/lark-doc-design/) | 飞书云文档／知识库页面的写作与排版规范：先想清楚要表达什么，再选形式；包含留白脚本和发布前 lint | v0.3 |

## 安装

**CC Switch**：在“Skills → 发现 → 管理技能仓库”里添加 `dustman2817/skills`，分支选 `main`，然后在发现列表里按需安装。

**手动**：把 `skills/<技能名>/` 整个目录复制到 `%USERPROFILE%\.claude\skills\<技能名>\`。

## 目录约定

```
skills/
  <技能名>/
    SKILL.md        必需。frontmatter 里的 name 和目录名保持一致
    references/     可选。参考文档
    scripts/        可选。脚本
    tests/          可选。回归样例
    CHANGELOG.md    建议。每个技能自己记版本
```

- **根目录不放 `SKILL.md`**：CC Switch 扫描时，遇到含 `SKILL.md` 的目录就把它当成一个技能，不再往下找。根目录如果有 `SKILL.md`，整个仓库会被当成一个技能。
- **每个技能自包含**：安装时只会复制这个技能的目录，所以不要引用合集根目录或其他技能里的文件。
- **加新技能**：新建一个 `skills/<技能名>/`，在上面的技能清单里加一行。
- **只放通用内容**：仓库是公开的。项目专属的人名、账号、内部链接、业务名称不要放进来。
