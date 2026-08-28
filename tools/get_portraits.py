#!/usr/bin/env python3
"""Install real photographs of the cast, from Wikimedia Commons.

    python3 get_portraits.py            # writes portraits/<id>.jpg beside the HTML
    python3 get_portraits.py --list     # show the plan and licences, download nothing

The game looks for portraits/<id>.jpg. If a file is there it is used; if not, the
drawn avatar stays. So you can run this, delete any face you dislike, and re-open
the page — nothing else needs rebuilding.

LICENCE SAFETY. This script does not trust the file list below. For every file it
asks the Commons API for the licence and the author, and it REFUSES to download
anything that is not public domain or CC0/CC BY/CC BY-SA. Whatever it does write,
it credits in portraits/CREDITS.txt. Read that file before you publish the repo.

Needs: pip install requests pillow
"""
import argparse, io, json, os, sys

API = "https://commons.wikimedia.org/w/api.php"
UA  = "PM2-CASTOR-study-project/1.0 (educational, non-commercial)"

# id -> Commons file name. Only figures whose lifetime portraits are old enough
# that copyright has expired, plus Grace Hopper, whose official portraits are
# works of the US Navy and therefore public domain by statute.
#
# DELIBERATELY ABSENT — their photographs are very likely still in copyright:
#   turing   (d. 1954)  · deming (d. 1993) · lamarr (d. 2000)
#   tesla is present: he died in 1943 and the 1890 Sarony portrait is long expired.
# Those three keep the drawn avatar. Do not add them without checking first.
FILES = {
 "leonardo":   "Leonardo self.jpg",
 "medici":     "Lorenzo de' Medici.jpg",
 "gutenberg":  "Gutenberg.jpg",
 "babbage":    "Charles Babbage - 1860.jpg",
 "lovelace":   "Ada Lovelace portrait.jpg",
 "nightingale":"Florence Nightingale (H Hering NPG x82368).jpg",
 "eiffel":     "Gustave Eiffel 1888 Nadar2.jpg",
 "gantt":      "Henry Gantt 1919.jpg",
 "curie":      "Marie Curie c1920.jpg",
 "tesla":      "N.Tesla.JPG",
 "brandeis":   "Louis Brandeis.jpg",
 "einstein":   "Albert Einstein Head.jpg",
 "hopper":     "Commodore Grace M. Hopper, USN (covered).jpg",
}

OK_LICENCE = ("public domain","pd-","cc0","cc by","cc-by","attribution")
BAD_HINT   = ("fair use","non-free","all rights reserved","copyrighted")

def meta(session, names):
    out={}
    names=list(names)
    for i in range(0,len(names),20):
        chunk=names[i:i+20]
        r=session.get(API, params={
            "action":"query","format":"json","prop":"imageinfo",
            "iiprop":"url|extmetadata|size","iiurlwidth":"640",
            "titles":"|".join("File:"+n for n in chunk)}, timeout=30)
        r.raise_for_status()
        pages=r.json().get("query",{}).get("pages",{})
        for pg in pages.values():
            title=pg.get("title","").replace("File:","")
            if "missing" in pg or not pg.get("imageinfo"):
                out[title]=None; continue
            ii=pg["imageinfo"][0]; em=ii.get("extmetadata",{})
            g=lambda k: (em.get(k,{}) or {}).get("value","")
            out[title]={"url":ii.get("thumburl") or ii.get("url"),
                        "page":ii.get("descriptionurl",""),
                        "licence":g("LicenseShortName") or g("UsageTerms"),
                        "author":strip(g("Artist")),
                        "credit":strip(g("Credit"))}
    return out

def strip(h):
    import re
    return re.sub(r"<[^>]+>","",h or "").strip()[:160]

def allowed(lic):
    l=(lic or "").lower()
    if any(b in l for b in BAD_HINT): return False
    return any(k in l for k in OK_LICENCE)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--list",action="store_true")
    ap.add_argument("--out",default="portraits")
    ap.add_argument("--size",type=int,default=480)
    a=ap.parse_args()
    try:
        import requests
        from PIL import Image
    except ImportError:
        sys.exit("pip install requests pillow")
    s=requests.Session(); s.headers["User-Agent"]=UA
    info=meta(s, FILES.values())
    plan=[]
    for cid,fn in FILES.items():
        m=info.get(fn)
        if not m:            plan.append((cid,fn,None,"NOT FOUND on Commons")); continue
        if not allowed(m["licence"]): plan.append((cid,fn,m,"REFUSED — licence is "+(m["licence"] or "unstated"))); continue
        plan.append((cid,fn,m,"ok"))
    w=max(len(c) for c in FILES)
    for cid,fn,m,st in plan:
        print(f"{cid:<{w}}  {st:<34}  {(m['licence'] if m else ''):<28}  {fn}")
    if a.list: return
    os.makedirs(a.out,exist_ok=True)
    creds=["Portraits used in Project CASTOR / Project POLLUX",
           "Downloaded from Wikimedia Commons by get_portraits.py.",
           "Each line: character · licence · author · source page.",""]
    n=0
    for cid,fn,m,st in plan:
        if st!="ok": continue
        img=s.get(m["url"],timeout=60); img.raise_for_status()
        im=Image.open(io.BytesIO(img.content)).convert("RGB")
        # square centre crop, biased to the upper third so faces sit well
        wd,ht=im.size; side=min(wd,ht)
        left=(wd-side)//2; top=int((ht-side)*0.18)
        im=im.crop((left,top,left+side,top+side)).resize((a.size,a.size),Image.LANCZOS)
        im.save(os.path.join(a.out,cid+".jpg"),"JPEG",quality=88,optimize=True)
        creds.append(f"{cid} · {m['licence']} · {m['author'] or 'unknown'} · {m['page']}")
        n+=1
    open(os.path.join(a.out,"CREDITS.txt"),"w").write("\n".join(creds)+"\n")
    print(f"\nwrote {n} portraits to {a.out}/ and {a.out}/CREDITS.txt")
    print("Characters with no file here keep their drawn avatar. That is expected.")

if __name__=="__main__": main()
