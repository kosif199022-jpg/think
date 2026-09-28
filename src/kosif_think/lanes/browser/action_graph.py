"""
Stable Semantic Action Graph for Jev-Browser.
Indexes interactive DOM elements, calculates FNV-1a stable hashes for persistent element IDs,
and maps numeric badges for ultra-fast action selection.
"""

from typing import Dict, Any, List, Optional

INDEX_JS = r"""(() => {
  const vis = e => {
    const r = e.getBoundingClientRect(), s = getComputedStyle(e);
    return r.width > 2 && r.height > 2 && s.display !== 'none' && s.visibility !== 'hidden' && +s.opacity > .05;
  };
  const sel = [
    'a[href]', 'button', 'input:not([type=hidden])', 'textarea', 'select',
    '[role=button]', '[role=link]', '[role=tab]', '[role=menuitem]', '[role=checkbox]',
    '[role=radio]', '[role=combobox]', '[role=searchbox]', '[tabindex]:not([tabindex="-1"])', '[onclick]'
  ].join(',');
  const cand = [...document.querySelectorAll(sel)].filter(vis).slice(0, 220);
  const fnv = s => {
    let h = 2166136261;
    for (let i = 0; i < s.length; i++) {
      h ^= s.charCodeAt(i);
      h = Math.imul(h, 16777619);
    }
    return (h >>> 0).toString(36);
  };
  const used = new Map(), out = [];
  for (const e of cand) {
    const r = e.getBoundingClientRect(), role = e.getAttribute('role') || e.tagName.toLowerCase();
    const label = (e.getAttribute('aria-label') || e.placeholder || e.innerText || e.textContent || e.name || '').replace(/\s+/g, ' ').trim().slice(0, 100);
    const href = e.href ? (() => { try { return new URL(e.href).pathname } catch { return e.href } })() : '';
    const sig = [e.tagName, role, e.name || '', e.placeholder || '', label, href, e.type || ''].join('|');
    const h = fnv(sig), n = (used.get(h) || 0) + 1; used.set(h, n);
    const id = 'a_' + h + (n > 1 ? '_' + n : '');
    e.setAttribute('data-kosif-action', id);
    out.push({
      id,
      tag: e.tagName.toLowerCase(),
      role,
      text: label,
      name: e.name || null,
      placeholder: e.placeholder || null,
      type: e.type || null,
      href: href || null,
      disabled: !!e.disabled,
      checked: typeof e.checked === 'boolean' ? e.checked : null,
      in_viewport: r.bottom > 0 && r.right > 0 && r.top < innerHeight && r.left < innerWidth,
      rect: { x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height) }
    });
  }
  return {
    url: location.href,
    title: document.title,
    text: (document.body?.innerText || '').slice(0, 14000),
    viewport: { w: innerWidth, h: innerHeight, scrollX, scrollY },
    count: out.length,
    elements: out
  };
})()"""


class ActionGraph:
    """Manages the semantic action graph of browser elements."""

    def __init__(self):
        self._last_snapshot: Dict[str, Any] = {}
        self._id_map: Dict[int, str] = {}
        self._stable_map: Dict[str, int] = {}

    def build_graph(self, raw_elements: List[Dict[str, Any]], url: str = "", title: str = "") -> Dict[str, Any]:
        """Maps raw indexed elements to numeric aliases and stable action IDs."""
        self._id_map.clear()
        self._stable_map.clear()
        mapped_elements = []

        for idx, el in enumerate(raw_elements, 1):
            stable_id = str(el.get("id") or f"el_{idx}")
            self._id_map[idx] = stable_id
            self._stable_map[stable_id] = idx
            
            entry = dict(el)
            entry["numeric_id"] = idx
            entry["stable_id"] = stable_id
            mapped_elements.append(entry)

        graph = {
            "url": url,
            "title": title,
            "count": len(mapped_elements),
            "elements": mapped_elements
        }
        self._last_snapshot = graph
        return graph

    def resolve_target(self, identifier: Any) -> Optional[str]:
        """Resolves either a numeric ID or a stable action_id into the authoritative selector."""
        try:
            num = int(identifier)
            return self._id_map.get(num)
        except (ValueError, TypeError):
            return str(identifier)
