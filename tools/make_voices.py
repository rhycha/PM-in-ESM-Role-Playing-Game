#!/usr/bin/env python3
"""Regenerate the recorded voices for Project CASTOR and Project POLLUX.

    pip install piper-tts numpy
    # voice model (CC BY 4.0) — see VOICES_ATTRIBUTION.txt
    curl -LO https://github.com/rhasspy/piper/releases/download/v0.0.2/voice-en-us-libritts-high.tar.gz
    tar xf voice-en-us-libritts-high.tar.gz
    python3 make_voices.py            # writes voice/*.mp3 and voice/index.json

Both takes are produced: the natural script and the Plain English script.
Every line is normalised (digits to words), synthesised one sentence at a time
and joined with a fixed pause, so nothing ever breaks in the middle of a number.
Needs ffmpeg on PATH. About 8 hours of audio; roughly 1 hour of compute per
2.4 hours of audio on two cores. Resumable — just run it again.
"""
import json, os, re, subprocess, sys, time
import numpy as np
from piper import PiperVoice, SynthesisConfig

SR=22050; GAP=0.20; SENT_PAUSE=0.24; MAX_INNER=0.26; EDGE_KEEP=0.02
FR=int(0.02*SR)
MODEL="en-us-libritts-high.onnx"
OUT="voice"; TMP="_voice_tmp"

# speaker id and speaking rate per character, chosen by measuring the pitch of
# 72 LibriTTS speakers and spreading the cast across the range
CAST={"narr":(0,1.06),"you":(27,1.00),"nightingale":(20,1.00),"hopper":(25,0.96),
 "curie":(11,1.00),"lovelace":(17,0.94),"lamarr":(4,0.98),"leonardo":(6,1.02),
 "medici":(30,1.06),"deming":(29,1.08),"gantt":(26,1.00),"brandeis":(33,1.04),
 "turing":(24,1.00),"tesla":(8,0.95),"eiffel":(19,1.00),"einstein":(37,1.10),
 "gutenberg":(39,1.04),"babbage":(31,1.00)}

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vnorm import norm, sentences          # shipped beside this file

def env(a):
    n=len(a)//FR
    if n<1: return np.zeros(0),0
    x=a[:n*FR].reshape(n,FR).astype(np.float32)/32768.0
    return np.sqrt((x*x).mean(axis=1)), n

def trim(a):
    e,n=env(a)
    if n<2: return a
    thr=max(e.max()*0.02,3e-4); nz=np.flatnonzero(e>=thr)
    if not len(nz): return a[:0]
    k=int(EDGE_KEEP/0.02)
    return a[max(0,nz[0]-k)*FR: min(n,nz[-1]+1+k)*FR]

def cap_inner(a):
    e,n=env(a)
    if n<3: return a
    thr=max(e.max()*0.02,3e-4); sil=e<thr
    keep=[]; i=0; capf=int(round(MAX_INNER/0.02))
    while i<n:
        j=i
        if sil[i]:
            while j<n and sil[j]: j+=1
            keep.append((i,i+min(j-i,capf)))
        else:
            while j<n and not sil[j]: j+=1
            keep.append((i,j))
        i=j
    return np.concatenate([a[s*FR:t*FR] for s,t in keep]) if keep else a

def fade(a,ms=8):
    k=int(SR*ms/1000)
    if len(a)<2*k: return a
    a=a.astype(np.float32); a[:k]*=np.linspace(0,1,k); a[-k:]*=np.linspace(1,0,k)
    return a.astype(np.int16)

def say(voice,sid,ls,text):
    parts=[]
    for sent in sentences(text):
        t=norm(sent)
        if not t.strip(): continue
        cfg=SynthesisConfig(speaker_id=sid,length_scale=ls,normalize_audio=True)
        pcm=np.frombuffer(b"".join(c.audio_int16_bytes for c in voice.synthesize(t,syn_config=cfg)),dtype=np.int16)
        pcm=cap_inner(trim(pcm))
        if len(pcm): parts.append(pcm)
    if not parts: return np.zeros(0,dtype=np.int16)
    pause=np.zeros(int(SENT_PAUSE*SR),dtype=np.int16)
    out=parts[0]
    for p in parts[1:]: out=np.concatenate([out,pause,p])
    return fade(out)

def main():
    os.makedirs(OUT,exist_ok=True); os.makedirs(TMP,exist_ok=True)
    IDX=f"{TMP}/index.json"
    idx=json.load(open(IDX)) if os.path.exists(IDX) else {"clips":{},"acts":{}}
    voice=PiperVoice.load(MODEL)
    jobs=[]
    for take in ("plain","natural"):
        for tag in ("pollux","castor"):
            for c in json.load(open(f"lines_{tag}.json")):
                jobs.append((c["id"]+(":p" if take=="plain" else ""),
                             f"{tag}_act{c['act']}"+("_p" if take=="plain" else ""),
                             c["who"], c[take]))
    t0=time.time(); done=0
    for cid,key,who,text in jobs:
        if cid in idx["clips"]: continue
        sid,ls=CAST.get(who,CAST["narr"])
        a=say(voice,sid,ls,text)
        if not len(a): continue
        with open(f"{TMP}/{key}.pcm","ab") as f:
            start=idx["acts"].get(key,0.0)
            f.write(a.tobytes()); f.write(np.zeros(int(GAP*SR),dtype=np.int16).tobytes())
        idx["acts"][key]=start+len(a)/SR+GAP
        idx["clips"][cid]=[key,round(start,3),round(len(a)/SR,3)]
        done+=1
        if done%40==0:
            json.dump(idx,open(IDX,"w"))
            print(f"{done} clips · {(time.time()-t0)/60:.0f} min",flush=True)
    json.dump(idx,open(IDX,"w"))
    for key in sorted(idx["acts"]):
        subprocess.run(["ffmpeg","-v","error","-f","s16le","-ar",str(SR),"-ac","1",
                        "-i",f"{TMP}/{key}.pcm","-c:a","libmp3lame","-b:a","32k",
                        f"{OUT}/{key}.mp3","-y"],check=True)
        print("wrote",f"{OUT}/{key}.mp3")
    json.dump(idx["clips"],open(f"{OUT}/index.json","w"))
    print("done —",len(idx["clips"]),"clips")

if __name__=="__main__": main()
