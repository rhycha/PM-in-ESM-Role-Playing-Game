#!/usr/bin/env python3
"""Regenerate selected recorded acts with content-addressed per-line caching.

Preview without synthesis dependencies:
    python3 tools/make_voices.py --plan --project castor --act 1 --take plain

Render the same selection when piper-tts, numpy, ffmpeg and a local model exist:
    python3 tools/make_voices.py --project castor --act 1 --take plain --model /path/to/en-us-libritts-high.onnx

Dialogue comes from the current play HTML, including choice replies, never the
older tools/lines_*.json scripts. The legacy --take plain name means the page's
single :p playback slot; its exact current text is rendered, not a second script.
Output goes beside the source pages in voice/. Each successful act gets a new
content-addressed MP3 plus matching voice/index.json and embedded VIDX entries.
The other acts, the story, saved progress and older MP3 files remain untouched.
No model is downloaded by this script. The existing MP3s retain their original
pronunciation until explicitly regenerated. See VOICES_ATTRIBUTION.txt for model
licensing. Cache keys include normalized text, synthesis code, cast, and model.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

from vnorm import norm

ROOT=Path(__file__).resolve().parents[1]
TOOLS=Path(__file__).resolve().parent
SR=22050
GAP=0.20
PAGES={"castor":"06_Project_CASTOR_EN.html","pollux":"09_Project_POLLUX_EN.html"}

CAST={"narr":(0,1.06),"you":(27,1.00),"nightingale":(20,1.00),"hopper":(25,0.96),
 "curie":(11,1.00),"lovelace":(17,0.94),"lamarr":(4,0.98),"leonardo":(6,1.02),
 "medici":(30,1.06),"deming":(29,1.08),"gantt":(26,1.00),"brandeis":(33,1.04),
 "turing":(24,1.00),"tesla":(8,0.95),"eiffel":(19,1.00),"einstein":(37,1.10),
 "gutenberg":(39,1.04),"babbage":(31,1.00)}



def json_constant(text, name):
    """Locate one JSON constant without executing any page JavaScript."""
    # The page payloads are top-level declarations. Indented local variables
    # (including the portrait renderer's separate P array) are not payloads.
    matches=list(re.finditer(r"(?m)^const[ \t]+"+re.escape(name)+r"\s*=\s*",text))
    if len(matches)!=1: raise ValueError(f"Expected one JSON constant {name}, found {len(matches)}")
    start=matches[0].end()
    value,length=json.JSONDecoder().raw_decode(text[start:])
    return value,start,start+length


def jobs_from_page(text, tag, act=None):
    payload,_,_=json_constant(text,"P")
    actual_tag,_,_=json_constant(text,"VTAG")
    if actual_tag!=tag: raise ValueError(f"Page tag {actual_tag!r} does not match {tag!r}")
    jobs={}
    seen=set()
    for scene in payload["S"]:
        if act is not None and scene["act"]!=act: continue
        key=f"{tag}_act{scene['act']}_p"
        slots=[(str(i),line) for i,line in enumerate(scene["lines"])]
        slots.extend((f"c{i}",option["reply"]) for i,option in enumerate((scene.get("choice") or {}).get("options",[])) if option.get("reply"))
        for slot,line in slots:
            cid=f"{tag}:{scene['id']}:{slot}:p"
            if cid in seen: raise ValueError(f"Duplicate playback slot: {cid}")
            if not isinstance(line.get("text"),str) or not line["text"].strip():
                raise ValueError(f"Missing spoken text: {cid}")
            seen.add(cid)
            jobs.setdefault(key,[]).append((cid,line["who"],line["text"]))
    return jobs


def jobs_for(project="all", take="plain", act=None, pages_dir=None):
    if take!="plain": raise ValueError("Current pages have one :p take; render exact page text with --take plain.")
    pages_dir=Path(pages_dir or ROOT/"play")
    jobs={}
    for tag in (("castor","pollux") if project=="all" else (project,)):
        jobs.update(jobs_from_page((pages_dir/PAGES[tag]).read_text(),tag,act))
    return jobs


def merge_index(index, key, rows, entries):
    """Replace only the selected act's slots; retain all unrelated timings."""
    scenes={cid.rsplit(":",2)[0] for cid,_,_ in rows}
    return {**{cid:entry for cid,entry in index.items()
               if not (cid.endswith(":p") and cid.rsplit(":",2)[0] in scenes)
               and entry[0]!=key and not entry[0].startswith(key+"_")},**entries}


def page_with_index(text, key, rows, entries):
    """Validate against current dialogue and change only the VIDX JSON span."""
    tag=key.split("_",1)[0]
    current=jobs_from_page(text,tag).get(key)
    if current!=rows: raise ValueError(f"Dialogue changed during synthesis for {key}; refusing to publish stale audio.")
    if set(entries)!={cid for cid,_,_ in rows}: raise ValueError("Timing entries do not match selected playback slots.")
    for entry in entries.values():
        if len(entry)!=3 or not (entry[0]==key or entry[0].startswith(key+"_")) or entry[1]<0 or entry[2]<=0:
            raise ValueError("Invalid timing entry for selected act.")
    index,start,end=json_constant(text,"VIDX")
    updated=merge_index(index,key,rows,entries)
    return text[:start]+json.dumps(updated,ensure_ascii=False)+text[end:]


def cache_key(text, speaker, model_stamp, source_stamp):
    # A clip ID alone is insufficient: a corrected decimal must invalidate audio.
    payload=json.dumps([norm(text),speaker,model_stamp,source_stamp],sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()


def write_json(path, value):
    write_text(path,json.dumps(value))


def write_text(path, value):
    with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, suffix=".json", delete=False) as handle:
        handle.write(value)
        temporary=Path(handle.name)
    os.replace(temporary,path)


def main():
    parser=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--project",choices=("all","castor","pollux"),default="all")
    parser.add_argument("--take",choices=("plain",),default="plain",help="legacy name for the current page's :p slots")
    parser.add_argument("--act",type=int)
    parser.add_argument("--model",type=Path,default=TOOLS/"en-us-libritts-high.onnx")
    parser.add_argument("--pages-dir",type=Path,default=ROOT/"play",help="source HTML directory; output is its adjacent voice/ folder")
    parser.add_argument("--cache",type=Path,default=ROOT/".voice-cache")
    parser.add_argument("--plan",action="store_true",help="list selected acts and sample spoken text; do not synthesize or write")
    args=parser.parse_args()
    try: jobs=jobs_for(args.project,args.take,args.act,args.pages_dir)
    except (OSError,ValueError,KeyError) as exc: parser.error(str(exc))
    if not jobs: parser.error("No dialogue matches this project/act/take selection.")
    for key,rows in jobs.items(): print(f"{key}: {len(rows)} lines")
    output=args.pages_dir/"voice"
    print("Source pages:",args.pages_dir)
    print("Output:",output)
    if args.plan:
        print("Example:",norm(next(iter(jobs.values()))[0][2]))
        print("Plan only: no recordings or cache files changed.")
        return
    if not args.model.is_file(): parser.error(f"Local model missing: {args.model}. Supply --model; use --plan to inspect without synthesis.")
    if not shutil.which("ffmpeg"): parser.error("ffmpeg is required to encode recordings; no files changed.")
    try:
        import numpy as np
        from piper import PiperVoice,SynthesisConfig
        from vaudio import say
    except ImportError as exc:
        parser.error(f"Synthesis dependency unavailable: {exc}. No files changed.")
    model_config=args.model.with_suffix(args.model.suffix+".json")
    stamps=[(str(p.resolve()),p.stat().st_size,p.stat().st_mtime_ns) for p in (args.model,model_config) if p.exists()]
    source_stamp=hashlib.sha256(b"".join((TOOLS/name).read_bytes() for name in ("make_voices.py","vnorm.py","vaudio.py"))).hexdigest()
    voice=PiperVoice.load(str(args.model))
    if int(voice.config.sample_rate)!=SR: parser.error(f"This renderer expects a {SR} Hz model; received {voice.config.sample_rate} Hz.")
    output.mkdir(parents=True,exist_ok=True)
    args.cache.mkdir(parents=True,exist_ok=True)
    index_path=output/"index.json"
    index=json.loads(index_path.read_text()) if index_path.exists() else {}
    from vnorm import sentences
    for key,rows in jobs.items():
        new_entries={}
        with tempfile.TemporaryDirectory(prefix="pm2-voice-",dir=args.cache) as temporary:
            pcm_path=Path(temporary)/"act.pcm"
            start=0
            with pcm_path.open("wb") as pcm:
                for cid,who,text in rows:
                    sid,rate=CAST.get(who,CAST["narr"])
                    digest=cache_key(text,[sid,rate],stamps,source_stamp)
                    cached=args.cache/(digest+".npy")
                    if cached.exists(): audio=np.load(cached,allow_pickle=False)
                    else:
                        audio=say(voice,lambda:SynthesisConfig(speaker_id=sid,length_scale=rate,normalize_audio=True),text,norm,sentences)
                        if not len(audio): raise RuntimeError(f"Empty audio for {cid}; existing act was not replaced.")
                        pending=cached.with_suffix(".tmp")
                        with pending.open("wb") as handle: np.save(handle,audio,allow_pickle=False)
                        os.replace(pending,cached)
                    pcm.write(audio.tobytes())
                    pcm.write(np.zeros(int(GAP*SR),dtype=np.int16).tobytes())
                    new_entries[cid]=[key,round(start,3),round(len(audio)/SR,3)]
                    start+=len(audio)/SR+GAP
            # A new content-addressed name keeps old pages playable until their
            # timing table is switched, and avoids stale browser MP3 caches.
            with tempfile.NamedTemporaryFile(dir=output,suffix=".mp3",delete=False) as handle:
                encoded=Path(handle.name)
            try:
                subprocess.run(["ffmpeg","-v","error","-f","s16le","-ar",str(SR),"-ac","1","-i",str(pcm_path),"-c:a","libmp3lame","-b:a","64k",str(encoded),"-y"],check=True)
                audio_hash=hashlib.sha256(encoded.read_bytes()).hexdigest()[:16]
                recorded_key=key+"_"+audio_hash
                for entry in new_entries.values(): entry[0]=recorded_key
                page=args.pages_dir/PAGES[key.split("_",1)[0]]
                latest=page.read_text()
                revised=page_with_index(latest,key,rows,new_entries)
                # All source/timing validation happens before publication.
                os.replace(encoded,output/(recorded_key+".mp3"))
                index=merge_index(index,key,rows,new_entries)
                write_json(index_path,index)
                write_text(page,revised)
            finally:
                encoded.unlink(missing_ok=True)
        print("Wrote",key,len(new_entries),"clips",flush=True)
    print("Done. Selected source pages and voice/index.json now reference the new recordings.")


if __name__=="__main__": main()
