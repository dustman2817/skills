---
name: lark-doc-design
description: 飞书云文档／知识库页面的写作与排版规范：先定表达再选形式、版式记号（高亮块、颜色、加粗）、留白、截图与画板、@人和@文档，附留白脚本和发布前 lint。写新飞书文档、重排或改写已有飞书文档、给团队写规范／操作说明／排障页时使用。只管“写成什么样”，飞书读写命令本身走 lark-doc。
---

# 飞书文档设计规范

团队内部规范、操作说明、规则查询类飞书文档按这套规范写。对外文档、汇报材料和幻灯片不适用。

- 规范全文：[references/style-guide.md](references/style-guide.md)（唯一权威源）
- 已实测的 XML 写法和已知的坑：[references/xml-cookbook.md](references/xml-cookbook.md)
- 改写例子：[references/examples.md](references/examples.md)
- 读写飞书文档的命令、参数：用 lark-doc 技能，本技能不重复。

## 工作流程

不能跳步。

1. **定读者和类型。** 先回答：这篇给谁看、读者什么时候打开它、这个话题别处写过没有。再按 style-guide 第 3 节选类型、套骨架。写过的话题只写一句话加链接。
2. **按节定表达。** 每一节写两句话：“读者要做到什么”“只看文字会卡在哪”。再按 style-guide 第 1 节的对照表选形式。说不出解决了哪个卡点的组件，就不用。
3. **写草稿 XML。** 按 style-guide 第 4～8 节的版式记号来写，XML 写法查 xml-cookbook。
4. **加留白。** 运行 `scripts/spacing.py`，不要手工加空行。
5. **跑 lint。** 运行 `scripts/lint.py`。有错误必须改完；有警告的，逐条判断是否合理，不合理的改掉。
6. **改写已有文档时，核对信息有没有丢。** 原文的每一条规则都要能在新版里找到。图里放不下的，补在图下面的文字里。不要趁重排的机会改规则。
7. **发到验证位置。** 新结构或大改动，先发到用户的个人云空间给用户看，用户确认后再改线上文档。
8. **回读。** 回读检查：标题不变、正文和草稿逐行一致。有画板的，导出缩略图看一遍，看有没有文字截断、标签重叠。

## 命令

```
# Git Bash / PowerShell 均可（Python 3）
python scripts/spacing.py draft-raw.xml draft.xml
python scripts/lint.py draft.xml
python scripts/lint.py fetched.xml --fetched    # 回读的线上 XML（带 id 属性）也能查
```

## 硬约束（来自用户的长期要求）

- 改已有文档：先读远端当前标题，只改正文，不碰标题。用户改过的标题不能被顶回去。
- 新写的文字发布前，用 humanizer-zh 过一遍。
- 页尾不写“最后更新／维护人”：飞书页面顶部本来就显示修改时间。
- 不用时间组件、倒计时。
- 用工具写入的 @人 实测不会通知对方，可以用。同名的人先按部门核对 open_id。
