# 飞书 XML 写法和已知的坑

配合 lark-cli（`docs +create`／`docs +update`／`docs +fetch`）使用。标签的完整语法以 lark-doc 技能的 `lark-doc-xml.md` 为准，本页只记已在样张和线上文档里实测过的写法，以及踩过的坑。

## 已实测的写法

| 样式 | XML 或命令 |
|---|---|
| 蓝色提示 | `<callout emoji="💡" background-color="light-blue" border-color="blue">` |
| 黄色提醒 | `<callout emoji="❗" background-color="light-yellow" border-color="yellow">` |
| 红色警告 | `<callout emoji="⛔" background-color="light-red" border-color="red">` |
| 绿字、红字 | `<span text-color="green">`、`<span text-color="red">` |
| 行内代码、行内换行 | `<code>…</code>`、`<br/>`（列表项里也能用） |
| 空行 + 分割线 | `<p></p><hr/>` |
| 两栏、三栏 | `<grid><column width-ratio="0.5">…</column><column width-ratio="0.5">…</column></grid>`（三栏用 0.34 / 0.33 / 0.33） |
| 流程图（推荐写法） | `<whiteboard type="mermaid">转义后的 Mermaid 内容</whiteboard>` |
| 流程图（path 写法） | `<whiteboard type="mermaid" path="@./flow.mmd"></whiteboard>`（偶尔会写入失败，见下文） |
| 改已有画板 | `whiteboard +update --whiteboard-token <token> --input_format mermaid --source @./flow.mmd --overwrite`（不要新建空白画板） |
| 导出画板缩略图 | `docs +media-download --type whiteboard --token <token> --output ./wb` |
| 按钮 | `<button action="OpenLink" src="URL" background-color="blue">文字</button>` |
| @文档 | `<cite type="doc" doc-id="文档 obj token"/>` |
| @人 | `<cite type="user" user-id="open_id"/>` |
| 复制已有图片 | `<img src="已有图片 token" caption="…"/>` |
| 本地图片 | `<img path="@./img/x.png" caption="…"/>` |
| 参考页自动编号 | `<h2 seq="auto">…</h2>`、`<h3 seq="auto">…</h3>` |
| 回读带样式 | `docs +fetch --detail full`（默认模式下看不到颜色和高亮块样式） |

## 哪些组件能用工具写入

| 状态 | 组件 |
|---|---|
| 实测写入成功 | 图片、分栏（两栏、三栏）、高亮块、按钮、画板（Mermaid 流程图、时序图）、引用、代码、表格、@文档、@人、分割线 |
| 文档写了支持，还没实测 | 任务、电子表格、群名片、HTML 块、网页卡片、目标、子页面列表、附件、思维导图（用 Mermaid 写进画板） |
| 只能手动（工具文档没写到） | 同步块、目录导航、时间轴、多维表格、投票、信息收集、日程、会议议程、文本绘图、内嵌网页 |

## 已知的坑

| 现象 | 原因或应对 |
|---|---|
| 高亮块写了 ⚠️，显示成 💡 | ⚠️ 不受支持，会被悄悄替换，接口也不报错。黄色提醒改用 ❗ |
| 画板写入时报 `degrade_code=2107` | 用 path 引用时偶发。改成内联写法：把 Mermaid 内容转义（`&lt;` `&gt;` `&amp;`）后直接写进标签里 |
| 内联写法也报 2107 | Mermaid 标签里有中文弯引号“”，或者时序图消息里有全角括号（）。去掉这些字符 |
| 判断框文字被截断 | 框里字太多。缩短到 8 个字以内，补充说明挪到图下面 |
| 两条线的标签叠在一起 | 两个节点之间画了来回两条线。中间加一个节点拆开 |
| ①②③ 前面又多出 1. 2. 3. | 把带圈数字放进了有序列表。改成段落 |
| 默认模式回读，看不到颜色和高亮块 | 用 `--detail full` |
| 颜色写的是名字，回读变成 RGB | 正常现象：`green` 会变成 `rgb(46,161,33)`，`red` 会变成 `rgb(216,57,49)` |
| `block_replace` 之后，原 block id 失效 | 改完要重新 fetch，再取新的 id |
| 改已有文档时把用户改过的标题顶回去了 | 不要整篇 overwrite。用 `block_replace`，范围从第一个正文块到 `-1`；或者用 `str_replace` 做局部替换 |
| Windows 下 subprocess 读 lark-cli 输出，报 UnicodeDecodeError | 用 `capture_output=True` 取字节，再 `.decode('utf-8','replace')` |

## 整篇换正文、标题不动

```
# 1. 取第一个正文块的 id（紧跟在 <title> 之后的那个块）
lark-cli docs +fetch --as user --doc <obj> --detail with-ids --format json
# 2. 从这个块一直替换到文末
lark-cli docs +update --as user --doc <obj> --command block_replace --start-block-id <first> --end-block-id -1 --content @./body.xml --format json
# 3. 回读核对：标题不变，正文和 body.xml 逐行一致
```

body.xml 里不能带 `<title>`。

## @人 怎么取 open_id

```
lark-cli contact +search-user --query 姓名 --as user --format json
lark-cli contact +search-user --user-ids <open_id> --as user --format json   # 反查部门，确认没选错同名的人
```
