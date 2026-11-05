"""按 style-guide 第 5 节给飞书文档 XML 草稿加留白。

用法：
    python spacing.py 输入.xml 输出.xml [--title 新标题]

输入约定：每个顶层块一行（多行写的表格会先并成一行）。
已经加过留白的文件再跑一次，结果不变。
"""
import argparse
import re
import sys

BLANK = '<p></p>'


def tag(line):
    m = re.match(r'<([a-z0-9_-]+)', line)
    return m.group(1) if m else ''


def space(xml, title=None):
    xml = re.sub(r'\n(?=<(?:tr|/tbody|/table))', '', xml)
    lines = [l for l in xml.split('\n') if l.strip()]
    # 先去掉已有的空段和分割线，保证重复运行结果一致
    lines = [l for l in lines if l.strip() not in (BLANK, '<hr/>')]
    if title is not None and lines and lines[0].startswith('<title'):
        lines[0] = re.sub(r'<title>.*?</title>', f'<title>{title}</title>', lines[0])
    out = []
    body_started = False
    for l in lines:
        t = tag(l)
        if t == 'title':
            out.append(l)
            continue
        prev = tag(out[-1]) if out else ''
        if t == 'h2':
            if body_started:
                out += [BLANK, '<hr/>']
        elif body_started and (
            (t in ('img', 'grid') and prev in ('ol', 'ul'))
            or prev in ('img', 'grid')
            or t in ('callout', 'button')
            or (prev == 'callout' and t != 'h2')
        ):
            if prev not in ('h2', 'h3') and out[-1] != BLANK:
                out.append(BLANK)
        out.append(l)
        body_started = True
    return '\n'.join(out) + '\n'


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('src')
    ap.add_argument('dst')
    ap.add_argument('--title', default=None)
    a = ap.parse_args()
    with open(a.src, encoding='utf-8') as f:
        result = space(f.read(), a.title)
    with open(a.dst, 'w', encoding='utf-8', newline='\n') as f:
        f.write(result)
    return 0


if __name__ == '__main__':
    sys.exit(main())
