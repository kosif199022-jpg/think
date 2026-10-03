"""Unified KOSIF Think browser/Jev lane.

Design goals:
- Stable semantic action IDs instead of transient DOM indices.
- Local deterministic ranking first.
- Jev only for bounded ambiguity among observed candidates.
- Revalidate before a side effect.
- Verify observable state changes; FINISH is never proof of completion.
- Cancellation is checked before every write.
"""
from __future__ import annotations

import hashlib
import json
import re
import threading
import time
import urllib.request
from collections import deque
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

RUN_URL = "http://127.0.0.1:18766/run"
HEALTH_URL = "http://127.0.0.1:18766/health"

_LOCK = threading.RLock()
_HISTORY: deque = deque(maxlen=120)
_LAST_GRAPH: Dict[str, Any] = {}
_PREV_GRAPH: Dict[str, Any] = {}
_CANCELLED = False

_RISK_WORDS = re.compile(
    r"\b(pay|payment|purchase|buy|checkout|delete|remove|publish|send|submit|transfer|merge|commit|password|credential|security|billing|subscribe)\b|"
    r"(ادفع|دفع|شراء|حذف|احذف|نشر|انشر|إرسال|ارسل|أرسل|تحويل|ادمج|كلمة مرور|بيانات الدخول|أمان|فاتورة|اشتراك)",
    re.I,
)
_HUMAN_WORDS = re.compile(
    r"captcha|recaptcha|verify you are human|security check|one[- ]time|verification code|otp|2fa|mfa|"
    r"تحقق أنك إنسان|أنا لست روبوت|رمز التحقق|رمز لمرة واحدة|المصادقة الثنائية",
    re.I,
)

_INTERACTIVE_JS = r"""
(() => {
  const qs = ['a[href]','button','input:not([type="hidden"])','select','textarea',
    '[role="button"]','[role="link"]','[role="tab"]','[role="menuitem"]',
    '[role="checkbox"]','[role="radio"]','[role="combobox"]','[role="searchbox"]',
    '[contenteditable="true"]','[tabindex]:not([tabindex="-1"])','[onclick]'].join(',');
  const nodes = [...new Set(Array.from(document.querySelectorAll(qs)))];
  const out=[];
  function cssPath(el){
    if(el.id) return '#'+CSS.escape(el.id);
    const parts=[]; let cur=el;
    for(let d=0;cur&&cur.nodeType===1&&d<7;d++,cur=cur.parentElement){
      let p=cur.tagName.toLowerCase(); const parent=cur.parentElement;
      if(parent){const same=Array.from(parent.children).filter(x=>x.tagName===cur.tagName);if(same.length>1)p+=':nth-of-type('+(same.indexOf(cur)+1)+')';}
      parts.unshift(p); if(p==='body'||p==='html')break;
    }
    return parts.join(' > ');
  }
  for(const el of nodes){
    const r=el.getBoundingClientRect(), s=getComputedStyle(el);
    if(r.width<=2||r.height<=2||s.display==='none'||s.visibility==='hidden'||Number(s.opacity||1)<0.05) continue;
    let label=el.getAttribute('aria-label')||el.innerText||el.textContent||el.placeholder||el.name||'';
    label=String(label).replace(/\s+/g,' ').trim().slice(0,180);
    out.push({tag:el.tagName.toLowerCase(),role:el.getAttribute('role')||'',text:label,name:el.getAttribute('name')||'',type:el.getAttribute('type')||'',aria:el.getAttribute('aria-label')||'',placeholder:el.getAttribute('placeholder')||'',href:el.href||'',value:('value'in el)?String(el.value||'').slice(0,180):'',checked:('checked'in el)?!!el.checked:null,disabled:!!el.disabled,in_viewport:r.bottom>0&&r.right>0&&r.top<innerHeight&&r.left<innerWidth,selector:cssPath(el),rect:{x:Math.round(r.left+scrollX),y:Math.round(r.top+scrollY),width:Math.round(r.width),height:Math.round(r.height)}});
    if(out.length>=220) break;
  }
  const dialogs=Array.from(document.querySelectorAll('[role="dialog"],dialog,[aria-modal="true"]')).slice(0,12).map(el=>({text:(el.innerText||'').replace(/\s+/g,' ').trim().slice(0,1000),selector:cssPath(el)}));
  return {url:location.href,title:document.title,body_text:(document.body?.innerText||'').replace(/\s+/g,' ').trim().slice(0,30000),dialogs,elements:out};
})()
"""


def _params(args: Any) -> Dict[str, Any]:
    if not args:
        return {}
    if isinstance(args, dict):
        return args
    if isinstance(args, list) and args:
        args = args[0]
    try:
        return json.loads(args)
    except Exception:
        return {"value": args}


def _post(actions: List[Dict[str, Any]], timeout: float = 10.0) -> Dict[str, Any]:
    raw = json.dumps({"actions": actions}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(RUN_URL, data=raw, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def _norm(value: Any, limit: int = 240) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()[:limit]


def _url_key(url: str) -> str:
    try:
        u = urlparse(url)
        return f"{u.scheme}://{u.netloc}{u.path}"
    except Exception:
        return url


def _stable_id(node: Dict[str, Any], page_url: str, occurrence: int) -> str:
    payload = {
        "page": _url_key(page_url), "tag": _norm(node.get("tag"), 30).lower(),
        "role": _norm(node.get("role"), 40).lower(), "text": _norm(node.get("text"), 120).lower(),
        "name": _norm(node.get("name"), 80).lower(), "type": _norm(node.get("type"), 40).lower(),
        "aria": _norm(node.get("aria"), 120).lower(), "placeholder": _norm(node.get("placeholder"), 120).lower(),
        "href": _url_key(_norm(node.get("href"), 300)), "occurrence": occurrence,
    }
    return "a_" + hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]


def _fingerprint(graph: Dict[str, Any]) -> str:
    basis = {"url": graph.get("url", ""), "title": graph.get("title", ""),
             "nodes": [(n.get("id"), n.get("text"), n.get("value"), n.get("checked")) for n in graph.get("nodes", [])[:100]]}
    return hashlib.sha256(json.dumps(basis, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:20]


def build_stable_graph(raw: Dict[str, Any]) -> Dict[str, Any]:
    url = str(raw.get("url", "")); seen: Dict[str, int] = {}; nodes=[]
    for source in raw.get("elements") or []:
        key = "|".join(_norm(source.get(k), 140).lower() for k in ("tag","role","text","name","type","aria","placeholder","href"))
        occ = seen.get(key, 0); seen[key] = occ + 1
        node = dict(source); node["id"] = _stable_id(source, url, occ); node["occurrence"] = occ; nodes.append(node)
    graph = {"url": url, "title": raw.get("title", ""), "body_text": raw.get("body_text", ""),
             "dialogs": raw.get("dialogs") or [], "count": len(nodes), "nodes": nodes, "captured_at": time.time()}
    graph["fingerprint"] = _fingerprint(graph)
    return graph


def snapshot() -> Dict[str, Any]:
    global _LAST_GRAPH, _PREV_GRAPH
    r = _post([{"op":"eval","expression":_INTERACTIVE_JS}], timeout=8)
    results = r.get("results") or []
    if not results or not isinstance(results[0], dict):
        return {"ok":False,"error":"browser_snapshot_invalid"}
    graph = build_stable_graph(results[0])
    with _LOCK:
        _PREV_GRAPH, _LAST_GRAPH = _LAST_GRAPH, graph
    return {"ok":True, **graph}


def _tokens(text: str) -> List[str]:
    stop={"the","and","for","with","this","that","من","في","على","الى","إلى","عن","هذا","هذه","ثم"}
    return [t for t in re.findall(r"[\w\u0600-\u06ff]+", (text or "").lower()) if len(t)>1 and t not in stop][:40]


def _score_node(goal: str, node: Dict[str, Any]) -> float:
    blob=" ".join(str(node.get(k) or "") for k in ("text","aria","placeholder","name","href","role","tag")).lower()
    score=sum(10.0 for tok in _tokens(goal) if tok in blob)
    g=(goal or "").lower(); tag=(node.get("tag") or "").lower(); role=(node.get("role") or "").lower()
    if re.search(r"type|enter|search|find|write|اكتب|ادخل|أدخل|ابحث", g, re.I) and (tag in {"input","textarea"} or role in {"textbox","searchbox","combobox"}): score += 18
    if re.search(r"click|open|select|choose|press|continue|next|اضغط|افتح|اختر|اختار|تابع|التالي", g, re.I) and (tag in {"a","button"} or role in {"button","link","tab","menuitem"}): score += 10
    if node.get("disabled"): score -= 50
    if not node.get("in_viewport"): score -= 3
    return score


def assess(goal: str, graph: Optional[Dict[str, Any]]=None, max_candidates: int=8) -> Dict[str, Any]:
    if graph is None:
        graph=snapshot()
    if not graph.get("ok", True): return graph
    scored=sorted([(_score_node(goal,n),n) for n in graph.get("nodes",[])], key=lambda x:x[0], reverse=True)
    top=[x for x in scored if x[0]>0][:max(1,min(20,max_candidates))]
    best=top[0][0] if top else 0; second=top[1][0] if len(top)>1 else 0; gap=best-second
    needs_jev=(not top) or best<16 or (len(top)>1 and gap<7)
    return {"ok":True,"needs_jev":needs_jev,"best_score":best,"score_gap":gap,
            "recommended_id":top[0][1].get("id") if top and not needs_jev else None,
            "candidates":[{"id":n.get("id"),"score":s,"description":_norm(f"[{n.get('tag')}/{n.get('role')}] {n.get('text') or n.get('aria') or n.get('placeholder') or n.get('name')} {n.get('href')}",360),"node":n} for s,n in top],
            "graph_fingerprint":graph.get("fingerprint")}


def decision_packet(goal: str, graph: Optional[Dict[str, Any]]=None) -> Dict[str, Any]:
    a=assess(goal, graph)
    if not a.get("ok"): return a
    return {"ok":True,"type":"choice","instructions":"Choose exactly one observed stable action ID. Do not invent selectors or actions.",
            "state":{"goal":goal,"graph_fingerprint":a.get("graph_fingerprint")},
            "criteria":{c["id"]:c["description"] for c in a.get("candidates",[])},"needs_jev":a.get("needs_jev")}


def _risk(node: Optional[Dict[str, Any]], operation: str, text: str="") -> Dict[str, Any]:
    blob=" ".join([operation,text,_norm(node or {},500)])
    risky=bool(_RISK_WORDS.search(blob))
    return {"risk":"consequential" if risky else "low","approval_required":risky}


def _find_node(action_id: str, graph: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    return next((n for n in graph.get("nodes",[]) if n.get("id")==action_id), None)


def _similarity(a: Dict[str, Any], b: Dict[str, Any]) -> float:
    score=0.0
    for k,w in (("tag",1),("role",1),("name",2),("type",1),("aria",4),("placeholder",3),("text",5),("href",3)):
        av=_norm(a.get(k),200).lower(); bv=_norm(b.get(k),200).lower()
        if av and bv:
            if av==bv: score+=w
            elif av in bv or bv in av: score+=w*.55
    return score


def recover(action_id: str, old_graph: Optional[Dict[str, Any]]=None, new_graph: Optional[Dict[str, Any]]=None) -> Dict[str, Any]:
    old_graph=old_graph or _PREV_GRAPH or _LAST_GRAPH
    if not old_graph: return {"ok":False,"error":"no_prior_graph"}
    old=_find_node(action_id, old_graph)
    if not old: return {"ok":False,"error":"old_target_not_found","id":action_id}
    new_graph=new_graph or snapshot()
    exact=_find_node(action_id,new_graph)
    if exact: return {"ok":True,"id":action_id,"recovered":False,"node":exact,"score":99.0}
    candidates=sorted([(_similarity(old,n),n) for n in new_graph.get("nodes",[])],key=lambda x:x[0],reverse=True)
    if not candidates or candidates[0][0]<4: return {"ok":False,"error":"recovery_confidence_low","id":action_id}
    return {"ok":True,"id":candidates[0][1].get("id"),"recovered":True,"node":candidates[0][1],"score":candidates[0][0]}


def analyze(graph: Optional[Dict[str, Any]]=None) -> Dict[str, Any]:
    graph=graph or snapshot()
    text=" ".join([str(graph.get("title") or ""),str(graph.get("body_text") or "")," ".join(d.get("text","") for d in graph.get("dialogs",[]))])
    human=bool(_HUMAN_WORDS.search(text))
    return {"ok":True,"human_checkpoint":human,"dialogs":graph.get("dialogs",[]),"fingerprint":graph.get("fingerprint"),"recommended_mode":"human" if human else "action_graph"}


def execute(action_id: Optional[str], operation: str, text: str="", approved: bool=False) -> Dict[str, Any]:
    global _CANCELLED
    with _LOCK:
        if _CANCELLED: return {"ok":False,"cancelled":True,"error":"cancelled_before_side_effect"}
    pre=snapshot(); node=_find_node(action_id,pre) if action_id else None
    if action_id and not node:
        rec=recover(action_id,_PREV_GRAPH,pre)
        if not rec.get("ok"): return rec
        node=rec.get("node"); action_id=rec.get("id")
    risk=_risk(node,operation,text)
    if risk["approval_required"] and not approved:
        return {"ok":False,"approval_required":True,**risk,"id":action_id,"operation":operation}
    op=operation.upper()
    if op=="FINISH": return {"ok":True,"hypothesis_only":True,"operation":"FINISH"}
    if op=="CLICK" and node:
        raw=_post([{"op":"click","selector":node["selector"],"force":True}],8)
    elif op=="TYPE" and node:
        raw=_post([{"op":"fill","selector":node["selector"],"value":text}],8)
    elif op=="SCROLL_DOWN": raw=_post([{"op":"scroll","delta":500}],6)
    elif op=="SCROLL_UP": raw=_post([{"op":"scroll","delta":-500}],6)
    elif op=="GO_BACK": raw=_post([{"op":"eval","expression":"history.back(); true"}],6)
    else: return {"ok":False,"error":"unsupported_operation","operation":op}
    post=snapshot(); changed=pre.get("fingerprint")!=post.get("fingerprint")
    with _LOCK: _HISTORY.append({"ts":time.time(),"operation":op,"target_id":action_id,"changed":changed,"pre_fingerprint":pre.get("fingerprint"),"post_fingerprint":post.get("fingerprint")})
    return {"ok":bool(raw.get("ok",True)),"operation":op,"id":action_id,"changed":changed,"post":{"url":post.get("url"),"title":post.get("title"),"fingerprint":post.get("fingerprint")}}


def dispatch(action: str, args: Any) -> Dict[str, Any]:
    global _CANCELLED
    p=_params(args); a=str(action or "").lower()
    try:
        if a in {"snapshot","graph","action_space"}: return snapshot()
        if a=="analyze": return analyze()
        if a in {"assess","plan"}: return assess(str(p.get("goal") or p.get("task") or p.get("value") or ""),max_candidates=int(p.get("max_candidates",8)))
        if a=="decision_packet": return decision_packet(str(p.get("goal") or p.get("task") or ""))
        if a=="execute": return execute(p.get("id"),str(p.get("operation") or "CLICK"),str(p.get("text") or ""),bool(p.get("approved",False)))
        if a=="recover": return recover(str(p.get("id") or ""))
        if a in {"history","trace","events"}: return {"ok":True,"history":list(_HISTORY),"cancelled":_CANCELLED}
        if a=="cancel":
            with _LOCK: _CANCELLED=True
            return {"ok":True,"cancelled":True}
        if a=="reset_cancel":
            with _LOCK: _CANCELLED=False
            return {"ok":True,"cancelled":False}
        if a=="status":
            with urllib.request.urlopen(HEALTH_URL,timeout=2) as r: health=json.load(r)
            return {"ok":bool(health.get("ok")),"browser":health,"cancelled":_CANCELLED,"history_size":len(_HISTORY)}
        return {"ok":False,"error":"unknown_browserjev_action","action":a}
    except Exception as e:
        return {"ok":False,"error":type(e).__name__}
