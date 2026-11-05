"""按 style-guide 检查飞书文档 XML（本地草稿或 docs +fetch 回读的线上 XML）。

用法：
    python lint.py 文档.xml [--max-line 30] [--json]

结果分两级：
    错误：违反硬规则，必须改（退出码 1）
    警告：多半要改，但允许有理由地保留

只检查能机械判断的项。“要让读者做到什么”“信息有没有丢”这类判断，仍要人工做。
"""
import argparse
import html
import json
import re
import sys

GREEN = ('green', 'rgb(46,161,33)')
RED = ('red', 'rgb(216,57,49)')
CIRCLED = '①②③④⑤⑥⑦⑧⑨⑩'
EMOJI_RE = re.compile('[\U0001F300-\U0001FAFF☀-➿⬀-⯿]')


def strip_ids(x):
    return re.sub(r' (id|token|seq-marker|creator-id|file-type|title|user-name)="[^"]*"', '', x)


def text_of(x, code_width=None):
    x = re.sub(r'<cite[^>]*/>|<cite[^>]*>.*?</cite>', '＠＠＠＠', x, flags=re.S)
    if code_width is not None:  # 算行长时，行内代码按固定宽度计
        x = re.sub(r'<code>.*?</code>', '＃' * code_width, x, flags=re.S)
    return html.unescape(re.sub(r'<[^>]+>', '', x))


def top_blocks(body):
    """粗略切出顶层块：返回 [(tag, 原文)]。"""
    blocks, i, n = [], 0, len(body)
    while i < n:
        m = re.compile(r'<([a-z0-9_-]+)\b[^>]*?(/?)>').search(body, i)
        if not m:
            break
        t, selfclose = m.group(1), m.group(2) == '/'
        if selfclose or t in ('hr', 'img', 'br'):
            blocks.append((t, m.group(0)))
            i = m.end()
            continue
        depth, j = 0, m.start()
        pat = re.compile(r'<(/?)' + re.escape(t) + r'\b[^>]*?(/?)>')
        for mm in pat.finditer(body, m.start()):
            if mm.group(1):
                depth -= 1
            elif not mm.group(2):
                depth += 1
            if depth == 0:
                j = mm.end()
                break
        blocks.append((t, body[m.start():j]))
        i = j
    return blocks


def lint(xml, max_line=30):
    errs, warns = [], []
    E = lambda code, msg: errs.append((code, msg))
    W = lambda code, msg: warns.append((code, msg))
    xml = strip_ids(xml)
    body = re.sub(r'^\s*<title>.*?</title>', '', xml, flags=re.S).strip()
    blocks = top_blocks(body)
    tags = [t for t, _ in blocks]

    # 标题层级
    if '<h1' in body:
        E('H1', f'出现一级标题 {body.count("<h1")} 处：正文要从二级标题开始')
    for m in re.finditer(r'<(h[2-6])\b[^>]*>(.*?)</\1>', body, flags=re.S):
        inner, t = m.group(2), text_of(m.group(2))
        if EMOJI_RE.search(t):
            W('H-EMOJI', f'标题里有 emoji：{t[:30]}')
        if '<b>' in inner or 'text-color' in inner:
            W('H-STYLE', f'标题加粗或上色：{t[:30]}')

    # 第一屏
    first = next((b for b in blocks if b[0] != 'p' or text_of(b[1]).strip()), None)
    if not first or first[0] != 'callout' or 'emoji="💡"' not in first[1]:
        W('FIRST', '第一个块不是 💡 高亮块：第一屏要写“这页帮你做什么”')
    if blocks and blocks[0][1] == '<p></p>':
        W('FIRST-BLANK', '页面以空行开头：开头的第一个块前不加空行')

    # 高亮块
    emojis = re.findall(r'<callout\b[^>]*emoji="([^"]*)"', body)
    if any(e.startswith('⚠') for e in emojis):
        E('CALLOUT-WARN', '高亮块用了 ⚠️：飞书会把它换成 💡，黄色提醒改用 ❗')
    if emojis.count('💡') > 1:
        W('CALLOUT-BLUE', f'💡 高亮块 {emojis.count("💡")} 个：每页 1 个，只放在第一屏')
    if emojis.count('❗') > 3:
        W('CALLOUT-YELLOW', f'❗ 高亮块 {emojis.count("❗")} 个：每页最多 3 个')
    for e in {e for e in emojis if not e.startswith('⚠')} - {'💡', '❗', '⛔'}:
        W('CALLOUT-OTHER', f'高亮块用了规范外的图标 {e}：只用 💡 ❗ ⛔')

    # 留白：每个 h2 前是 <p></p><hr/>
    for i, t in enumerate(tags):
        if t == 'h2' and i > 0:
            if not (i >= 2 and tags[i - 1] == 'hr' and blocks[i - 2][1] == '<p></p>'):
                h = text_of(blocks[i][1])[:20]
                W('SPACE-H2', f'二级标题“{h}”前缺空行加分割线（跑一遍 spacing.py）')
    for i in range(1, len(blocks)):
        if blocks[i][1] == '<p></p>' and blocks[i - 1][1] == '<p></p>':
            W('SPACE-DOUBLE', '有连续两个空行')
            break

    # 行长：表格、代码块以外的 p/li，按 <br/> 分行
    prose = re.sub(r'<table.*?</table>|<pre.*?</pre>|<whiteboard.*?</whiteboard>', '', body, flags=re.S)
    long_lines = []
    for m in re.finditer(r'<(p|li)\b[^>]*>(.*?)</\1>', prose, flags=re.S):
        if re.search(r'<(p|li|ul|ol)\b', m.group(2)):
            continue
        for seg in re.split(r'<br/?>', m.group(2)):
            s = text_of(seg, code_width=6).strip()
            if len(s) > max_line:
                long_lines.append(text_of(seg).strip())
    for s in long_lines:
        W('LINE', f'超过 {max_line} 字：{s[:40]}…')

    # 带圈数字放进有序列表
    for m in re.finditer(r'<ol\b[^>]*>(.*?)</ol>', body, flags=re.S):
        if re.search(r'<li\b[^>]*>\s*[' + CIRCLED + ']', m.group(1)):
            E('OL-CIRCLED', '有序列表里的项以 ①②③ 开头：飞书会重复编号，改成段落')
            break

    # 表格列数
    for m in re.finditer(r'<table\b.*?</table>', body, flags=re.S):
        cols = len(re.findall(r'<col\b', m.group(0))) or len(re.findall(r'<th\b', m.group(0)))
        if cols > 4:
            W('TABLE-COLS', f'表格 {cols} 列：不超过 4 列')

    # 画板：旁边要有文字说明；Mermaid 里的危险字符
    for i, (t, raw) in enumerate(blocks):
        if t != 'whiteboard':
            continue
        near = []
        if i > 0 and not blocks[i - 1][0].startswith('h'):
            near.append(blocks[i - 1])
        for j in (i + 1, i + 2):  # 往后看两块，遇到标题就停
            if j >= len(blocks) or blocks[j][0].startswith('h'):
                break
            near.append(blocks[j])
        if not any(tt in ('p', 'table', 'ul', 'ol') and text_of(rr).strip() for tt, rr in near):
            W('WB-TEXT', '画板旁边没有文字说明：图不能是唯一的信息来源')
        mm = html.unescape(re.sub(r'<[^>]+>', '', raw))
        if '“' in mm or '”' in mm:
            W('WB-QUOTE', '画板内容里有中文弯引号：可能导致写入失败（2107）')
        if mm.lstrip().startswith('sequenceDiagram') and re.search('[（）]', mm):
            W('WB-PAREN', '时序图里有全角括号：可能导致写入失败（2107）')
        if 'path="@' in raw:
            W('WB-PATH', '画板用 path 引用：偶发写入失败，推荐改成内联转义写法')

    # 文字样式
    if '<em>' in body or '<i>' in body:
        W('ITALIC', '用了斜体：中文斜体显示效果差，不用')
    for c in re.findall(r'text-color="([^"]+)"', body):
        if c not in GREEN + RED:
            W('COLOR', f'用了规范外的字色 {c}：只用绿、红')
    if re.search(r'<span\b[^>]*background-color', body):
        W('BG', '文字用了背景色：不用')

    # 组件
    if '<time' in body:
        W('TIME', '用了时间组件：规范类文档不用')
    tail = text_of(''.join(r for _, r in blocks[-3:]))
    if re.search(r'最后更新|维护[:：]', tail):
        E('FOOTER', '页尾手写了“最后更新／维护人”：飞书顶部本来就显示修改时间，删掉')
    if re.search(r'！！|非常重要', text_of(body)):
        W('TONE', '有“！！”或“非常重要”：危险的地方改用红色或高亮块')

    return errs, warns


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('file')
    ap.add_argument('--max-line', type=int, default=30)
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args()
    with open(a.file, encoding='utf-8') as f:
        errs, warns = lint(f.read(), a.max_line)
    if a.json:
        print(json.dumps({'errors': errs, 'warnings': warns}, ensure_ascii=False, indent=1))
    else:
        for c, m in errs:
            print(f'错误 [{c}] {m}')
        for c, m in warns:
            print(f'警告 [{c}] {m}')
        print(f'— {len(errs)} 个错误，{len(warns)} 个警告')
    return 1 if errs else 0


if __name__ == '__main__':
    sys.exit(main())
