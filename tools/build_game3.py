# -*- coding: utf-8 -*-
import json, sys, glob, re, unicodedata
sys.path.insert(0,'gen')
from cast import CAST

FILES=["src/story/act1.json","src/story/act2.json","src/story/act3.json",
       "src/story/act4a.json","src/story/act4b.json","src/story/act5.json"]
S=[]
for f in FILES: S += json.load(open(f))
seen=set()
for s in S:
    u=[]
    for n in s.get("unlock",[]):
        if n not in seen: seen.add(n); u.append(n)
    s["unlock"]=u
NORM={"Phase Gate RfP (Ready for Planning)":"Phase Gate: RfP (Ready for Planning)",
      "Phase Gate RfE (Ready for Executing)":"Phase Gate: RfE (Ready for Executing)",
      "Phase Gate RfC (Ready for Closing)":"Phase Gate: RfC (Ready for Closing)",
      "Manage Risks":"Manage Risk","Manage Project Changes":"Manage Project Change",
      "Manage Issues & Decisions":"Manage Issues and Decisions",
      "Lessons Learned and Post-project Recommendations":"Lessons Learned and Post-Project Recommendations",
      "Initiating Phase":"Initiating Phase (overview)","Monitor & Control":"Monitor & Control (overview)"}
for s in S: s["covers"]=[NORM.get(c,c) for c in s.get("covers",[])]

# ---- full artefact data (diagram + fields) for the split pane ----
FULL={}
for f in glob.glob("src/art/*.json"):
    d=json.load(open(f))
    FULL[d["n"]]={"n":d["n"],"name":d["name"],"one":d["one_liner"],"p":d["guide_page"],
      "A":(d["rasci"] or {}).get("A"),"R":(d["rasci"] or {}).get("R"),"row":(d["rasci"] or {}).get("row"),
      "app":d["approved_by"],"phase":d["created_in"],"ex":d.get("castor_excerpt"),
      "traps":d.get("traps",[]),"diagram":d.get("diagram",[]),
      "fields":[{"f":x["f"],"what":x["what"],"who":x["who"],"castor":x["castor"]} for x in d.get("fields",[])]}

def norm(t): return re.sub(r'\s+',' ',unicodedata.normalize("NFKD",str(t))).strip().lower()

# name -> artefact number, for scene focus
ANAME={norm(v["name"]):k for k,v in FULL.items()}
ALIAS={"phase gate: rfp (ready for planning)":27,"phase gate: rfe (ready for executing)":27,
 "phase gate: rfc (ready for closing)":27,"planning kick-off meeting":17,"executing kick-off meeting":17,
 "project-end review meeting":33,"lessons learned and post-project recommendations":33,
 "administrative closure":33,"project coordination":19,"quality assurance":28,"project reporting":19,
 "information distribution":16,"monitor project performance":19,"control schedule":6,"control cost":6,
 "manage stakeholders":32,"manage requirements":11,"manage project change":21,"manage risk":23,
 "manage issues and decisions":24,"manage quality":28,"manage deliverables acceptance":29,
 "manage transition":30,"manage business implementation":31,"manage outsourcing":7,
 "initiating meeting":1,"project status report":19,"minutes of meeting":18,"meeting agenda":17,
 "project logs":25,"change request form":21}

# ---- field-name index for per-line highlighting ----
STOP={"date","name","status","owner","title","version","author","id","priority","description",
 "comments","notes","scope","cost","risks","issues","actions","objectives","deliverables","approach"}
def clean(t):
    nm=norm(t)
    nm=re.sub(r'^\d+(\.\d+)*\s*','',nm)
    nm=re.sub(r'\s*\(.*?\)\s*$','',nm).strip()
    nm=re.sub(r'\s*[—–-]\s*.*$','',nm).strip()
    return nm
IDX=[]  # (normname, artnum, kind, idx, len)
for n,a in FULL.items():
    for i,fl in enumerate(a["fields"]):
        nm=clean(fl["f"])
        if len(nm)<5 or nm in STOP: continue
        IDX.append((nm,n,"f",i,len(nm)))
    for bi,b in enumerate(a["diagram"]):
        nm=clean(b.get("sec",""))
        if len(nm)>=5 and nm not in STOP: IDX.append((nm,n,"s",bi,len(nm)))
        for it in b.get("items",[]):
            for part in re.split(r'\s*[·;]\s*', str(it)):
                nm=clean(part)
                if len(nm)>=5 and nm not in STOP: IDX.append((nm,n,"s",bi,len(nm)))
    # case-specific labels from the filled excerpt map back to the field of the same name
    ex=(a.get("ex") or {}).get("rows") or []
    fmap={clean(fl["f"]):i for i,fl in enumerate(a["fields"])}
    for r in ex:
        if not r: continue
        nm=clean(r[0])
        if len(nm)>=5 and nm not in STOP and nm in fmap:
            IDX.append((nm,n,"f",fmap[nm],len(nm)))
seenk=set(); U=[]
for t in IDX:
    k=(t[0],t[1])
    if k in seenk: continue
    seenk.add(k); U.append(t)
IDX=sorted(U,key=lambda x:-x[4])

prev=None
hits=0
for s in S:
    # focus artefact for the scene
    fa=None
    if s["unlock"]: fa=s["unlock"][0]
    if fa is None:
        for c in s["covers"]:
            k=norm(c)
            if k in ANAME: fa=ANAME[k]; break
            if k in ALIAS: fa=ALIAS[k]; break
    if fa is None: fa=prev or 1
    s["fa"]=fa; prev=fa
    # candidate artefacts for this scene only — never anchor to something the scene is not about
    cand=set(s.get("unlock",[]))
    if fa: cand.add(fa)
    for c in s["covers"]:
        k=norm(c)
        if k in ANAME: cand.add(ANAME[k])
        elif k in ALIAS: cand.add(ALIAS[k])
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

print("scenes with focus artefact:",sum(1 for s in S if s.get("fa")),"/",len(S))
print("lines with a field anchor:",hits,"/",sum(len(s['lines']) for s in S))

BG=json.load(open("src/background.json"))
CHECK=[
 ("Initiating (ch.5)",["Initiating Meeting","Project Initiation Request","Business Case","Project Charter","Phase Gate: RfP (Ready for Planning)"]),
 ("Planning (ch.6)",["Planning Kick-off Meeting","Project Handbook","Project Stakeholder Matrix","Project Work Plan","Outsourcing Plan","Deliverables Acceptance Plan","Transition Plan","Business Implementation Plan","Phase Gate: RfE (Ready for Executing)"]),
 ("The six Management Plans (App. B)",["Requirements Management Plan","Project Change Management Plan","Risk Management Plan","Issue Management Plan","Quality Management Plan","Communications Management Plan"]),
 ("Executing (ch.7)",["Executing Kick-off Meeting","Project Coordination","Quality Assurance","Project Reporting","Information Distribution","Phase Gate: RfC (Ready for Closing)"]),
 ("Monitor & Control — the 13 processes (ch.9)",["Monitor Project Performance","Control Schedule","Control Cost","Manage Stakeholders","Manage Requirements","Manage Project Change","Manage Risk","Manage Issues and Decisions","Manage Quality","Manage Deliverables Acceptance","Manage Transition","Manage Business Implementation","Manage Outsourcing"]),
 ("Closing (ch.8)",["Project-End Review Meeting","Lessons Learned and Post-Project Recommendations","Project-End Report","Administrative Closure"]),
]
ACTS=[(1,"Act I","Initiating","The problem exists before the project does."),
      (2,"Act II","Planning","Everyone in one room, once."),
      (3,"Act III","Planning","The four plans that decide who owns what."),
      (4,"Act IV","Executing","Nothing survives contact with a live disbursement."),
      (5,"Act V","Closing","The work ends before the value arrives.")]
open("src/game_payload.json","w").write(json.dumps(
  {"S":S,"CAST":CAST,"ART":FULL,"ACTS":ACTS,"CHECK":CHECK,"BG":BG},ensure_ascii=False))
import os; print("payload",os.path.getsize("src/game_payload.json"),"bytes")
