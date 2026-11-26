import sys, re
from pypdf import PdfReader
r = PdfReader(sys.argv[1])
pats = sys.argv[2:]
for i, p in enumerate(r.pages):
    t = re.sub(r"\s+", " ", p.extract_text() or "")
    for pat in pats:
        for m in re.finditer(pat, t, re.I):
            print(f"p{i+1} [{pat}]: ...{t[max(0,m.start()-120):m.end()+160]}...")
