#!/usr/bin/env python3
"""Build static data for the Hán tự site.
Usage: build.py <srcdir> <outdir>
srcdir needs: dictionary.txt, graphics.txt (makemeahanzi), hsk.json (complete-hsk-vocabulary),
              Unihan_Readings.txt (Unicode Unihan)
"""
import json, sys, os, collections
src, out = sys.argv[1], sys.argv[2]
os.makedirs(out + '/strokes', exist_ok=True)

# --- Hán Việt (Unihan kVietnamese) ---
hv = {}
for line in open(f'{src}/Unihan_Readings.txt', encoding='utf8'):
    if '\tkVietnamese\t' in line:
        cp, _, val = line.rstrip('\n').split('\t')
        hv[chr(int(cp[2:], 16))] = val.split()

# --- simplified -> traditional (OpenCC single-char pairs, then HSK forms) ---
import re, unicodedata
occ = open(f'{src}/opencc_cn2t.js', encoding='utf8').read()
s2t = {}
for m in re.finditer(r'(?<![^|"`\s])(\S) (\S)(?=[|"`])', occ):
    a, b = m.group(1), m.group(2)
    if a != b and a not in s2t: s2t[a] = b

# --- Hán Việt by pinyin (ph0ngp/hanviet-pinyin-words) ---
t = open(f'{src}/hanvietData.js', encoding='utf8').read()
hvp = json.loads(t[t.index('{'):t.rindex('}')+1])
TONES = {'\u0304': '1', '\u0301': '2', '\u030c': '3', '\u0300': '4'}
def numeric(py):
    out, tone = '', '5'
    for ch in unicodedata.normalize('NFD', py.lower()):
        if ch in TONES: tone = TONES[ch]
        elif unicodedata.combining(ch): pass
        else: out += ch
    return (out.replace('ü', 'v') + tone)
NOM_FIX = {'冷': ['lãnh'], '低': ['đê'], '年': ['niên'], '看': ['khán'], '找': [], '搬': ['ban'], '刷': ['loát'],
           '吧': [], '呢': [], '吗': [], '啊': [], '喂': [], '哪': ['na'], '他': ['tha'], '地': ['địa'], '她': [], '它': []}
def hv_for(c, pinys):
    cands = [c] + ([s2t[c]] if c in s2t else [])
    res = []
    for p in pinys:
        n = numeric(p)
        got = []
        for k in cands:
            e = hvp.get(k)
            if not e: continue
            for key in (n, '*'):
                if key in e and e[key]:
                    got = e[key]; break
            if got: break
        res.append(got)
    return res

# --- HSK ---
hsk = json.load(open(f'{src}/hsk.json', encoding='utf8'))
lvl, freq, words = {}, {}, collections.defaultdict(list)
for e in hsk:
    w = e['simplified']
    levels = e['level']
    old = [int(l[4:]) for l in levels if l.startswith('old-')]
    new = [int(l[4:]) for l in levels if l.startswith('new-')]
    L = min(old) if old else (min(new) if new else None)
    f = e.get('frequency', 10**6)
    form = e['forms'][0]
    py = form['transcriptions']['pinyin']
    mean = form['meanings'][0] if form['meanings'] else ''
    if len(w) == 1:
        if L is not None: lvl[w] = L if old else L  # old-scale if available
        freq[w] = f
        lvl[w] = (L, 'old' if old else 'new')
    else:
        for ch in set(w):
            words[ch].append((f, w, py, mean, L))
wl = {}
for ch, lst in words.items():
    lst.sort()
    wl[ch] = [[w, py, m, L] for _, w, py, m, L in lst[:10]]
json.dump(wl, open(out + '/words.json', 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))

# --- single-char meanings from HSK ---
hsk_mean = {}
for e in hsk:
    if len(e['simplified']) == 1:
        ms = []
        for f in e['forms']:
            ms += f['meanings']
        bad = ('surname', 'used in', 'variant of', 'abbr.', 'old variant', 'archaic', 'Taiwan pr.', 'also pr.')
        good = [m for m in ms if not any(b in m for b in bad)]
        hsk_mean[e['simplified']] = (good or ms)[:5]
        trad = e['forms'][0]['traditional']
        if trad != e['simplified'] and len(trad) == 1: s2t.setdefault(e['simplified'], trad)

vi = dict(l.rstrip('\n').split(' ', 1) for l in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vi_gloss.txt'), encoding='utf8') if l.strip())
# --- dictionary (decomposition / etymology) ---
chars = {}
for line in open(f'{src}/dictionary.txt', encoding='utf8'):
    d = json.loads(line)
    c = d['character']
    o = {}
    if d.get('pinyin'): o['p'] = d['pinyin']
    if d.get('definition'): o['d'] = d['definition']
    if d.get('decomposition') and d['decomposition'] != '？': o['dc'] = d['decomposition']
    et = d.get('etymology')
    if et:
        o['et'] = {k: et[k] for k in ('type', 'phonetic', 'semantic', 'hint') if k in et}
    if d.get('radical'): o['r'] = d['radical']
    pinys = d.get('pinyin') or []
    if pinys:
        h = hv_for(c, pinys)
        if c in NOM_FIX: h = [NOM_FIX[c]] * len(pinys)
        if not any(h):
            fb = hv.get(c) or hv.get(s2t.get(c, ''), [])
            h = [fb[:2]] * len(pinys) if fb else []
        if any(h): o['hv'] = h
    elif c in hv: o['hv'] = [hv[c][:2]]
    if c in vi: o['v'] = vi[c]
    if c in lvl: o['h'], o['hs'] = lvl[c]
    if c in freq: o['f'] = freq[c]
    if c in hsk_mean: o['m'] = hsk_mean[c]
    chars[c] = o

# --- strokes, sharded by codepoint >> 8 ---
shards = collections.defaultdict(dict)
for line in open(f'{src}/graphics.txt', encoding='utf8'):
    g = json.loads(line)
    c = g['character']
    shards[ord(c) >> 8][c] = {'s': g['strokes'], 'm': g['medians']}
    if c in chars: chars[c]['n'] = len(g['strokes'])
    else: chars[c] = {'n': len(g['strokes'])}
for k, v in shards.items():
    json.dump(v, open(f'{out}/strokes/{k:x}.json', 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))

# matches (stroke -> component path) kept separately, same shard scheme
mt = collections.defaultdict(dict)
for line in open(f'{src}/dictionary.txt', encoding='utf8'):
    d = json.loads(line)
    if d.get('matches'):
        mt[ord(d['character']) >> 8][d['character']] = d['matches']
for k, v in mt.items():
    p = f'{out}/strokes/{k:x}.json'
    s = json.load(open(p, encoding='utf8'))
    for c, m in v.items():
        if c in s: s[c]['x'] = m
    json.dump(s, open(p, 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))

json.dump(chars, open(out + '/chars.json', 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))
print(len(chars), 'chars;', len(shards), 'stroke shards')
