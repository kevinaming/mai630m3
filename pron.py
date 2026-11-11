"""Pronunciation of the words in the speech: a respelling to read aloud (pə-RAM-ih-terz) and IPA (/pəˈræmɪtərz/).
Source: the CMU Pronouncing Dictionary (cmudict.dict, see CMUDICT-LICENSE.txt), plus the course's own words in MANUAL."""
import os, re

HERE = os.path.dirname(os.path.abspath(__file__))
VOWELS = {"AA", "AE", "AH", "AO", "AW", "AY", "EH", "ER", "EY", "IH", "IY", "OW", "OY", "UH", "UW"}
# respelling: how each sound is written so it can be read like English
RESP = {"AA": "ah", "AE": "a", "AH": "uh", "AO": "aw", "AW": "ow", "AY": "eye", "EH": "eh", "ER": "ur", "EY": "ay", "IH": "ih",
        "IY": "ee", "OW": "oh", "OY": "oy", "UH": "uu", "UW": "oo",
        "B": "b", "CH": "ch", "D": "d", "DH": "th", "F": "f", "G": "g", "HH": "h", "JH": "j", "K": "k", "L": "l", "M": "m", "N": "n",
        "NG": "ng", "P": "p", "R": "r", "S": "s", "SH": "sh", "T": "t", "TH": "th", "V": "v", "W": "w", "Y": "y", "Z": "z", "ZH": "zh"}
IPA = {"AA": "ɑ", "AE": "æ", "AH": "ʌ", "AO": "ɔ", "AW": "aʊ", "AY": "aɪ", "EH": "ɛ", "ER": "ɝ", "EY": "eɪ", "IH": "ɪ", "IY": "i",
       "OW": "oʊ", "OY": "ɔɪ", "UH": "ʊ", "UW": "u",
       "B": "b", "CH": "tʃ", "D": "d", "DH": "ð", "F": "f", "G": "ɡ", "HH": "h", "JH": "dʒ", "K": "k", "L": "l", "M": "m", "N": "n",
       "NG": "ŋ", "P": "p", "R": "r", "S": "s", "SH": "ʃ", "T": "t", "TH": "θ", "V": "v", "W": "w", "Y": "j", "Z": "z", "ZH": "ʒ"}
ONSETS = {("P", "L"), ("P", "R"), ("B", "L"), ("B", "R"), ("T", "R"), ("D", "R"), ("K", "L"), ("K", "R"), ("G", "L"), ("G", "R"),
          ("F", "L"), ("F", "R"), ("S", "L"), ("S", "M"), ("S", "N"), ("S", "P"), ("S", "T"), ("S", "K"), ("S", "W"), ("T", "W"),
          ("K", "W"), ("SH", "R"), ("TH", "R"), ("P", "Y"), ("B", "Y"), ("K", "Y"), ("F", "Y"), ("M", "Y"), ("V", "Y"), ("HH", "Y"),
          ("S", "P", "L"), ("S", "P", "R"), ("S", "T", "R"), ("S", "K", "R"), ("S", "K", "W")}
SHORT = {"AE", "EH", "IH", "UH", "AH"}  # a stressed short vowel keeps the next sound: RAM-ih, not RA-mih

# Words of the course that the dictionary doesn't have, as phonemes (ARPAbet with stress).
MANUAL = {
    "yolo": "Y OW1 L OW0", "iou": "AY1 OW1 Y UW1", "resnet": "R EH1 Z N EH2 T", "imagenet": "IH1 M IH0 JH N EH2 T",
    "pytorch": "P AY1 T AO2 R CH", "opencv": "OW1 P AH0 N S IY1 V IY1", "ultralytics": "AH2 L T R AH0 L IH1 T IH0 K S",
    "kaggle": "K AE1 G AH0 L", "cvat": "S IY1 V AE2 T", "subagent": "S AH1 B EY2 JH AH0 N T", "subagents": "S AH1 B EY2 JH AH0 N T S",
    "overfitting": "OW2 V ER0 F IH1 T IH0 NG", "underfitting": "AH2 N D ER0 F IH1 T IH0 NG", "softmax": "S AO1 F T M AE2 K S",
    "dataset": "D EY1 T AH0 S EH2 T", "datasets": "D EY1 T AH0 S EH2 T S", "checkbox": "CH EH1 K B AA2 K S",
    "hyperparameter": "HH AY2 P ER0 P ER0 AE1 M AH0 T ER0", "hyperparameters": "HH AY2 P ER0 P ER0 AE1 M AH0 T ER0 Z",
    "imgsz": "IH1 M IH0 JH S AY2 Z", "coco": "K OW1 K OW0", "github": "G IH1 T HH AH2 B", "gpu": "JH IY1 P IY1 Y UW1",
    "cpu": "S IY1 P IY1 Y UW1", "mps": "EH1 M P IY1 EH1 S", "json": "JH EY1 S AA0 N", "csv": "S IY1 EH1 S V IY1",
    "readme": "R IY1 D M IY0", "py": "P AY1", "pt": "P IY1 T IY1", "src": "S AO1 R S", "yaml": "Y AE1 M AH0 L", "repo": "R IY1 P OW0", "workflow": "W ER1 K F L OW2", "screenshot": "S K R IY1 N SH AA2 T",
}
# Words whose capitals change how they're said (mAP is "M A P", not "map").
CASED = {"mAP": "EH1 M EY1 P IY1", "IoU": "AY1 OW1 Y UW1"}
LETTER = {"a": "EY1", "b": "B IY1", "c": "S IY1", "d": "D IY1", "e": "IY1", "f": "EH1 F", "g": "JH IY1", "h": "EY1 CH", "i": "AY1",
          "j": "JH EY1", "k": "K EY1", "l": "EH1 L", "m": "EH1 M", "n": "EH1 N", "o": "OW1", "p": "P IY1", "q": "K Y UW1", "r": "AA1 R",
          "s": "EH1 S", "t": "T IY1", "u": "Y UW1", "v": "V IY1", "w": "D AH1 B AH0 L Y UW0", "x": "EH1 K S", "y": "W AY1", "z": "Z IY1"}

_dict = None
def cmu():
    global _dict
    if _dict is None:
        _dict = {}
        with open(os.path.join(HERE, "cmudict.dict"), encoding="utf-8") as f:
            for line in f:
                line = line.split("#")[0].strip()
                if not line: continue
                w, ph = line.split(" ", 1)
                if "(" in w: continue  # keep the first (most common) pronunciation
                _dict[w] = ph
    return _dict

def syllables(ph):
    """Phonemes -> syllables [(sounds, stress)] by the largest onset English allows."""
    toks = ph.split()
    nuc = [i for i, t in enumerate(toks) if t[:2] in VOWELS and t[-1].isdigit()]
    if not nuc: return [(toks, 0)]
    cuts = []
    for a, b in zip(nuc, nuc[1:]):
        cons = [t for t in toks[a + 1:b]]
        n = len(cons)
        if n == 0: cut = b
        elif n == 1:
            v, stress = toks[a][:2], toks[a][-1]
            cut = b if (v in SHORT and stress == "1") else a + 1
        else:
            keep = 1
            for k in (3, 2):
                if k <= n and tuple(cons[n - k:]) in ONSETS: keep = k; break
            cut = b - keep
        cuts.append(cut)
    bounds = [0] + cuts + [len(toks)]
    out = []
    for s, e in zip(bounds, bounds[1:]):
        part = toks[s:e]
        st = next((int(t[-1]) for t in part if t[-1].isdigit() and t[:2] in VOWELS), 0)
        out.append(([t.rstrip("012") for t in part], st, [t for t in part]))
    return [(p, st) for p, st, _ in out]

CLOSED = {"AE": "a", "EH": "e", "IH": "i", "AA": "o", "UH": "uu"}   # a short vowel before a consonant in its syllable: STRENGKTH, not STREHNGKTH
WITH_R = {"AA": "ar", "AO": "or", "EH": "air", "EY": "air", "IH": "eer", "IY": "eer", "UH": "oor", "UW": "oor", "AY": "ire", "AW": "owr", "OW": "or"}

def respell(ph):
    toks = ph.split(); out = []
    for sounds, st in syllables(ph):
        k = len(sounds); part = toks[:k]; toks = toks[k:]
        rest_after = toks  # what comes after this syllable
        s, j = "", 0
        while j < len(part):
            t = part[j]; base = t.rstrip("012"); d = t[-1] if t[-1].isdigit() else ""
            if base in VOWELS:
                nxt = part[j + 1].rstrip("012") if j + 1 < len(part) else None
                if nxt == "R" and base in WITH_R and not (j + 2 == len(part) and rest_after and rest_after[0][:2] in VOWELS):
                    s += WITH_R[base]; j += 2; continue
                closed = any(x.rstrip("012") not in VOWELS for x in part[j + 1:])
                if base == "ER": s += "ur" if d in ("1", "2") else "er"
                elif base == "AH" and d in ("1", "2"): s += "u" if closed else "uh"
                elif closed and base in CLOSED: s += CLOSED[base]
                elif base == "AY" and j > 0:  # after a consonant: HY-POTH-uh-sis, LYKE, KYND
                    tail = [x.rstrip("012") for x in part[j + 1:]]
                    s += "y" + "".join(RESP[x] for x in tail) + ("e" if len(tail) == 1 else ""); j = len(part); continue
                else: s += RESP[base]
            else:
                s += RESP[base]
            j += 1
        out.append(s.upper() if st == 1 else s)
    return "-".join(out)

def ipa(ph):
    out = ""
    for sounds, st in syllables(ph):
        raw = ph  # stress-aware vowels: unstressed AH -> ə, unstressed ER -> ər
        s = ""
        for x in sounds: s += IPA[x]
        out += ("ˈ" if st == 1 else "ˌ" if st == 2 else "") + s
    return "/" + out + "/"

def ipa_full(ph):
    toks = ph.split(); res = ""
    for sounds, st in syllables(ph):
        k = len(sounds); part = toks[:k]; toks = toks[k:]
        s = ""
        for t in part:
            base, d = t.rstrip("012"), t[-1] if t[-1].isdigit() else ""
            if base == "AH" and d == "0": s += "ə"
            elif base == "ER" and d == "0": s += "ər"
            else: s += IPA[base]
        res += ("ˈ" if st == 1 else "ˌ" if st == 2 else "") + s
    return "/" + res + "/"

def lookup(word):
    """(respelling, ipa) for a word as written in the speech, or None."""
    if word in CASED: ph = CASED[word]; return {"sp": respell(ph), "ipa": ipa_full(ph)}
    w = word.lower().strip("'’").replace("’", "'")
    ph = MANUAL.get(w) or cmu().get(w)
    if not ph:  # a plural or a possessive of a known word: detections, Claude's, YOLO's
        m = re.fullmatch(r"(.+?)('s|s)", w)
        base = m and (MANUAL.get(m.group(1)) or cmu().get(m.group(1)))
        if base:
            last = base.split()[-1].rstrip("012")
            ph = base + (" AH0 Z" if last in ("S", "Z", "SH", "ZH", "CH", "JH") else " S" if last in ("P", "T", "K", "F", "TH") else " Z")
    if not ph and re.fullmatch(r"[A-Z]{2,5}s?", word):  # an acronym nobody says as a word: its letters
        ph = " ".join(LETTER[c] for c in word.lower() if c in LETTER)
    if not ph: return None
    return {"sp": respell(ph), "ipa": ipa_full(ph)}
