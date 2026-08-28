# -*- coding: utf-8 -*-
"""Per-line prop focus: which single item in which prop is the line pointing at."""
import re, json
W={'zero':0,'one':1,'two':2,'three':3,'four':4,'five':5,'six':6,'seven':7,'eight':8,'nine':9,
'ten':10,'eleven':11,'twelve':12,'thirteen':13,'fourteen':14,'fifteen':15,'sixteen':16,
'seventeen':17,'eighteen':18,'nineteen':19,'twenty':20,'thirty':30,'forty':40}
ORD={'first':1,'second':2,'third':3,'fourth':4,'fifth':5,'sixth':6,'seventh':7,'eighth':8,
'ninth':9,'tenth':10,'eleventh':11,'twelfth':12,'thirteenth':13,'fourteenth':14,'fifteenth':15}
# phrases that mean "item N of this object"
LEAD=r'(?:line|principle|item|row|tab|point|step|clause|criterion|check|question|number|column|section|card|story|entry|finding|test|no\.)'
RX=re.compile(r'\b'+LEAD+r'\s+((?:twenty[- ])?(?:'+'|'.join(list(W)+list(ORD))+r')|\d{1,3})\b', re.I)

def numify(t):
    t=t.strip().lower()
    if t.isdigit(): return t
    if t.startswith('twenty'):
        rest=t.split()[-1].split('-')[-1]
        return str(20+(W.get(rest) or ORD.get(rest) or 0))
    return str(W.get(t) or ORD.get(t) or '')

def item_keys(p):
    """-> set of item keys addressable in this prop"""
    k=set()
    for it in p.get('items',[]): k.add(str(it.get('n')))
    for t in p.get('tabs',[]): k.add(str(t.get('id')))
    for c in p.get('cells',[]): k.add(str(c.get('id')))
    for col in p.get('cols',[]) if p.get('look')=='board' else []:
        for cd in col.get('cards',[]): k.add(str(cd.get('id')))
    for b in p.get('body',[]):
        if b.get('id'): k.add(str(b['id']))
    return k

def titles(p):
    """-> list of (lowercase phrase, key) for title matching"""
    out=[]
    def add(t,k):
        t=re.sub(r'\s+',' ',str(t or '')).strip().lower()
        if len(t)>=6: out.append((t,str(k)))
    for it in p.get('items',[]): add(it.get('t'),it.get('n'))
    for t in p.get('tabs',[]): add(t.get('t'),t.get('id'))
    for c in p.get('cells',[]): add(c.get('t'),c.get('id'))
    if p.get('look')=='board':
        for col in p.get('cols',[]):
            for cd in col.get('cards',[]): add(cd.get('t'),cd.get('id'))
    for b in p.get('body',[]):
        if b.get('id'): add(b.get('h'),b['id'])
    out.sort(key=lambda x:-len(x[0]))
    return out

def run(payload_path):
    P=json.load(open(payload_path))
    PROPS=P.get('PROP',[])
    BY={}
    for i,p in enumerate(PROPS):
        for s in p.get('scenes',[]): BY.setdefault(s,[]).append(i)
    KEYS=[item_keys(p) for p in PROPS]
    TITS=[titles(p) for p in PROPS]
    hits=0; lines=0
    for s in P['S']:
        cand=BY.get(s['id'],[])
        if not cand: continue
        for l in s['lines']:
            lines+=1
            tx=l.get('text','') or ''
            low=re.sub(r'\s+',' ',tx).lower()
            best=None
            # 1. "line nine" / "tab 9" / "row seven" — an explicit item reference
            for m in RX.finditer(tx):
                n=numify(m.group(1))
                if not n: continue
                for pi in cand:
                    if n in KEYS[pi]: best=(pi,n); break
                if best: break
            # 2. a distinctive item title quoted in the line
            if not best:
                for pi in cand:
                    for t,k in TITS[pi]:
                        if t in low: best=(pi,k); break
                    if best: break
            if best: l['px']=[best[0],best[1]]; hits+=1
    json.dump(P, open(payload_path,'w'), ensure_ascii=False)
    print("  per-line prop focus: %d/%d lines in prop scenes"%(hits,lines))

if __name__=='__main__':
    import sys; run(sys.argv[1])
