# -*- coding: utf-8 -*-
"""Number / date / id gloss matcher. Additive only: never touches text."""
import json, re, os

STOPALIAS = set()   # aliases we refuse regardless of source

def load_registry(paths):
    ents=[]
    for p in paths:
        for e in json.load(open(p)):
            a=[x for x in e.get('a',[]) if x and x.lower() not in STOPALIAS]
            if not a: continue
            ents.append({'a':a,'k':e.get('k','count'),'s':e.get('s',''),
                         'd':e.get('d',''),'sc':e.get('sc')})
    return ents

def build_index(ents):
    """-> list of (compiled_regex, entryIdx, sceneSet|None, aliasLen) sorted longest first"""
    idx=[]
    for i,e in enumerate(ents):
        sc=set(e['sc']) if e.get('sc') else None
        for al in e['a']:
            pat=r'(?<![A-Za-z0-9-])'+re.escape(al)+r'(?![A-Za-z0-9-])'
            try: rx=re.compile(pat, re.I)
            except re.error: continue
            idx.append((rx,i,sc,len(al)))
    idx.sort(key=lambda t:(-t[3], 0 if t[2] else 1))
    return idx

def annotate(text, idx, sceneId, cap=6):
    """-> list of [surface, entryIdx] , non-overlapping, longest-first"""
    if not text: return []
    taken=[]   # (start,end)
    out=[]; seen=set()
    for rx,ei,sc,_ in idx:
        if len(out)>=cap: break
        if sc is not None and sceneId not in sc: continue
        if ei in seen: continue
        for m in rx.finditer(text):
            s,e=m.span()
            if any(not(e<=ts or s>=te) for ts,te in taken): continue
            taken.append((s,e)); out.append([m.group(0), ei]); seen.add(ei)
            break
    # order by position in text so footnote order reads naturally
    pos={}
    for surf,ei in out:
        pos[(surf,ei)] = text.lower().find(surf.lower())
    out.sort(key=lambda p: pos[(p[0],p[1])])
    return out

def key_for(i): return 'n%d'%i
