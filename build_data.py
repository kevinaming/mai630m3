"""Builds data.js from the speaker notes of the Module 3 deck (English): every slide, split into parts at each class cover.
Run: python3 build_data.py   (the page's script tag gets a version, so browsers load the new speech right away)"""
import hashlib, html, json, os, re, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
DECK = os.path.join(HERE, "../../../Modulo 3/Slides/MAI630_Module3_Class_en.pptx")

z = zipfile.ZipFile(DECK)
rels = {re.search(r'Id="([^"]+)"', r).group(1): re.search(r'Target="([^"]+)"', r).group(1)
        for r in re.findall(r"<Relationship [^>]*/>", z.read("ppt/_rels/presentation.xml.rels").decode())}
order = [rels[r] for r in re.findall(r'<p:sldId [^>]*r:id="([^"]+)"', z.read("ppt/presentation.xml").decode())]

def paras(x):
    out = []
    for p in re.findall(r"<a:p\b[^>]*>(.*?)</a:p>", x, re.S):
        t = html.unescape("".join(re.findall(r"<a:t(?: [^>]*)?>([^<]*)</a:t>", p))).strip()
        if t: out.append(t)
    return out

def clean(notes):
    """What is read: without the reminders for the presenter (▶ ON THE PC, (When you come back.))."""
    out = []
    for p in notes:
        if p.startswith("▶"): continue
        p = re.sub(r"^\(When you come back\.\)\s*", "", p).strip()
        if p: out.append(p)
    return out

SEP = {"/": " slash ", "_": " underscore ", ".": " dot ", "-": " dash "}
PIECE = {"src": "source", "py": "pie", "md": "M D", "pt": "P T", "cnn": "C N N", "ipynb": "I P Y N B", "yaml": "yaml", "csv": "C S V",
         "claude": "Claude", "CLAUDE": "Claude", "LOG": "log", "png": "P N G", "json": "J S O N", "app": "app"}
def spoken_name(tok):
    out = ""
    for part in re.split(r"([/_.\-])", tok):
        if part in SEP: out += SEP[part]
        elif part: out += PIECE.get(part, part)
    return re.sub(r"\s+", " ", out).strip()

slides, parts, names = [], [], set()
for n in range(1, len(order) + 1):
    path = "ppt/" + order[n - 1]
    texts = paras(z.read(path).decode())
    r = z.read(path.replace("slides/", "slides/_rels/") + ".rels").decode()
    m = re.search(r'Target="\.\./notesSlides/([^"]+)"', r)
    notes = []
    if m:
        nx = z.read("ppt/notesSlides/" + m.group(1)).decode()
        for sp in re.findall(r"<p:sp>.*?</p:sp>", nx, re.S):
            if 'type="body"' in sp: notes += paras(sp)
    cover = len(texts) > 2 and texts[2].startswith("Prof.")
    if cover:  # a class cover starts a new part: "Building the" + "Training Page", "MAI 630 · Module 3 · Class 3.1"
        cls = (re.search(r"Class\s+([\d.]+)", " ".join(texts)) or [None, ""])[1]
        parts.append({"p": len(parts) + 1, "cls": cls, "title": texts[0] + " " + texts[1]})
    if texts and texts[0] == "ATLANTIS UNIVERSITY" and len(texts) > 3: title = texts[3]
    elif cover: title = texts[0] + " " + texts[1]
    elif texts: title = texts[0]
    else: title = f"Slide {n}"
    ps = clean(notes)
    if not ps: continue  # a slide with nothing to read (the blank one between the classes)
    if not parts: parts.append({"p": 1, "cls": "", "title": ""})
    slides.append({"n": n, "part": len(parts), "title": title, "paras": ps})
    for p in ps:
        for tok in re.findall(r"[\w.<>/\-]*[\w>](?:[/_.][\w.<>/\-]*[\w>])+|\.[a-z]+/[a-z]+|\.gitignore", re.sub(r"\([^()]*\d[^()]*\)|^\d+\.\s", "", p)):
            if not re.fullmatch(r"[\d./,]+", tok) and not re.fullmatch(r"[A-Z]\.", tok): names.add(tok)

for pt in parts:
    ns = [s["n"] for s in slides if s["part"] == pt["p"]]
    pt["first"], pt["last"], pt["count"] = ns[0], ns[-1], len(ns)
spoken = {t: spoken_name(t) for t in sorted(names)}
spoken.update({"mAP": "M A P", "imgsz": "image size", ".gitignore": "dot git ignore"})

body = ("window.PARTS = " + json.dumps(parts, ensure_ascii=False) + ";\nwindow.SLIDES = " + json.dumps(slides, ensure_ascii=False)
        + ";\nwindow.SPOKEN = " + json.dumps(spoken, ensure_ascii=False, indent=0) + ";\n")
open(os.path.join(HERE, "data.js"), "w").write(body)
digest = hashlib.sha1(body.encode()).hexdigest()[:8]
page = os.path.join(HERE, "index.html")
src = open(page).read()
new = re.sub(r'<script src="data\.js(\?v=[0-9a-f]+)?"></script>', f'<script src="data.js?v={digest}"></script>', src)
if new != src: open(page, "w").write(new)
print(f"{len(slides)} slides in {len(parts)} parts:", ", ".join(f"Part {p['p']} (Class {p['cls']}) slides {p['first']}-{p['last']}" for p in parts))
