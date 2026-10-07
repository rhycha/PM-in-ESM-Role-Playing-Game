# -*- coding: utf-8 -*-
"""Synthesise one dialogue line as clean, sentence-separated speech."""
import numpy as np
SR=22050
FR=int(0.02*SR)              # 20 ms analysis frame
SENT_PAUSE=0.24              # deliberate pause between sentences
MAX_INNER=0.26               # any silence inside a sentence is capped at this
EDGE_KEEP=0.02               # silence left at each edge after trimming

def _env(a):
    n=len(a)//FR
    if n<1: return np.zeros(0), n
    x=a[:n*FR].reshape(n,FR).astype(np.float32)/32768.0
    return np.sqrt((x*x).mean(axis=1)), n

def trim(a, floor=0.02):
    """Remove leading/trailing silence, keeping a little air."""
    e,n=_env(a)
    if n<2: return a
    thr=max(e.max()*floor, 3e-4)
    nz=np.flatnonzero(e>=thr)
    if len(nz)==0: return a[:0]
    k=int(EDGE_KEEP/0.02)
    s=max(0,nz[0]-k)*FR; t=min(n,nz[-1]+1+k)*FR
    return a[s:t]

def cap_inner(a, cap=MAX_INNER, floor=0.02):
    """Shorten any silence inside the clip to `cap` seconds."""
    e,n=_env(a)
    if n<3: return a
    thr=max(e.max()*floor, 3e-4)
    sil=e<thr
    keep=[]; i=0; capf=int(round(cap/0.02))
    while i<n:
        if sil[i]:
            j=i
            while j<n and sil[j]: j+=1
            run=j-i
            keep.append((i, i+min(run,capf)))
            i=j
        else:
            j=i
            while j<n and not sil[j]: j+=1
            keep.append((i,j)); i=j
    return np.concatenate([a[s*FR:t*FR] for s,t in keep]) if keep else a

def fade(a, ms=8):
    k=int(SR*ms/1000)
    if len(a)<2*k: return a
    a=a.astype(np.float32)
    a[:k]*=np.linspace(0,1,k); a[-k:]*=np.linspace(1,0,k)
    return a.astype(np.int16)

def say(voice, cfg_factory, text, norm, sentences):
    """-> int16 mono at 22050, sentence-separated, silence-cleaned."""
    parts=[]
    # Expand decimals and versions before splitting so punctuation inside a
    # number can never become a sentence boundary.
    for t in sentences(norm(text)):
        if not t.strip(): continue
        chunks=list(voice.synthesize(t, syn_config=cfg_factory()))
        pcm=np.frombuffer(b"".join(c.audio_int16_bytes for c in chunks), dtype=np.int16)
        pcm=cap_inner(trim(pcm))
        if len(pcm): parts.append(pcm)
    if not parts: return np.zeros(0,dtype=np.int16)
    pause=np.zeros(int(SENT_PAUSE*SR),dtype=np.int16)
    out=parts[0]
    for p in parts[1:]:
        out=np.concatenate([out,pause,p])
    return fade(out)
