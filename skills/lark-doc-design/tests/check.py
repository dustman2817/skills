"""回归检查：bad.xml 每条规则都要报出来，good.xml 不能有错误。"""
import json, subprocess, sys, os
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
here = os.path.dirname(os.path.abspath(__file__))
lint = os.path.join(here, '..', 'scripts', 'lint.py')
def run(f):
    r = subprocess.run([sys.executable, '-I', lint, os.path.join(here, f), '--json'], capture_output=True)
    d = json.loads(r.stdout.decode('utf-8'))
    return {c for c, _ in d['errors']}, {c for c, _ in d['warnings']}
want = {'H1','H-EMOJI','FIRST','FIRST-BLANK','CALLOUT-WARN','CALLOUT-BLUE','CALLOUT-OTHER','SPACE-H2','SPACE-DOUBLE',
        'LINE','OL-CIRCLED','TABLE-COLS','WB-TEXT','WB-QUOTE','WB-PAREN','ITALIC','COLOR','BG','TIME','FOOTER','TONE'}
e, w = run('bad.xml'); got = e | w
ge, gw = run('good.xml')
ok = want <= got and not ge and not gw
print('bad 漏报:', sorted(want - got) or '无', '| good 错误:', sorted(ge) or '无', '| good 警告:', sorted(gw) or '无')
print('通过' if ok else '失败'); sys.exit(0 if ok else 1)
