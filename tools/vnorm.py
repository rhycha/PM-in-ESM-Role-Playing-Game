# -*- coding: utf-8 -*-
"""English speech normalization shared in behavior with speech_reading.js.

Numbers are interpreted before synthesis, preserving decimal zeroes and identifier
leading zeroes. This improves input pronunciation; it cannot change an existing MP3.
"""
import re

ONES=["zero","one","two","three","four","five","six","seven","eight","nine","ten","eleven","twelve",
"thirteen","fourteen","fifteen","sixteen","seventeen","eighteen","nineteen"]
TENS=["","","twenty","thirty","forty","fifty","sixty","seventy","eighty","ninety"]

def u99(n):
    if n<20: return ONES[n]
    t,o=divmod(n,10)
    return TENS[t]+("-"+ONES[o] if o else "")

def u999(n):
    if n<100: return u99(n)
    h,r=divmod(n,100)
    return ONES[h]+" hundred"+(" and "+u99(r) if r else "")

def cardinal(n):
    n=int(str(n).replace(",", ""))
    if n<0: return "minus "+cardinal(-n)
    if n<1000: return u999(n)
    for scale, word in ((10**12,"trillion"),(10**9,"billion"),(10**6,"million"),(1000,"thousand")):
        if n>=scale:
            q,r=divmod(n,scale)
            return cardinal(q)+" "+word+(" "+cardinal(r) if r else "")

ORD={"one":"first","two":"second","three":"third","five":"fifth","eight":"eighth","nine":"ninth","twelve":"twelfth"}
def ordinal(n):
    def ending(m):
        w=m.group()
        return ORD.get(w, w[:-1]+"ieth" if w.endswith("y") else w+"th")
    return re.sub(r"[a-z]+$", ending, cardinal(n))

def year(n):
    n=int(n)
    hi,lo=divmod(n,100)
    if 2000<=n<2010:
        return "two thousand"+(" "+cardinal(lo) if lo else "")
    if 1100<=n<=2099:
        if lo==0: return cardinal(hi)+" hundred"
        if lo<10: return cardinal(hi)+" oh "+cardinal(lo)
        return cardinal(hi)+" "+cardinal(lo)
    return cardinal(n)

MONTHS="January February March April May June July August September October November December".split()
MONTH="("+"|".join(MONTHS)+")"
NUM=r"\d+(?:,\d{3})*(?:\.\d+)?"
SCALE=r"(?:billion|million|thousand|bn|m|k)"

def _scale(s):
    s=(s or "").lower()
    return {"m":"million","bn":"billion","k":"thousand"}.get(s,s)

def _identifier(s):
    return " ".join(ONES[int(d)] for d in s) if s.startswith("0") else cardinal(s)

def norm(t):
    s=str(t).replace("\u00a0", " ").replace("_", " ")
    for a,b in SAY.items():
        s=re.sub(r"(?<![A-Za-z0-9])"+re.escape(a)+r"(?![A-Za-z0-9])", b, s)
    s=re.sub(r"\b(\d{1,2})\s+"+MONTH+r"(?:\s+(\d{4}))?\b",
             lambda m: "the "+ordinal(m[1])+" of "+m[2]+(" "+year(m[3]) if m[3] else ""), s, flags=re.I)
    s=re.sub(r"\b"+MONTH+r"\s+(\d{4})\b", lambda m:m[1]+" "+year(m[2]),s,flags=re.I)
    def numeric_date(m, iso=False):
        y,mo,d=(m[1],m[2],m[3]) if iso else (m[3],m[2],m[1])
        if 1<=int(mo)<=12 and 1<=int(d)<=31:
            return "the "+ordinal(d)+" of "+MONTHS[int(mo)-1]+" "+year(y)
        return m[0]
    s=re.sub(r"\b(\d{4})-(\d{2})-(\d{2})\b",lambda m:numeric_date(m,True),s)
    s=re.sub(r"\b(\d{2})-(\d{2})-(\d{4})\b",numeric_date,s)
    def clock(m):
        h,mi=int(m[1]),int(m[2])
        return cardinal(h%12 or 12)+((" oh " if mi<10 else " ")+cardinal(mi) if mi else "")+" "+(m[3].upper() if m[3] else "A" if h<12 else "P")+" M"
    s=re.sub(r"\b([01]?\d|2[0-3]):([0-5]\d)(?:\s*([ap])\.?m\.?)?",clock,s,flags=re.I)
    s=re.sub(r"\b([A-Z]{1,4})(\d+)-(\d+)\b",lambda m:" ".join(m[1])+" "+_identifier(m[2])+" "+_identifier(m[3]),s)
    s=re.sub(r"\b([A-Z]{1,4})-(\d+)\b",lambda m:" ".join(m[1])+" "+_identifier(m[2]),s)
    s=re.sub(r"\b([A-Z]{1,4})(\d+)\b",lambda m:" ".join(m[1])+" "+_identifier(m[2]),s)
    currency={"€":"euros","$":"dollars","£":"pounds"}
    s=re.sub(r"([€$£])\s*("+NUM+r")\s*[-–—]\s*("+NUM+r")\s*("+SCALE+r")?\b",
             lambda m:decimal(m[2])+" to "+decimal(m[3])+(" "+_scale(m[4]) if m[4] else "")+" "+currency[m[1]],s,flags=re.I)
    s=re.sub(r"([€$£])\s*("+NUM+r")\s*("+SCALE+r")?\b",
             lambda m:decimal(m[2])+(" "+_scale(m[3]) if m[3] else "")+" "+currency[m[1]],s,flags=re.I)
    s=re.sub(r"\b("+NUM+r")\s*[-–—]\s*("+NUM+r")\s*%",lambda m:decimal(m[1])+" to "+decimal(m[2])+" per cent",s)
    s=re.sub(r"\b("+NUM+r")\s*%",lambda m:decimal(m[1])+" per cent",s)
    s=re.sub(r"\b(version\s+|v)(\d+(?:\.\d+)*)\b",lambda m:"version "+" point ".join(_identifier(x) for x in m[2].split(".")),s,flags=re.I)
    s=re.sub(r"\b(section|chapter|work package)\s+(\d+(?:\.\d+)+)\b",lambda m:m[1]+" "+" point ".join(_identifier(x) for x in m[2].split(".")),s,flags=re.I)
    s=re.sub(r"\b\d+(?:\.\d+){2,}\b",lambda m:" point ".join(_identifier(x) for x in m[0].split(".")),s)
    s=re.sub(r"\b(\d+)(?:st|nd|rd|th)\b",lambda m:ordinal(m[1]),s,flags=re.I)
    s=re.sub(r"\b("+NUM+r")\s*[-–—]\s*("+NUM+r")\b",lambda m:decimal(m[1])+" to "+decimal(m[2]),s)
    s=re.sub(r"\b("+NUM+r")\s*/\s*("+NUM+r")\b",lambda m:decimal(m[1])+" out of "+decimal(m[2]),s)
    s=re.sub(r"\b(\d+):(\d+)\b",lambda m:cardinal(m[1])+" to "+cardinal(m[2]),s)
    s=re.sub(r"(^|[\s(=])[-−]("+NUM+r")\b",lambda m:m[1]+"minus "+decimal(m[2]),s)
    s=re.sub(r"\b"+NUM+r"\b",lambda m:decimal(m[0]),s)
    for a,b in {"≥":" at least ","≤":" at most ",">":" greater than ","<":" less than ","×":" times ","÷":" divided by ","=":" equals ","+":" plus ","~":" about ","&":" and ","%":" per cent ","_":" ","/":" slash "}.items():
        s=s.replace(a,b)
    return re.sub(r"\s+"," ",s).strip()

# spoken forms for the acronyms that actually occur in the dialogue
SAY={
 "LOS":"L O S", "EFSF":"E F S F", "ESM":"E S M", "PM\u00b2":"P M two", "PM2":"P M two",
 "PCCL":"P C C L", "ECCL":"E C C L", "PMSF":"P M S F", "SMSF":"S M S F", "SRF":"S R F",
 "RASCI":"rasky", "RfP":"R F P", "RfE":"R F E", "RfC":"R F C", "WBS":"W B S",
 "PSC":"P S C", "AGB":"A G B", "PCT":"P C T", "PSO":"P S O", "PQA":"P Q A",
 "DPC":"D P C", "LISO":"L I S O", "DMO":"D M O", "BIG":"B I G",
 "API":"A P I", "UI":"U I", "IT":"I T", "SWOT":"swot", "MoSCoW":"moscow",
 "TeCo":"Teh-co", "PrOw":"Pro-Ow", "ArOw":"Ar-Ow", "ATeM":"A team", "WIL":"W I L",
 "MVP":"M V P", "DoD":"D O D", "CIR":"C I R", "ISO":"I S O",
}

def decimal(x):
    x=str(x).replace(",", "")
    if "." in x:
        a,b=x.split(".",1)
        return cardinal(a)+" point "+" ".join(ONES[int(d)] for d in b)
    return cardinal(x)

# ---------- sentence splitting for speech ----------
ABBR={"mr","mrs","ms","dr","prof","st","no","vs","etc","e.g","i.e","approx"}
def sentences(t):
    t=re.sub(r"\s+"," ",t.strip())
    parts=re.split(r'(?<=[.!?])\s+(?=[“"A-Z0-9])', t)
    out=[]
    for p in parts:
        if out:
            prev=out[-1]
            w=re.split(r"[\s(]", prev.rstrip("."))[-1].lower()
            if w in ABBR:
                out[-1]=prev+" "+p; continue
        out.append(p)
    # split very long sentences at em dashes / semicolons so the model breathes sensibly
    final=[]
    for p in out:
        if len(p)>190:
            bits=re.split(r'(?<=[;:])\s+|\s+—\s+', p)
            buf=""
            for b in bits:
                if len(buf)+len(b)<170: buf=(buf+" "+b).strip()
                else:
                    if buf: final.append(buf)
                    buf=b
            if buf: final.append(buf)
        else: final.append(p)
    return [x for x in final if x.strip()]
