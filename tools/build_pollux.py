# -*- coding: utf-8 -*-
import json, glob, re, sys, unicodedata, collections
sys.path.insert(0,'gen')
from cast import CAST

S=[]
for f in ["src/pollux/act1.json","src/pollux/act2.json","src/pollux/act3.json"]:
    S += json.load(open(f))
seen=set()
for s in S:
    u=[]
    for n in s.get("unlock",[]):
        if n not in seen: seen.add(n); u.append(n)
    s["unlock"]=u

# ---- agile atlas -> game ART shape ----
AT=[json.load(open(f)) for f in sorted(glob.glob("src/agile_art/*.json"))]
AT.sort(key=lambda a:a["n"])
ART={}
for a in AT:
    r=a.get("rasci") or {}
    row=None
    if r.get("cols") and r.get("row"): row=dict(zip(r["cols"],r["row"]))
    ART[a["n"]]={"n":a["n"],"name":a["name"],"one":a["one_liner"],"p":a["guide_page"],
      "A":r.get("A"),"R":r.get("R"),"row":row,"app":r.get("A") or "—","phase":a["group"],
      "ex":a.get("pollux_excerpt"),"traps":a.get("traps",[]),"diagram":a.get("diagram",[]),
      "meta":a.get("meta",[]),
      "fields":[{"f":x["f"],"what":x["what"],"who":x["who"],"castor":x.get("pollux","")} for x in a.get("fields",[])]}

def norm(t): return re.sub(r'\s+',' ',unicodedata.normalize("NFKD",str(t))).strip().lower()
ANAME={norm(v["name"]):k for k,v in ART.items()}
EXTRA={"work items list":16,"release plan":17,"iteration plan":18,"development work plan":15,
 "the pm²-agile model":1,"pm²-agile model":1,"lifecycle":2,"iterations":3,"releases":4,
 "pm²-agile principles":1,"the pm²-agile mindsets":1,"agile & pm²":1,"tailoring & customisation":1,
 "core roles":23,"project manager (pm)":27,"business manager (bm)":28,
 "ready for closing (rfc)":22,"closing":22,"lessons learned":9,"administrative closure":22,
 "transition into service":20,"transition iteration":4,"success criteria":10,
 "coordination and reporting":33,"definition of done":8,"project logs":22,"project reports":22}
for a in AT:
    g=norm(a["name"]); EXTRA.setdefault(g,a["n"])
    for th in ("themes",):
        pass
# themes by short name
for a in AT:
    if a["group"]=="Themes":
        EXTRA.setdefault(norm(a["name"].replace("Theme — ","")), a["n"])

STOP={"date","name","status","owner","title","version","author","priority","description",
 "comments","notes","scope","cost","risks","issues","actions","objectives","deliverables","approach","goal"}
def clean(t):
    nm=norm(t)
    nm=re.sub(r'^\d+(\.\d+)*\s*','',nm); nm=re.sub(r'^§\S+\s*','',nm)
    nm=re.sub(r'\s*\(.*?\)\s*$','',nm).strip()
    nm=re.sub(r'\s*[—–-]\s*.*$','',nm).strip()
    return nm
IDX=[]
for n,a in ART.items():
    for i,fl in enumerate(a["fields"]):
        nm=clean(fl["f"])
        if len(nm)<5 or nm in STOP: continue
        IDX.append((nm,n,"f",i,len(nm)))
    for bi,b in enumerate(a["diagram"]):
        nm=clean(b.get("sec",""))
        if len(nm)>=5 and nm not in STOP: IDX.append((nm,n,"s",bi,len(nm)))
        for it in b.get("items",[]):
            for part in re.split(r'\s*[·;:]\s*', str(it)):
                nm=clean(part)
                if len(nm)>=6 and nm not in STOP: IDX.append((nm,n,"s",bi,len(nm)))
sk=set(); U=[]
for t in IDX:
    k=(t[0],t[1])
    if k in sk: continue
    sk.add(k); U.append(t)
IDX=sorted(U,key=lambda x:-x[4])

prev=None; hits=0
for s in S:
    cand=set(s.get("unlock",[]))
    for c in s.get("covers",[]):
        k=norm(c)
        if k in ANAME: cand.add(ANAME[k])
        elif k in EXTRA: cand.add(EXTRA[k])
        else:
            for nm,n in EXTRA.items():
                if nm and nm in k: cand.add(n); break
    fa=(s["unlock"][0] if s.get("unlock") else (sorted(cand)[0] if cand else prev)) or 1
    s["fa"]=fa; prev=fa
    if fa: cand.add(fa)
    s["cand"]=sorted(cand)
    local=[t for t in IDX if t[1] in cand]
    for l in s["lines"]:
        hay=norm(l["text"]+" "+l.get("plain",""))
        best=None
        for nm,an,kind,fi,L in local:
            if nm in hay:
                if best is None or (an==fa and best[0]!=fa): best=(an,kind,fi,L)
                if an==fa: break
        if best: l["fx"]=[best[0],best[1],best[2]]; hits+=1

# ---- POLLUX role overrides: the same people hold agile roles here ----
import copy
CAST=copy.deepcopy(CAST)
CAST.pop("tesla",None)
def rolecard(n):
    a=next((x for x in AT if x["n"]==n),None)
    if not a: return None
    return a["purpose"]
OVR={
 "you":{"r":"Project Manager (PM)","layer":"Managing Layer","org":"ESM Project Support Office",
   "why":"You keep the PM² role. PM²-Agile does not delete it — it puts an agile team inside the Executing phase you still run.",
   "acc":"In a PM²-Agile project the Project Manager is <b>Accountable on every agile artefact row</b> — Development Handbook, Development Work Plan, Work Items List, Release Plan, Iteration Plan, Test Plan, Deployment Plan, Development Status Report. What changes is who is Responsible. You do not run the ceremonies and you do not prioritise the Work Items List."},
 "curie":{"r":"Product Owner (PrOw)","layer":"Core agile role","org":"Head of Reporting, Lending Operations",
   "why":"She refused to sign for 998 of 1,000 loans in Project CASTOR. Now she owns the Work Items List and decides what gets built first. Nobody argues with her acceptance criteria.",
   "acc":"Owns and prioritises the <b>Work Items List</b>, formulates the Iteration Goal, defines acceptance criteria, and accepts or rejects work at the Iteration Review. Accountable for Iteration Planning. Her authority is delegated by the Business Manager (p.65) — not the same thing as Scrum's Product Owner."},
 "lovelace":{"r":"Team Coordinator (TeCo)","layer":"Core agile role","org":"Team Coordinator, Project POLLUX",
   "why":"The Business Analyst from Project CASTOR, promoted. She turned intention into specification; now she facilitates the team that builds it.",
   "acc":"Facilitates the ceremonies, removes impediments, protects the team's way of working, and is <b>Responsible</b> for the Development Handbook, Development Work Plan, Release Plan, Iteration Plan, Deployment Plan and Development Status Report. <b>A TeCo is not a Scrum Master</b> and reports to the Project Manager."},
 "einstein":{"r":"Architecture Owner (ArOw)","layer":"Core agile role","org":"seconded from Enterprise Architecture",
   "why":"He reframes. Every enabler story starts with him asking what problem is actually being solved.",
   "acc":"Owns the technical direction inside the team. <b>Responsible</b> for the Architecture Overview and the Operational Model; supports planning and the Work Items List. Guides, rather than dictates, the team's technical decisions."},
 "eiffel":{"r":"Agile Team Member (ATeM)","layer":"Performing Layer","org":"seconded lead, Levallois Systems",
   "why":"He delivered a 300-metre tower on time and under budget, and he is contractually precise about what 'done' means — which is exactly the argument this project needs.",
   "acc":"Agile Team Members build and test the solution, estimate their own work, state their own capacity, and commit to the Iteration Goal. <b>Responsible</b> for Iteration Planning, the Daily Stand-up, the Iteration Review and the Test Plan."},
 "hopper":{"r":"Business Manager (BM)","layer":"Managing Layer","org":"Senior Loan Operations Officer",
   "why":"Same as Project CASTOR. Still the business's daily voice — and in an agile project she is the one who empowers the Product Owner.",
   "acc":"Represents the Project Owner day to day and <b>empowers the Product Owner</b> to prioritise on the business's behalf (p.65). Still Responsible for the Business Case and the Business Implementation Plan. She does not re-prioritise the Work Items List herself."},
 "nightingale":{"r":"Project Owner (PO)","layer":"Directing Layer","org":"Head of Lending Operations Division",
   "why":"Unchanged from Project CASTOR. Still accountable for the benefits — which, this time, some of them can be demonstrated on closing day.",
   "acc":"Accountable for the project's success and for realising the benefits. Chairs the PSC. The PM² governance layers survive PM²-Agile completely intact."},
}
for k,v in OVR.items():
    if k in CAST: CAST[k].update(v)

GRP=collections.OrderedDict()
for a in AT: GRP.setdefault(a["group"],[]).append(a["name"])
CHECK=[(g+" ("+str(len(v))+")", v) for g,v in GRP.items()]
covmap={}
for s in S:
    for n in s["cand"]: covmap.setdefault(ART[n]["name"],s["id"])
covered=sum(1 for _,v in CHECK for x in v if x in covmap)
print("atlas entries reached by the story:",covered,"/",sum(len(v) for _,v in CHECK))
print("scenes",len(S),"lines",sum(len(x['lines']) for x in S),
      "| field anchors",hits,"| choices",sum(1 for s in S if s.get('choice')))

ACTS=[(1,"Act I","Initiating & Planning","Why agile, and everything in PM² that survives it."),
      (2,"Act II","Executing","Five ceremonies, one iteration, two of them mishandled."),
      (3,"Act III","Releases & Closing","The gates were there the whole time.")]
BG=json.load(open("src/background.json"))
# map covers -> atlas names for the coverage screen
for s in S: s["covers"]=[ART[n]["name"] for n in s["cand"]]
open("src/pollux_payload.json","w").write(json.dumps(
 {"S":S,"CAST":CAST,"ART":ART,"ACTS":ACTS,"CHECK":CHECK,"BG":BG},ensure_ascii=False))
import os; print("payload",os.path.getsize("src/pollux_payload.json"))
