#!/usr/bin/env python3
"""Generate public/kk-swap.js from .kktmp data (full 24-member mapping + bios)."""
import json

bios = json.load(open(".kktmp/bios.json"))
fresh = json.load(open(".kktmp/fresh_cards.json"))

def js(s):
    return json.dumps(s, ensure_ascii=False)

import glob as _glob, os as _os

teams_files = {p: _os.path.basename(p) for p in _glob.glob("public/images/teams/*")}

def photo_file(b):
    """Find the local photo file for a member by slug (slug-name -> slug_name.ext)."""
    base = b["slug"].replace("-", "_")
    for p, name in teams_files.items():
        stem = _os.path.splitext(name)[0]
        if stem == base:
            return name
    # fallback: first file starting with slug prefix
    for name in teams_files.values():
        if _os.path.splitext(name)[0].startswith(base):
            return name
    return None

names = []
for i in range(min(24, len(bios), len(fresh))):
    b, f = bios[i], fresh[i]
    names.append({
        "old": f["name"].replace("&amp;", "&"),
        "new": b["name"],
        "oldRole": f["role"].replace("&amp;", "&"),
        "newRole": b["role"],
        "photo": photo_file(b),
        "bio": b.get("bio", ""),
    })

surplus_start = min(24, len(fresh))

data = {
    "NAMES": names,
    "SURPLUS": surplus_start,
    "TEXT": [
        # specific pairs FIRST (emails/domains), generic name pairs LAST
        ["info@momentolegal.com", "info@khuranaandkhurana.com"],
        ["INFO@MOMENTOLEGAL.COM", "INFO@KHURANAANDKHURANA.COM"],
        ["momentolegal.com", "khuranaandkhurana.com"],
        ["MOMENTOLEGAL.COM", "KHURANAANDKHURANA.COM"],
        ["Momento Legal Partners", "Khurana & Khurana"],
        ["MOMENTO LEGAL", "KHURANA & KHURANA"],
        ["Momento Legal", "Khurana & Khurana"],
        ["MOMENTO", "KHURANA & KHURANA"],
        ["The Moment of Precision", "Rendering Sage Legal Advice"],
        ["Law. Strategy. Timing.", "Law. Strategy. Precision."],
        ["Expertise Shaped for the Right Momento", "Expertise Shaped for Every Challenge"],
        ["Insights for Every Defining Momento", "Insights that Shape Decisions"],
        ["0212 890 80 55", "+91 89202 69831"],
        ["Istanbul / Turkey", "Delhi NCR / India"],
        ["ISTANBUL / TURKEY", "DELHI NCR / INDIA"],
        ["instagram.com/momentolegal", "instagram.com/khuranaandkhurana"],
        ["momento-legal-partners", "khurana-&-khurana-advocates-and-ip-attorneys"],
        ["Copyright © 2026 Momento Legal.", "Copyright © 2007-2026 Khurana & Khurana."],
        ["About Momento", "About Us"],
        ["Momento", "Moment"]
    ],
    "PAINT": [
        ["#000321", "#0d0a0c"], ["#000218", "#0b090a"], ["#000214", "#0a0808"],
        ["#05071c", "#120d0f"], ["#010320", "#140e10"], ["#0a1240", "#2b140f"],
        ["#10234f", "#3a1a12"], ["#000020", "#0d0a0c"]
    ],
}

JS = """/* Khurana & Khurana overlay — generated from scraped data. Text/images/colors only. */
(function () {
  "use strict";
  var DATA = __DATA__;
  var NAMES = DATA.NAMES, TEXT = DATA.TEXT, PAINT = DATA.PAINT, SURPLUS = DATA.SURPLUS;

  function mapStr(s) {
    var out = s;
    TEXT.forEach(function (p) { out = out.split(p[0]).join(p[1]); });
    NAMES.forEach(function (p) {
      out = out.split(p.old).join(p.new);
    });
    return out;
  }

  function swapText(root) {
    var w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null);
    var nodes = [];
    while (w.nextNode()) nodes.push(w.currentNode);
    for (var i = 0; i < nodes.length; i++) {
      var t = nodes[i].nodeValue;
      if (t && t.length > 2) {
        var out = mapStr(t);
        if (out !== t) nodes[i].nodeValue = out;
      }
    }
  }

  function rebuildHeadings(root) {
    root.querySelectorAll("h1, h2").forEach(function (h) {
      var nodes = [];
      var w = document.createTreeWalker(h, NodeFilter.SHOW_TEXT, null);
      while (w.nextNode()) nodes.push(w.currentNode);
      if (!nodes.length) return;
      var joined = nodes.map(function (n) { return n.nodeValue; }).join("");
      var mapped = mapStr(joined);
      if (mapped === joined) return;
      var per = Math.ceil(mapped.length / nodes.length);
      var k = 0;
      nodes.forEach(function (n) { n.nodeValue = mapped.slice(k, k + per); k += per; });
    });
  }

  function swapAttrs(root) {
    ["aria-label", "alt", "title", "content"].forEach(function (attr) {
      root.querySelectorAll("[" + attr + "]").forEach(function (el) {
        var v = el.getAttribute(attr);
        if (v && v.length > 2) {
          var o = mapStr(v);
          if (o !== v) el.setAttribute(attr, o);
        }
      });
    });
  }

  function swapLinks(root) {
    root.querySelectorAll('a[href*="momentolegal"], a[href*="momento-legal"]').forEach(function (a) {
      a.setAttribute("href", (a.getAttribute("href") || "")
        .replace("instagram.com/momentolegal", "instagram.com/khuranaandkhurana")
        .replace("momento-legal-partners", "khurana-&-khurana-advocates-and-ip-attorneys")
        .replace(/https?:\\/\\/(www\\.)?momentolegal\\.com/g, "https://khuranaandkhurana.com"));
    });
  }

  function repaint(root) {
    if (!root.querySelectorAll) return;
    root.querySelectorAll("[style]").forEach(function (el) {
      var s = el.getAttribute("style");
      if (s && s.indexOf("#") !== -1) {
        var o = s;
        PAINT.forEach(function (p) { o = o.split(p[0]).join(p[1]); });
        if (o !== s) el.setAttribute("style", o);
      }
    });
    root.querySelectorAll("style").forEach(function (st) {
      var c = st.textContent;
      if (c && c.indexOf("#") !== -1) {
        var o = c;
        PAINT.forEach(function (p) { o = o.split(p[0]).join(p[1]); });
        if (o !== c) st.textContent = o;
      }
    });
  }

  function swapCards(root) {
    var cards = root.querySelectorAll("button[aria-label^='View '][aria-label$=' details']");
    cards.forEach(function (btn, idx) {
      var label = btn.getAttribute("aria-label").replace(/^View /, "").replace(/ details$/, "");
      var m = null;
      for (var i = 0; i < NAMES.length; i++) if (NAMES[i].old === label || NAMES[i].new === label) { m = NAMES[i]; break; }
      if (idx >= SURPLUS || (label && !m && idx >= NAMES.length)) {
        var li = btn.closest("li") || btn;
        li.style.display = "none";
        return;
      }
      if (!m) return;
      btn.setAttribute("aria-label", "View " + m.new + " details");
      var ps = btn.querySelectorAll("p");
      if (ps[0]) ps[0].textContent = m.new;
      if (ps[1] && ps[1].textContent.trim() === m.oldRole) ps[1].textContent = m.newRole;
      var img = btn.querySelector("img");
      if (img) {
        img.setAttribute("src", "/images/teams/" + m.photo + "?v=4");
        img.removeAttribute("srcset");
        img.setAttribute("alt", m.new + " — " + m.newRole);
      }
    });
  }

  function fixLogos(root) {
    root.querySelectorAll('img[src*="header%2Flogo"], img[src*="header/logo"], img[alt="brand logo"]').forEach(function (img) {
      img.setAttribute("src", "/images/header/logo.png?v=4");
      img.removeAttribute("srcset");
    });
    root.querySelectorAll('img[src*="istcode"], img[alt*="Istcode"], a[href*="awwwards"], [class*="awwwards"]').forEach(function (el) {
      el.style.display = "none";
    });
  }

  function full() {
    var r = document.body || document.documentElement;
    if (!r) return;
    var dt = document.title;
    if (dt) { var t2 = mapStr(dt); if (t2 !== dt) document.title = t2; }
    swapText(r);
    rebuildHeadings(r);
    swapAttrs(r);
    swapLinks(r);
    repaint(r);
    swapCards(r);
    fixLogos(r);
  }

  var st = document.createElement("style");
  st.textContent = 'a[href*="awwwards"],[class*="awwwards"]{display:none!important}';
  document.head.appendChild(st);

  full();
  [500, 1500, 3000, 5000, 7500, 10000].forEach(function (d) { setTimeout(full, d); });
  document.addEventListener("DOMContentLoaded", full);
  window.addEventListener("load", full);

  var sweepTimer = null;
  function scheduleSweep() {
    if (sweepTimer) return;
    sweepTimer = setTimeout(function () { sweepTimer = null; full(); }, 400);
  }
  new MutationObserver(function (muts) {
    for (var i = 0; i < muts.length; i++) {
      var m = muts[i];
      if (m.type === "characterData") {
        var t = m.target.nodeValue || "";
        if (t.indexOf("Momento") !== -1 || t.indexOf("Korkmaz") !== -1 || t.indexOf("Yasan") !== -1 || t.indexOf("Kalkavan") !== -1) {
          var o = mapStr(t);
          if (o !== t) m.target.nodeValue = o;
        }
      } else if (m.addedNodes.length) {
        scheduleSweep();
        break;
      }
    }
  }).observe(document.body || document.documentElement, { childList: true, subtree: true, characterData: true });
})();
"""

JS = JS.replace("__DATA__", json.dumps(data, ensure_ascii=False))
open("public/kk-swap.js", "w", encoding="utf-8").write(JS)
print("kk-swap.js generated:", len(JS), "bytes,", len(names), "members, surplus from card", surplus_start)
