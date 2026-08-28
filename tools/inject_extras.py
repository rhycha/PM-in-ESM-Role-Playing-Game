# -*- coding: utf-8 -*-
"""Add NUM / PROP / SOL / FACTS / SUBS to a game payload. Additive: text is never modified."""
import json, sys, glob, os
sys.path.insert(0,'gen')
import nums

def run(payload_path, reg_paths, sol_path, prop_path, facts_path, subs_key):
    P=json.load(open(payload_path))
    ents=nums.load_registry(reg_paths)
    idx=nums.build_index(ents)
    NUM={}; used={}
    tot=0; totp=0; lines=0; covered=0
    for s in P["S"]:
        for l in s["lines"]:
            lines+=1
            a=nums.annotate(l.get("text",""), idx, s["id"])
            b=nums.annotate(l.get("plain",""), idx, s["id"]) if l.get("plain") else []
            def emit(hits):
                out=[]
                for surf,ei in hits:
                    k='n%d'%ei
                    if k not in NUM:
                        e=ents[ei]; NUM[k]=[e['s'],e['d'],e['k'],surf]
                    out.append([surf,k])
                return out
            if a: l["n"]=emit(a); tot+=len(a)
            if b: l["np"]=emit(b); totp+=len(b)
            if a or b: covered+=1
    P["NUM"]=NUM
    P["SOL"]=json.load(open(sol_path))
    P["PROP"]=json.load(open(prop_path))
    P["FACTS"]=json.load(open(facts_path))
    P["SUBS"]=json.load(open("src/subs.json"))[subs_key]
    json.dump(P, open(payload_path,"w"), ensure_ascii=False)
    print("  registry entries %d · aliases %d · glossed keys %d"%(len(ents),len(idx),len(NUM)))
    print("  chips: %d natural + %d plain · %d/%d lines carry at least one (%.0f%%)"%(tot,totp,covered,lines,covered/lines*100))
    print("  diagrams %d · props %d · payload %.1f MB"%(len(P["SOL"]),len(P["PROP"]),os.path.getsize(payload_path)/1e6))
    # scene coverage
    sp=set(); ss=set()
    for p in P["PROP"]:
        for x in p.get("scenes",[]): sp.add(x)
    for d in P["SOL"]:
        for x in d.get("scenes",[]): ss.add(x)
    ids=[s["id"] for s in P["S"]]
    print("  scenes with a prop %d/%d · with a solution diagram %d/%d"%(
        len([i for i in ids if i in sp]),len(ids),len([i for i in ids if i in ss]),len(ids)))

if __name__=="__main__":
    which=sys.argv[1]
    if which=="castor":
        run("src/game_payload.json",
            ["src/nums/c1.json","src/nums/c2.json","src/nums/c3.json"],
            "src/solu/castor.json","src/solu/castor_props.json","src/facts_castor.json","castor")
    else:
        run("src/pollux_payload.json",["src/nums/p1.json"],
            "src/solu/pollux.json","src/solu/pollux_props.json","src/facts_pollux.json","pollux")
