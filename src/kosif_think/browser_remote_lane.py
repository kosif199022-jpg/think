"""Deterministic KOSIF browserremote lane.
No Jev/model calls. Reuses the authenticated persistent KOSIF browser controller.
"""
from __future__ import annotations
import json, os, urllib.request
from pathlib import Path
from typing import Any, Dict

RUN_URL="http://127.0.0.1:18766/run"
HEALTH_URL="http://127.0.0.1:18766/health"

def _p(args):
    if not args:return {}
    if isinstance(args,dict):return args
    if isinstance(args,list):
        if not args:return {}
        if isinstance(args[0],dict):return args[0]
        try:return json.loads(args[0])
        except Exception:return {"value":args[0]}
    try:return json.loads(args)
    except Exception:return {"value":args}

def _post(actions,timeout=12):
    raw=json.dumps({"actions":actions},ensure_ascii=False).encode("utf-8")
    req=urllib.request.Request(RUN_URL,data=raw,headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=timeout) as r:return json.load(r)

def _health(timeout=2):
    with urllib.request.urlopen(HEALTH_URL,timeout=timeout) as r:return json.load(r)

def dispatch(action,args):
    p=_p(args); a=str(action or "").lower()
    try:
        if a=="info":return {"ok":True,"browser":_health()}
        if a=="tabs":return _post([{"op":"listPages"}])
        if a=="new_tab":return _post([{"op":"newPage","url":str(p.get("url") or "about:blank")}])
        if a=="switch_tab":return _post([{"op":"switchPage","index":int(p.get("index",0))}])
        if a=="close_tab":return _post([{"op":"closePage","index":int(p.get("index",0))}])
        if a in {"click_pct","touch_pct","pointer_pct"}:
            return _post([{"op":"mousePct","xPct":float(p.get("x",p.get("xPct",50))),"yPct":float(p.get("y",p.get("yPct",50)))}])
        if a=="type":return _post([{"op":"keyboardType","value":str(p.get("text") or ""),"enter":bool(p.get("enter",False))}])
        if a=="key":return _post([{"op":"keyboardKey","key":str(p.get("key") or "Enter")}])
        if a=="scroll":
            delta=int(p.get("delta",p.get("amount",450)))
            if str(p.get("direction","down")).lower()=="up":delta=-abs(delta)
            return _post([{"op":"scroll","delta":delta}])
        if a=="zoom":
            factor=max(.25,min(3.0,float(p.get("factor",1.0))))
            return _post([{"op":"eval","expression":f"document.documentElement.style.zoom={json.dumps(str(factor))}; true"}])
        if a=="extract":
            limit=max(1000,min(100000,int(p.get("limit",30000))))
            expr=f"(()=>({{url:location.href,title:document.title,text:(document.body?.innerText||'').slice(0,{limit}),links:[...document.querySelectorAll('a[href]')].slice(0,300).map(a=>({{text:(a.innerText||'').trim().slice(0,180),href:a.href}}))}}))()"
            return _post([{"op":"eval","expression":expr}])
        if a=="screenshot":
            out=Path(str(p.get("path") or (Path(os.environ.get("LOCALAPPDATA","."))/"KOSIF"/"browserremote.png")))
            out.parent.mkdir(parents=True,exist_ok=True)
            r=_post([{"op":"screenshot","path":str(out),"fullPage":bool(p.get("full_page",False))}])
            return {"ok":bool(r.get("ok",True)),"path":str(out),"raw":r}
        if a=="pdf":
            return {"ok":False,"error":"route_to_devtools_print_to_pdf","note":"Use the persistent Chrome DevTools Page.printToPDF lane; do not add a second browser runtime."}
        return {"ok":False,"error":"unknown_browserremote_action","action":a}
    except Exception as e:
        return {"ok":False,"error":type(e).__name__}
