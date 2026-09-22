#!/usr/bin/env python3
"""Robustness calibration for ENTITY_RESOLUTION_V2.

Uses current public discovery media/text and controlled repost-like transformations.
This is not a substitute for real cross-surface labels; it only calibrates tolerance
to crop/border/recompression/text truncation and checks false-merge risk.
"""
import io, json, math, statistics, urllib.request
from PIL import Image, ImageOps, ImageDraw
from envelope_v2 import _phash_image, image_phash_views, simhash64, text_tokens

LATEST="https://raw.githubusercontent.com/arascxe/h40-graac-canary/premint-discovery-data-v2/latest.json"
UA="Mozilla/5.0"

def get(url, limit=4_000_000):
    req=urllib.request.Request(url,headers={"User-Agent":UA})
    with urllib.request.urlopen(req,timeout=12) as r:
        return r.read(limit)

def hd(a,b):
    if not a or not b: return None
    return sum(x!=y for x,y in zip(a,b))

def views_from_image(src):
    src=src.convert("RGB")
    w,h=src.size
    out={"full":_phash_image(src)}
    dx,dy=int(w*.10),int(h*.10)
    out["center"]=_phash_image(src.crop((dx,dy,w-dx,h-dy))) if w-2*dx>=16 and h-2*dy>=16 else None
    side=min(w,h); left=(w-side)//2; top=(h-side)//2
    out["square"]=_phash_image(src.crop((left,top,left+side,top+side))) if side>=16 else None
    return out

def min_view_hd(a,b):
    vals=[hd(x,y) for x in a.values() for y in b.values() if x and y]
    return min(vals) if vals else None

def transforms(img):
    img=img.convert("RGB")
    w,h=img.size
    out={}
    out["recompress_resize"]=img.resize((max(64,w//2),max(64,h//2)),Image.Resampling.LANCZOS)
    dx,dy=int(w*.10),int(h*.10)
    if w-2*dx>=32 and h-2*dy>=32: out["crop10"]=img.crop((dx,dy,w-dx,h-dy))
    dx2,dy2=int(w*.20),int(h*.20)
    if w-2*dx2>=32 and h-2*dy2>=32: out["crop20"]=img.crop((dx2,dy2,w-dx2,h-dy2))
    border=max(8,int(min(w,h)*.08))
    out["border"]=ImageOps.expand(img,border=border,fill="white")
    # Caption-like lower band.
    cap=Image.new("RGB",(w,h+max(24,int(h*.15))),"white")
    cap.paste(img,(0,0))
    out["caption_band"]=cap
    return out

def text_variants(text):
    toks=text_tokens(text,limit=40)
    if not toks: return {}
    out={}
    out["drop_last20"]=" ".join(toks[:max(1,int(len(toks)*.8))])
    out["drop_first20"]=" ".join(toks[max(0,int(len(toks)*.2)):])
    out["append_boilerplate"]=" ".join(toks)+" watch full video source comments"
    out["keep_core60"]=" ".join(toks[:max(2,int(len(toks)*.6))])
    return out

payload=json.loads(get(LATEST).decode())
items=payload.get("items") or []
image_items=[x for x in items if x.get("media_url")][:16]
text_items=[x for x in items if len(text_tokens(x.get("text") or ""))>=5][:80]

image_rows=[]
for item in image_items:
    try:
        src=Image.open(io.BytesIO(get(item["media_url"]))).convert("RGB")
        base=views_from_image(src)
        for kind,timg in transforms(src).items():
            tv=views_from_image(timg)
            image_rows.append({
                "kind":kind,
                "full_hd":hd(base["full"],tv["full"]),
                "multiview_hd":min_view_hd(base,tv),
            })
    except Exception:
        pass

text_rows=[]
for item in text_items:
    base=simhash64(text_tokens(item.get("text") or "",limit=40))
    for kind,var in text_variants(item.get("text") or "").items():
        vv=simhash64(text_tokens(var,limit=40))
        d=hd(base,vv)
        if d is not None: text_rows.append({"kind":kind,"hd":d})

def summarize(rows,key,thresholds):
    out={}
    vals=[r[key] for r in rows if r.get(key) is not None]
    out["n"]=len(vals)
    if vals:
        vals=sorted(vals)
        out["median"]=statistics.median(vals)
        out["p90"]=vals[min(len(vals)-1,math.ceil(.9*len(vals))-1)]
        out["max"]=max(vals)
        out["recall"]={str(t):round(sum(v<=t for v in vals)/len(vals),4) for t in thresholds}
    return out

result={
  "schema":"entity_resolution_robustness_v2",
  "generated_at":payload.get("generated_at"),
  "image_full":summarize(image_rows,"full_hd",[4,8,12,16]),
  "image_multiview":summarize(image_rows,"multiview_hd",[4,8,12,16]),
  "image_by_transform":{},
  "text":summarize(text_rows,"hd",[4,6,8,10,12,16]),
  "text_by_transform":{},
  "warning":"Controlled-transform robustness only; real cross-surface labels remain required."
}
for kind in sorted({r["kind"] for r in image_rows}):
    rr=[r for r in image_rows if r["kind"]==kind]
    result["image_by_transform"][kind]={
      "full":summarize(rr,"full_hd",[4,8,12,16]),
      "multiview":summarize(rr,"multiview_hd",[4,8,12,16]),
    }
for kind in sorted({r["kind"] for r in text_rows}):
    result["text_by_transform"][kind]=summarize([r for r in text_rows if r["kind"]==kind],"hd",[4,6,8,10,12,16])

print(json.dumps(result,ensure_ascii=False))
