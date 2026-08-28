# -*- coding: utf-8 -*-
"""Speech text normaliser: turn every digit form in the dialogue into words that
espeak-ng reads in one breath, so Piper never breaks inside a number."""
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
    n=int(n)
    if n<0: return "minus "+cardinal(-n)
    if n<1000: return u999(n)
    if n<1000000:
        t,r=divmod(n,1000)
        return u999(t)+" thousand"+(" "+u999(r) if r else "")
    m,r=divmod(n,1000000)
    return u999(m)+" million"+(" "+cardinal(r) if r else "")

ORD={1:"first",2:"second",3:"third",5:"fifth",8:"eighth",9:"ninth",12:"twelfth"}
def ordinal(n):
    n=int(n)
    if n in ORD: return ORD[n]
    if n<20: return ONES[n]+"th"
    t,o=divmod(n,10)
    if o==0: return TENS[t][:-1]+"ieth"
    return TENS[t]+"-"+ordinal(o)

def year(n):
    n=int(n)
    if 1100<=n<=1999 or 2000<=n<=2099:
        hi,lo=divmod(n,100)
        if lo==0:  return cardinal(hi)+" hundred"
        if lo<10:  return cardinal(hi)+" oh "+ONES[lo]      # 2005 -> twenty oh five
        return cardinal(hi)+" "+u99(lo)                      # 2028 -> twenty twenty-eight
    return cardinal(n)

MONTH=r"(?:January|February|March|April|May|June|July|August|September|October|November|December)"

def norm(t):
    s=" "+t+" "
    # 1. clock times  09:41 / 16:20 / 9.30
    def clock(m):
        h,mi=int(m.group(1)),int(m.group(2))
        if mi==0:  return u99(h)+" hundred hours" if h>=13 else u99(h)+" o'clock"
        if mi<10:  return u99(h)+" oh "+ONES[mi]
        return u99(h)+" "+u99(mi)
    s=re.sub(r"\b(\d{1,2}):([0-5]\d)\b", clock, s)
    # 2. money  €8.4 m / €1.2 bn / €250,000
    def money(m):
        num=m.group(1).replace(",","")
        unit=(m.group(2) or "").lower()
        w=decimal(num)
        if unit in("m","million"): return w+" million euro"
        if unit in("bn","billion"): return w+" billion euro"
        if unit in("k",): return w+" thousand euro"
        return w+" euro"
    s=re.sub(r"€\s?([\d,]+(?:\.\d+)?)\s*(bn|billion|million|m|k)?\b", money, s, flags=re.I)
    # 3. percentages
    s=re.sub(r"\b([\d,]+(?:\.\d+)?)\s*%", lambda m: decimal(m.group(1).replace(",",""))+" per cent", s)
    # 4. lettered ids  R-07 -> "R oh seven"   I-14 -> "I fourteen"   CR-014 -> "C R oh fourteen"
    def lid(m):
        letters=" ".join(list(m.group(1).upper()))
        d=m.group(2)
        if d.startswith("0"): return letters+" oh "+cardinal(d.lstrip("0") or "0")
        return letters+" "+cardinal(d)
    s=re.sub(r"\b([A-Z]{1,3})-(\d{1,3})\b", lid, s)
    s=re.sub(r"\b(SC|AC|WP|CR)(\d{1,3})\b", lambda m: " ".join(list(m.group(1)))+" "+cardinal(m.group(2)), s)
    # 5. dates  15 May 2028 / May 2028
    s=re.sub(r"\b(\d{1,2})\s+("+MONTH+r")\s+(\d{4})\b",
             lambda m: "the "+ordinal(m.group(1))+" of "+m.group(2)+" "+year(m.group(3)), s)
    s=re.sub(r"\b("+MONTH+r")\s+(\d{4})\b", lambda m: m.group(1)+" "+year(m.group(2)), s)
    s=re.sub(r"\b(\d{1,2})\s+("+MONTH+r")\b", lambda m: "the "+ordinal(m.group(1))+" of "+m.group(2), s)
    # 6. version / section numbers  v1.0  4.11  3.1
    s=re.sub(r"\bv(\d+)\.(\d+)\b", lambda m: "version "+cardinal(m.group(1))+" point "+cardinal(m.group(2)), s)
    s=re.sub(r"\b(\d{1,2})\.(\d{1,2})\.(\d{1,2})\b",
             lambda m: " point ".join(cardinal(x) for x in m.groups()), s)
    s=re.sub(r"(?<![\d.])\b(\d{1,2})\.(\d{1,2})\b(?!\d)",
             lambda m: cardinal(m.group(1))+" point "+cardinal(m.group(2)), s)
    # 7. bare years
    s=re.sub(r"\b(1[89]\d{2}|20\d{2})\b", lambda m: year(m.group(1)), s)
    # 8. remaining plain integers, with thousands separators
    s=re.sub(r"\b(\d{1,3}(?:,\d{3})+)\b", lambda m: cardinal(m.group(1).replace(",","")), s)
    s=re.sub(r"\b(\d+)\b", lambda m: cardinal(m.group(1)), s)
    # 9. symbols and acronyms the model reads badly
    s=s.replace("~"," about ").replace("&"," and ").replace("%"," per cent ")
    for a,b in SAY.items():
        s=re.sub(r"\b"+re.escape(a)+r"\b", b, s)
    # tidy
    s=re.sub(r"\s+"," ",s).strip()
    return s

# spoken forms for the acronyms that actually occur in the dialogue
SAY={
 "LOS":"L O S", "EFSF":"E F S F", "ESM":"E S M", "PM\u00b2":"P M two", "PM2":"P M two",
 "PCCL":"P C C L", "ECCL":"E C C L", "PMSF":"P M S F", "SMSF":"S M S F", "SRF":"S R F",
 "RASCI":"rasky", "RfP":"R f P", "RfE":"R f E", "RfC":"R f C", "WBS":"W B S",
 "PSC":"P S C", "AGB":"A G B", "PCT":"P C T", "PSO":"P S O", "PQA":"P Q A",
 "DPC":"D P C", "LISO":"L I S O", "DMO":"D M O", "BIG":"B I G",
 "API":"A P I", "UI":"U I", "IT":"I T", "SWOT":"swot", "MoSCoW":"moscow",
 "TeCo":"Teh-co", "PrOw":"Pro-Ow", "ArOw":"Ar-Ow", "ATeM":"A team", "WIL":"W I L",
 "MVP":"M V P", "DoD":"D o D", "CIR":"C I R", "ISO":"I S O",
}

def decimal(x):
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
