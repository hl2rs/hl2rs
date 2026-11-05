#!/usr/bin/env python3
"""Generate the animated SVG artwork used by README.md.

    python scripts/build_assets.py

Every SVG is self-contained: tech icons are downloaded at build time from
skillicons.dev (MIT) and simple-icons (CC0) and inlined. GitHub renders README
images through <img>, which blocks web fonts and scripts, so the artwork relies
on system font stacks plus CSS/SMIL animation only.
"""
import html
import math
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
SKILL_ICONS = "https://skillicons.dev/icons?i={}&theme=dark"
# Pinned to 9.x: later releases dropped several brand icons used here (Tableau, Canva, InDesign, ...).
SIMPLE_ICONS = "https://cdn.jsdelivr.net/npm/simple-icons@9.21.0/icons/{}.svg"

SANS = "'Segoe UI', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "'Cascadia Code', 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"

VIOLET, SKY, TEAL, PINK, AMBER, CORAL = "#7F5AF0", "#2CB1FF", "#00C9A7", "#FF5FA2", "#FFB547", "#FF5F6D"


# ── helpers ──────────────────────────────────────────────────────────────────

def esc(value):
    return html.escape(str(value), quote=True)


def rule(selector, body):
    return selector + "{" + body + "}"


def keyframes(name, frames):
    return "@keyframes " + name + "{" + "".join(rule(k, v) for k, v in frames) + "}"


BASE_CSS = (
    rule("text", "font-family:" + SANS)
    + rule(".mono", "font-family:" + MONO)
    + "@media (prefers-reduced-motion:reduce){"
    + rule("*", "animation:none!important")
    + rule(".rm-hide", "display:none")
    + "}"
)


def text_width(s, size, bold=False, mono=False):
    """Rough advance width; deliberately generous so layouts never collide."""
    if mono:
        return len(s) * size * 0.6
    return len(s) * size * (0.57 if bold else 0.53)


def txt(x, y, s, size=16, fill="#FFFFFF", weight=None, anchor=None, cls=None,
        opacity=None, spacing=None, extra=""):
    attrs = [f'x="{x}"', f'y="{y}"', f'font-size="{size}"', f'fill="{fill}"']
    if weight:
        attrs.append(f'font-weight="{weight}"')
    if anchor:
        attrs.append(f'text-anchor="{anchor}"')
    if cls:
        attrs.append(f'class="{cls}"')
    if opacity is not None:
        attrs.append(f'fill-opacity="{opacity}"')
    if spacing is not None:
        attrs.append(f'letter-spacing="{spacing}"')
    if extra:
        attrs.append(extra)
    return f"<text {' '.join(attrs)}>{esc(s)}</text>"


def grad(gid, colors, x1=0, y1=0, x2=1, y2=1, radial=False):
    """Gradient from plain colours or (offset, colour, opacity) tuples."""
    stops = []
    for i, c in enumerate(colors):
        if isinstance(c, tuple):
            offset, color, alpha = c[0], c[1], (c[2] if len(c) > 2 else 1)
        else:
            offset, color, alpha = (i / (len(colors) - 1) if len(colors) > 1 else 0), c, 1
        stops.append(f'<stop offset="{offset:.3f}" stop-color="{color}" stop-opacity="{alpha}"/>')
    joined = "".join(stops)
    if radial:
        return f'<radialGradient id="{gid}">{joined}</radialGradient>'
    return f'<linearGradient id="{gid}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{joined}</linearGradient>'


def svg_doc(w, h, title, defs, body, css=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'fill="none" role="img" aria-label="{esc(title)}">\n'
        f"<title>{esc(title)}</title>\n"
        f"<style>{BASE_CSS}{css}</style>\n"
        f"<defs>{''.join(defs)}</defs>\n"
        + "\n".join(body)
        + "\n</svg>\n"
    )


def write(rel, content):
    path = ASSETS / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)
    print(f"  assets/{rel:<30} {len(content.encode('utf-8')) / 1024:6.1f} KB")


# Mockup loops start this many seconds into their 10s timeline, so the first frame
# (and any renderer that freezes animations) shows the finished UI instead of a blank one.
LOOP_START = 8.5


def seq(cls, start, end, total, dy=8, fade=0.45):
    """CSS that shows `.cls` between `start` and `end` seconds of a looping timeline."""
    def pct(sec):
        return f"{max(0.0, min(100.0, sec / total * 100)):.2f}%"

    return rule(f".{cls}", f"animation:k{cls} {total}s ease-out -{LOOP_START}s infinite") + keyframes(f"k{cls}", [
        (f"0%,{pct(start)}", f"opacity:0;transform:translateY({dy}px)"),
        (f"{pct(start + fade)},{pct(end)}", "opacity:1;transform:translateY(0)"),
        (f"{pct(min(end + fade, total))},100%", "opacity:0;transform:translateY(0)"),
    ])


def pill(x, y, label, size, text_fill, fill, fill_op, stroke, stroke_op, h=28, weight=600, pad=13):
    w = text_width(label, size, bold=True) + pad * 2
    markup = (
        f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="{h / 2}" fill="{fill}" '
        f'fill-opacity="{fill_op}" stroke="{stroke}" stroke-opacity="{stroke_op}"/>'
        + txt(f"{x + w / 2:.1f}", f"{y + h / 2 + size * 0.36:.1f}", label, size, text_fill, weight, "middle")
    )
    return markup, w


def chrome(wid, bg, bar, border, tab, tab_fill):
    """Browser-window frame for the project mockups (520x360, local coordinates)."""
    defs = [f'<clipPath id="{wid}"><rect width="520" height="360" rx="14"/></clipPath>']
    head = (
        f'<g clip-path="url(#{wid})"><rect width="520" height="360" fill="{bg}"/>'
        f'<rect width="520" height="34" fill="{bar}"/>'
        '<circle cx="20" cy="17" r="5.5" fill="#FF5F57"/><circle cx="38" cy="17" r="5.5" fill="#FEBC2E"/>'
        '<circle cx="56" cy="17" r="5.5" fill="#28C840"/>'
        + txt(80, 21.5, tab, 11.5, tab_fill, 500)
        + f'<line x1="0" y1="34" x2="520" y2="34" stroke="{border}"/>'
    )
    tail = f'</g><rect x=".5" y=".5" width="519" height="359" rx="13.5" stroke="{border}"/>'
    return defs, head, tail


# ── icons ────────────────────────────────────────────────────────────────────

_cache = {}


def fetch(url):
    if url not in _cache:
        req = urllib.request.Request(url, headers={"User-Agent": "profile-readme-builder"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            _cache[url] = resp.read().decode("utf-8")
    return _cache[url]


def prefix_ids(markup, prefix):
    """Namespace ids so several inlined icons can live in one document."""
    for old in sorted(set(re.findall(r'\bid="([^"]+)"', markup)), key=len, reverse=True):
        new = prefix + old
        markup = (markup.replace(f'id="{old}"', f'id="{new}"')
                  .replace(f"url(#{old})", f"url(#{new})")
                  .replace(f'href="#{old}"', f'href="#{new}"'))
    return markup


def simple_path(slug):
    return re.search(r'<path d="([^"]+)"', fetch(SIMPLE_ICONS.format(slug))).group(1)


TILE = '<rect width="256" height="256" rx="60" fill="#242938"/>'


def tile(icon, uid):
    """Markup for a 256x256 icon tile in the skillicons.dev style."""
    kind = icon["kind"]
    if kind == "skill":
        raw = fetch(SKILL_ICONS.format(icon["id"]))
        inner = raw[raw.index(">", raw.index("<svg")) + 1:raw.rindex("</svg>")]
        return prefix_ids(inner, uid)
    if kind == "simple":
        scale = icon.get("scale", 5.6667)
        offset = 128 - 12 * scale
        return TILE + (f'<path transform="translate({offset:.2f} {offset:.2f}) scale({scale})" '
                       f'd="{simple_path(icon["slug"])}" fill="{icon["color"]}"/>')
    if kind == "text":
        gid = uid + "g"
        return (TILE + "<defs>" + grad(gid, icon["colors"]) + "</defs>"
                + txt(128, round(128 + icon["size"] * 0.34), icon["text"], icon["size"],
                      f"url(#{gid})", 800, "middle", "mono"))
    if kind == "db":
        return TILE + (
            '<path d="M70 84V170c0 13 26 24 58 24s58-11 58-24V84z" fill="#4285F4"/>'
            '<path d="M70 113c0 13 26 24 58 24s58-11 58-24M70 142c0 13 26 24 58 24s58-11 58-24" '
            'stroke="#AECBFA" stroke-width="8"/>'
            '<ellipse cx="128" cy="84" rx="58" ry="22" fill="#8AB4F8"/>'
        )
    raise ValueError(kind)


def sk(icon_id, label):
    return {"kind": "skill", "id": icon_id, "label": label}


def si(slug, color, label):
    return {"kind": "simple", "slug": slug, "color": color, "label": label}


# ── I. banner ────────────────────────────────────────────────────────────────

def build_banner():
    W, H = 1000, 330
    phrases = [
        "building full-stack platforms",
        "shipping AI tools & model routers",
        "automating operations with data",
        "architecting software that scales",
    ]
    size, y_type, x0 = 17, 238, 78
    cw = size * 0.6

    # Typewriter timeline, played back with discrete SMIL steps.
    t, tracks, cursor = 0.3, [], []
    for p in phrases:
        n, ev = len(p), [(0.0, 0)]
        ev += [(t + k * 0.065, k) for k in range(1, n + 1)]
        t += n * 0.065 + 1.9
        ev += [(t + (n - k) * 0.03, k) for k in range(n - 1, -1, -1)]
        t += n * 0.03 + 0.45
        tracks.append(ev)
        cursor += ev[1:]
    total = round(t, 2)
    cursor = [(0.0, 0)] + sorted(cursor)

    def smil(attr, events, to_value):
        times = ";".join(f"{e[0] / total:.4f}" for e in events)
        values = ";".join(f"{to_value(e[1]):.1f}" for e in events)
        # Start 3s in, while the first phrase is fully typed, so a still frame (or the PDF) shows the tagline.
        return (f'<animate attributeName="{attr}" dur="{total}s" begin="-3s" repeatCount="indefinite" '
                f'calcMode="discrete" keyTimes="{times}" values="{values}"/>')

    defs = [
        '<clipPath id="card"><rect width="1000" height="330" rx="24"/></clipPath>',
        grad("bg", ["#0B0A1F", "#1A1446", "#0B2A4A"]),
        grad("name", ["#FFFFFF", "#C7D2FE"], 0, 0, 1, 0),
        grad("role", [SKY, VIOLET, PINK], 0, 0, 1, 0),
        grad("edge", [VIOLET, SKY, TEAL, PINK]),
        grad("ai", [VIOLET, TEAL]),
        '<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="60"/></filter>',
        '<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">'
        '<path d="M40 0H0V40" stroke="#FFFFFF" stroke-opacity=".06"/></pattern>',
        grad("fade", [(0, "#FFFFFF", 0.9), (1, "#FFFFFF", 0)], radial=True),
        '<mask id="gridMask"><rect width="1000" height="330" fill="url(#fade)"/></mask>',
    ]
    for i, p in enumerate(phrases):
        width_anim = smil("width", tracks[i], lambda k: k * cw + (0.5 if k else 0))
        defs.append(f'<clipPath id="type{i}"><rect x="{x0}" y="{y_type - 18}" height="26" width="0">'
                    f"{width_anim}</rect></clipPath>")

    css = (
        "".join(rule(f".o{i}", f"animation:o{i} {d}s ease-in-out infinite alternate")
                + keyframes(f"o{i}", [("to", f"transform:translate({dx}px,{dy}px)")])
                for i, (d, dx, dy) in enumerate([(16, 140, 50), (19, -160, -40), (14, -120, 70), (21, 150, -60)]))
        + rule(".tw", "animation:tw 3s ease-in-out infinite")
        + keyframes("tw", [("0%,100%", "opacity:.15"), ("50%", "opacity:.9")])
        + rule(".blink", "animation:blink 1s steps(1) infinite")
        + keyframes("blink", [("50%", "opacity:0")])
        + rule(".edge", "stroke-dasharray:4 7;animation:dash 1.4s linear infinite")
        + keyframes("dash", [("to", "stroke-dashoffset:-22")])
        + rule(".pulse", "animation:pulse 2.4s ease-out infinite;transform-box:fill-box;transform-origin:center")
        + keyframes("pulse", [("0%", "opacity:.7;transform:scale(1)"), ("100%", "opacity:0;transform:scale(1.25)")])
    )

    body = ['<g clip-path="url(#card)">', '<rect width="1000" height="330" fill="url(#bg)"/>',
            '<g filter="url(#blur)">',
            f'<circle class="o0" cx="120" cy="60" r="150" fill="{VIOLET}" fill-opacity=".55"/>',
            f'<circle class="o1" cx="880" cy="300" r="170" fill="{SKY}" fill-opacity=".4"/>',
            f'<circle class="o2" cx="560" cy="-30" r="130" fill="{PINK}" fill-opacity=".35"/>',
            f'<circle class="o3" cx="360" cy="370" r="140" fill="{TEAL}" fill-opacity=".3"/>',
            "</g>",
            '<rect width="1000" height="330" fill="url(#grid)" mask="url(#gridMask)"/>']

    seed = 7
    for i in range(22):
        seed = (seed * 9301 + 49297) % 233280
        x = 20 + seed % 960
        seed = (seed * 9301 + 49297) % 233280
        y = 14 + seed % 300
        r = 0.8 + (i % 3) * 0.5
        body.append(f'<circle class="tw" cx="{x}" cy="{y}" r="{r}" fill="#FFFFFF" '
                    f'style="animation-delay:-{i * 0.37:.2f}s"/>')

    body += [
        txt(56, 84, "HI THERE, I'M", 14, "#A5B4FC", 700, spacing=4),
        txt(54, 146, "Brendan Stewart", 60, "url(#name)", 800),
        txt(56, 190, "Software Engineer & Architect", 26, "url(#role)", 700),
        txt(56, y_type, ">", size, TEAL, 700, cls="mono"),
    ]
    for i, p in enumerate(phrases):
        body.append(txt(x0, y_type, p, size, "#E6EDF3", cls="mono",
                        extra=f'textLength="{len(p) * cw:.1f}" lengthAdjust="spacing" clip-path="url(#type{i})"'))
    body.append(f'<rect class="blink" x="{x0 + 2}" y="{y_type - 14}" width="9" height="18" rx="1.5" fill="{TEAL}">'
                + smil("x", cursor, lambda k: x0 + 2 + k * cw) + "</rect>")

    x = 56
    for label, color in [("Studio City, CA", PINK), ("Logitech · UE Pro & IT", SKY), ("ASU · 4.0 GPA", AMBER)]:
        w = text_width(label, 13, bold=True) + 40
        body += [f'<rect x="{x:.1f}" y="266" width="{w:.1f}" height="30" rx="15" fill="#FFFFFF" fill-opacity=".08" '
                 'stroke="#FFFFFF" stroke-opacity=".18"/>',
                 f'<circle cx="{x + 16:.1f}" cy="281" r="4" fill="{color}"/>',
                 txt(f"{x + 28:.1f}", 285.5, label, 13, "#E6EDF3", 600)]
        x += w + 10

    # "Systems I architect" node graph.
    NW, NH = 150, 48
    nodes = [
        ("ui", 610, 52, "Web UI", "React · Vue", SKY),
        ("api", 820, 52, "Node API", "REST · Express", TEAL),
        ("ai", 715, 142, "AI Router", "LLMs · RAG · CLI", VIOLET),
        ("cv", 610, 232, "Vision QA", "mm-level defects", PINK),
        ("data", 820, 232, "Data Pipelines", "BigQuery → BI", AMBER),
    ]
    center = {n[0]: (n[1] + NW // 2, n[2] + NH // 2) for n in nodes}
    body.append(txt(610, 36, "// systems I architect", 12, "#8B93C9", cls="mono"))
    for a, b in [("ui", "api"), ("ui", "ai"), ("api", "ai"), ("ai", "cv"), ("ai", "data"), ("cv", "data")]:
        (ax, ay), (bx, by) = center[a], center[b]
        body.append(f'<line class="edge" x1="{ax}" y1="{ay}" x2="{bx}" y2="{by}" stroke="#8B93FF" '
                    'stroke-opacity=".55" stroke-width="1.5"/>')
    packets = [("ui", "api", TEAL, 2.2, 0), ("api", "ai", SKY, 2.0, -0.7), ("ai", "data", AMBER, 2.4, -1.1),
               ("ai", "cv", PINK, 2.6, -0.4), ("cv", "data", "#FFFFFF", 2.8, -1.6)]
    for a, b, color, dur, begin in packets:
        (ax, ay), (bx, by) = center[a], center[b]
        body.append(f'<circle r="3.5" fill="{color}"><animateMotion dur="{dur}s" begin="{begin}s" '
                    f'repeatCount="indefinite" path="M{ax} {ay}L{bx} {by}"/></circle>')
    for key, nx, ny, title, sub, color in nodes:
        if key == "ai":
            body.append(f'<rect class="pulse" x="{nx}" y="{ny}" width="{NW}" height="{NH}" rx="12" '
                        'stroke="url(#ai)" stroke-width="2"/>')
        stroke = 'stroke="url(#ai)" stroke-width="2"' if key == "ai" else 'stroke="#FFFFFF" stroke-opacity=".18"'
        body += [f'<rect x="{nx}" y="{ny}" width="{NW}" height="{NH}" rx="12" fill="#120F2E" fill-opacity=".94" {stroke}/>',
                 f'<circle cx="{nx + 16}" cy="{ny + 17}" r="4" fill="{color}"/>',
                 txt(nx + 27, ny + 21.5, title, 13.5, "#FFFFFF", 700),
                 txt(nx + 16, ny + 38, sub, 11, "#A5ADCB")]

    body += ["</g>", '<rect x=".75" y=".75" width="998.5" height="328.5" rx="23.25" stroke="url(#edge)" '
             'stroke-opacity=".6" stroke-width="1.5"/>']
    write("banner.svg", svg_doc(W, H, "Brendan Stewart — Software Engineer & Architect", defs, body, css))


# ── section headers ──────────────────────────────────────────────────────────

HEADER_ICONS = {
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.4 3.6-8 8-8s8 3.6 8 8"/>',
    "code": '<path d="M8 6l-6 6 6 6M16 6l6 6-6 6M14 4l-4 16"/>',
    "rocket": ('<path d="M12 2c3.5 2.5 5.5 6.5 5 11l-2.5 3h-5L7 13c-.5-4.5 1.5-8.5 5-11z"/><circle cx="12" cy="9" r="2"/>'
               '<path d="M7 13l-3 3.5 3.5.5M17 13l3 3.5-3.5.5M10.5 19.5L12 22l1.5-2.5"/>'),
    "briefcase": '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M9 7V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2M3 13h18"/>',
    "send": '<path d="M22 2L11 13M22 2l-7 20-4-9-9-4z"/>',
}


def build_header(slug, num, title, subtitle, c1, c2, icon):
    defs = [
        '<clipPath id="clip"><rect width="1000" height="96" rx="18"/></clipPath>',
        grad("bg", [c1, c2], 0, 0, 1, 0),
        grad("sheen", [(0, "#FFFFFF", 0), (0.5, "#FFFFFF", 0.35), (1, "#FFFFFF", 0)], 0, 0, 1, 0),
        '<pattern id="dots" width="16" height="16" patternUnits="userSpaceOnUse">'
        '<circle cx="2" cy="2" r="1.3" fill="#FFFFFF" fill-opacity=".22"/></pattern>',
        grad("fade", [(0, "#FFFFFF", 0), (1, "#FFFFFF", 1)], 0, 0, 1, 0),
        '<mask id="m"><rect x="560" width="440" height="96" fill="url(#fade)"/></mask>',
    ]
    css = (
        rule(".sheen", "animation:sweep 7s ease-in-out infinite")
        + keyframes("sweep", [("0%", "transform:translateX(-260px) skewX(-20deg)"),
                              ("55%,100%", "transform:translateX(1260px) skewX(-20deg)")])
        + rule(".float", "animation:float 4s ease-in-out infinite")
        + keyframes("float", [("0%,100%", "transform:translateY(0)"), ("50%", "transform:translateY(-5px)")])
        + rule(".ring", "animation:ring 3s ease-out infinite;transform-box:fill-box;transform-origin:center")
        + keyframes("ring", [("0%", "transform:scale(1);opacity:.55"), ("100%", "transform:scale(1.7);opacity:0")])
    )
    body = [
        '<g clip-path="url(#clip)">',
        '<rect width="1000" height="96" fill="url(#bg)"/>',
        '<rect x="560" width="440" height="96" fill="url(#dots)" mask="url(#m)"/>',
        '<circle cx="928" cy="48" r="70" stroke="#FFFFFF" stroke-opacity=".14" stroke-width="1.5"/>',
        '<circle cx="928" cy="48" r="104" stroke="#FFFFFF" stroke-opacity=".08" stroke-width="1.5"/>',
        '<rect class="sheen" x="0" y="-30" width="140" height="160" fill="url(#sheen)"/>',
        '<circle class="ring" cx="928" cy="48" r="28" stroke="#FFFFFF" stroke-width="1.5"/>',
        "</g>",
        txt(30, 63, num, 46, "#FFFFFF", 800, opacity=0.32),
        txt(104, 49, title, 30, "#FFFFFF", 700),
        txt(105, 74, subtitle, 15, "#FFFFFF", 500, opacity=0.9),
        '<g class="float">',
        '<circle cx="928" cy="48" r="28" fill="#FFFFFF" fill-opacity=".18" stroke="#FFFFFF" stroke-opacity=".45"/>',
        '<g transform="translate(911.2 31.2) scale(1.4)" stroke="#FFFFFF" stroke-width="1.7" '
        f'stroke-linecap="round" stroke-linejoin="round">{HEADER_ICONS[icon]}</g>',
        "</g>",
    ]
    write(f"headers/{slug}.svg", svg_doc(1000, 96, f"{num} · {title}", defs, body, css))


# ── II. about ────────────────────────────────────────────────────────────────

def build_about_code():
    W, H = 460, 380
    P, KEY, STR, KW, VAR, CMT = "#C9D1D9", "#79C0FF", "#A5D6FF", "#FF7B72", "#D2A8FF", "#8B949E"

    def kv(key, value):
        return [(2, [(key, KEY), (": ", P), (f'"{value}"', STR), (",", P)])]

    def arr(key, items):
        parts = [(key, KEY), (": [", P)]
        for i, item in enumerate(items):
            parts.append((f'"{item}"', STR))
            if i < len(items) - 1:
                parts.append((", ", P))
        return [(2, parts + [("],", P)])]

    lines = (
        [(0, [("// hello, world", CMT)]), (0, [("const ", KW), ("brendan", VAR), (" = {", P)])]
        + [(2, [("teams", KEY), (": [", P)]),
           (4, [('"Ultimate Ears Pro"', STR), (",", P)]),
           (4, [('"IT Software Development"', STR), (",", P)]),
           (2, [("],", P)])]
        + arr("specialty", ["full stack software"])
        + arr("builds", ["automation", "data access"])
        + arr("stack", ["React", "Vue", "Node", "Go"])
        + kv("status", "building something new")
        + [(0, [("};", P)]), (0, [("export default ", KW), ("brendan", VAR), (";", P)])]
    )
    size, cw, x_code, y0, lh = 13.5, 13.5 * 0.6, 52, 78, 23

    defs = [
        '<clipPath id="win"><rect width="460" height="380" rx="16"/></clipPath>',
        grad("top", [VIOLET, SKY, TEAL], 0, 0, 1, 0),
        grad("glow", [(0, VIOLET, 0.35), (1, VIOLET, 0)], radial=True),
    ]
    n = len(lines)
    # The code is always visible; only an "active line" highlight steps down through it.
    css = (
        rule(".hl", f"animation:hl {n * 0.9:.1f}s steps({n}) infinite")
        + keyframes("hl", [("from", "transform:translateY(0)"), ("to", f"transform:translateY({n * lh}px)")])
        + rule(".blink", "animation:blink 1s steps(1) infinite")
        + keyframes("blink", [("50%", "opacity:0")])
    )
    body = [
        '<g clip-path="url(#win)">',
        '<rect width="460" height="380" fill="#0D1117"/>',
        '<circle cx="420" cy="20" r="220" fill="url(#glow)"/>',
        '<rect width="460" height="40" fill="#161B22"/>',
        '<rect width="460" height="2.5" fill="url(#top)"/>',
        '<circle cx="20" cy="21" r="5.5" fill="#FF5F57"/><circle cx="38" cy="21" r="5.5" fill="#FEBC2E"/>',
        '<circle cx="56" cy="21" r="5.5" fill="#28C840"/>',
        '<rect x="78" y="8" width="112" height="32" rx="8" fill="#0D1117"/>',
        '<circle cx="94" cy="24" r="4" fill="#F0DB4F"/>',
        txt(104, 28.5, "brendan.js", 12, "#E6EDF3", 500),
        f'<g class="hl"><rect x="0" y="{y0 - 16}" width="460" height="{lh}" fill="#FFFFFF" fill-opacity=".05"/>'
        f'<rect x="0" y="{y0 - 16}" width="3" height="{lh}" fill="{TEAL}"/></g>',
    ]
    for i, (indent, parts) in enumerate(lines):
        y = y0 + i * lh
        spans = "".join(f'<tspan fill="{c}">{esc(s)}</tspan>' for s, c in parts)
        body.append('<g>'
                    + txt(36, y, str(i + 1), 12, "#6E7681", anchor="end", cls="mono")
                    + f'<text x="{x_code + indent * cw:.1f}" y="{y}" font-size="{size}" class="mono" '
                      f'xml:space="preserve">{spans}</text></g>')
    cursor_y = y0 + len(lines) * lh
    body += [
        txt(36, cursor_y, str(len(lines) + 1), 12, "#6E7681", anchor="end", cls="mono"),
        f'<rect class="blink" x="{x_code}" y="{cursor_y - 13}" width="8" height="17" rx="1" fill="{TEAL}"/>',
        '<rect y="354" width="460" height="26" fill="#161B22"/>',
        f'<circle cx="18" cy="367" r="3.5" fill="{TEAL}"/>',
        txt(28, 371, "main", 11, "#8B949E", cls="mono"),
        txt(442, 371, "JavaScript · UTF-8", 11, "#8B949E", anchor="end", cls="mono"),
        "</g>",
        '<rect x=".75" y=".75" width="458.5" height="378.5" rx="15.25" stroke="#30363D" stroke-width="1.5"/>',
    ]
    write("about-code.svg", svg_doc(W, H, "brendan.js — a quick profile of Brendan in code", defs, body, css))


def build_education():
    gold = "#FFC627"
    defs = [
        '<clipPath id="clip"><rect width="1000" height="150" rx="20"/></clipPath>',
        grad("bg", ["#8C1D40", "#6B1631", "#3E0C1E"], 0, 0, 1, 1),
        grad("sheen", [(0, "#FFFFFF", 0), (0.5, "#FFFFFF", 0.22), (1, "#FFFFFF", 0)], 0, 0, 1, 0),
        '<pattern id="dots" width="18" height="18" patternUnits="userSpaceOnUse">'
        f'<circle cx="2" cy="2" r="1.3" fill="{gold}" fill-opacity=".22"/></pattern>',
        grad("fade", [(0, "#FFFFFF", 0), (1, "#FFFFFF", 1)], 0, 0, 1, 0),
        '<mask id="m"><rect x="600" width="400" height="150" fill="url(#fade)"/></mask>',
    ]
    css = (
        rule(".sheen", "animation:sweep 8s ease-in-out infinite")
        + keyframes("sweep", [("0%", "transform:translateX(-300px) skewX(-20deg)"),
                              ("50%,100%", "transform:translateX(1300px) skewX(-20deg)")])
        + rule(".tassel", "animation:swing 2.8s ease-in-out infinite;transform-origin:106px 66px")
        + keyframes("swing", [("0%,100%", "transform:rotate(10deg)"), ("50%", "transform:rotate(-12deg)")])
    )
    body = [
        '<g clip-path="url(#clip)">',
        '<rect width="1000" height="150" fill="url(#bg)"/>',
        '<rect x="600" width="400" height="150" fill="url(#dots)" mask="url(#m)"/>',
        '<rect class="sheen" y="-20" width="160" height="190" fill="url(#sheen)"/>',
        "</g>",
        f'<circle cx="78" cy="75" r="46" fill="{gold}" fill-opacity=".14" stroke="{gold}" stroke-opacity=".6" stroke-width="1.5"/>',
        f'<path d="M60 72v14c0 6 8 11 18 11s18-5 18-11V72" fill="{gold}" fill-opacity=".85"/>',
        f'<path d="M48 66l30-13 30 13-30 13z" fill="{gold}"/>',
        f'<g class="tassel"><path d="M106 66v18" stroke="{gold}" stroke-width="2.5" stroke-linecap="round"/>'
        f'<circle cx="106" cy="88" r="4" fill="{gold}"/></g>',
        txt(150, 46, "EDUCATION", 12, gold, 700, spacing=3),
        txt(150, 80, "Arizona State University", 28, "#FFFFFF", 700),
        txt(150, 108, "B.S. Graphical Information Technology · Full Stack Web Development", 15.5, "#F9D7E2", 500),
        f'<rect x="770" y="33" width="192" height="84" rx="16" fill="{gold}" fill-opacity=".12" '
        f'stroke="{gold}" stroke-opacity=".6"/>',
        txt(866, 79, "4.0 GPA", 34, gold, 800, "middle"),
        txt(866, 102, "Graduating Fall 2026", 13, "#FDE7EF", 500, "middle"),
        f'<rect x=".75" y=".75" width="998.5" height="148.5" rx="19.25" stroke="{gold}" stroke-opacity=".35" stroke-width="1.5"/>',
    ]
    write("education.svg", svg_doc(1000, 150, "Arizona State University — B.S. Graphical Information Technology, "
                                   "Full Stack Web Development — 4.0 GPA", defs, body, css))


# ── III. skills ──────────────────────────────────────────────────────────────

LANGUAGE_ROWS = [
    ("Languages", [VIOLET, SKY], [
        sk("js", "JavaScript"), sk("go", "Go"), sk("java", "Java"), sk("cpp", "C++"), sk("py", "Python"),
        {"kind": "text", "text": "SQL", "size": 80, "colors": ["#4FC3F7", VIOLET], "label": "SQL"},
        sk("html", "HTML5"), sk("css", "CSS3")]),
    ("Frontend", [SKY, TEAL], [
        sk("react", "React"), sk("vue", "Vue"), sk("threejs", "Three.js"), sk("tailwind", "Tailwind"),
        sk("vite", "Vite")]),
    ("Backend & APIs", [TEAL, VIOLET], [
        sk("nodejs", "Node.js"), sk("express", "Express"), sk("flask", "Flask"),
        {"kind": "text", "text": "{ }", "size": 92, "colors": [PINK, VIOLET], "label": "REST APIs"},
        si("googleappsscript", "#4285F4", "Apps Script")]),
]

PLATFORM_ROWS = [
    ("Data & BI", [PINK, VIOLET], [
        sk("mongodb", "MongoDB"), sk("postgres", "PostgreSQL"), sk("mysql", "MySQL"),
        si("microsoftsqlserver", "#CC2927", "SQL Server"), {"kind": "db", "label": "Cloud SQL"},
        si("googlebigquery", "#669DF6", "BigQuery"), si("googledatastudio", "#4285F4", "Data Studio"),
        si("tableau", "#E97627", "Tableau")]),
    ("Cloud & Platforms", [AMBER, PINK], [
        sk("gcp", "Cloud Run"), sk("vercel", "Vercel"), si("shopify", "#7AB55C", "Shopify"),
        sk("arduino", "Arduino"), sk("git", "Git"), sk("github", "GitHub")]),
    ("Design", [VIOLET, PINK], [
        sk("ps", "Photoshop"), sk("ai", "Illustrator"), si("adobeindesign", "#FF3366", "InDesign"),
        si("canva", "#00C4CC", "Canva")]),
]


def build_stack(filename, title, rows):
    W, pad, row_h = 1000, 22, 104
    H = pad * 2 + row_h * len(rows)
    defs = [grad("border", [VIOLET, SKY, TEAL])]
    css = (rule(".fl", "animation:fl 3.6s ease-in-out infinite")
           + keyframes("fl", [("0%,100%", "transform:translateY(0)"), ("50%", "transform:translateY(-7px)")]))
    body = [f'<rect x="1" y="1" width="998" height="{H - 2}" rx="20" fill="#0D1117"/>',
            f'<rect x="1" y="1" width="998" height="{H - 2}" rx="20" stroke="url(#border)" '
            'stroke-opacity=".55" stroke-width="1.5"/>']
    uid = 0
    for r, (label, colors, icons) in enumerate(rows):
        y0 = pad + r * row_h
        defs.append(grad(f"lg{r}", colors, 0, 0, 1, 0))
        body += [f'<rect x="{pad + 6}" y="{y0 + 22}" width="176" height="38" rx="19" fill="url(#lg{r})"/>',
                 txt(pad + 94, y0 + 46, label, 15, "#FFFFFF", 700, "middle"),
                 txt(pad + 94, y0 + 82, f"{len(icons)} tools", 12, "#8B949E", anchor="middle", cls="mono")]
        for i, icon in enumerate(icons):
            uid += 1
            x = 236 + i * 90
            delay = (i * 0.35 + r * 0.6) % 3.6
            body += [f'<g class="fl" style="animation-delay:-{delay:.2f}s">'
                     f'<svg x="{x}" y="{y0 + 12}" width="56" height="56" viewBox="0 0 256 256">'
                     f"{tile(icon, f'i{uid}_')}</svg></g>",
                     txt(x + 28, y0 + 90, icon["label"], 12.5, "#C9D1D9", 500, "middle")]
        if r < len(rows) - 1:
            body.append(f'<line x1="{pad}" y1="{y0 + row_h}" x2="{W - pad}" y2="{y0 + row_h}" '
                        'stroke="#30363D" stroke-dasharray="3 6"/>')
    alt = "; ".join(f"{label}: " + ", ".join(i["label"] for i in icons) for label, _, icons in rows)
    write(filename, svg_doc(W, H, f"{title} — {alt}", defs, body, css))


# ── IV. projects ─────────────────────────────────────────────────────────────

THEMES = {
    "web-auditor": dict(bg=["#FFFFFF", "#F1F4F8", "#DCE3EB"], glow1="#94A3B8", glow1_op=0.35,
                        glow2="#E2E8F0", glow2_op=0.7, edge=["#CBD5E1", "#94A3B8", "#CBD5E1"], edge_op=1,
                        shadow=0.35, dot="#0F172A", accent="#64748B", title="#0B0D10", tagline="#334155",
                        muted="#475569", chip=("#1E293B", "#FFFFFF", 1, "#94A3B8", 0.7), status="#22C55E"),
    "traveler": dict(bg=["#120A24", "#2A1245", "#4A1D3F"], glow1="#FF7A59", glow1_op=0.38,
                      glow2="#FFC15E", glow2_op=0.2, edge=["#FF7A59", "#B15CFF", "#FFC15E"], edge_op=0.6,
                      shadow=0.5, dot="#FFFFFF", accent="#FFB088", title="#FFFFFF", tagline="#FFD7B5",
                      muted="#D4C4E4", chip=("#FFE1D1", "#FF7A59", 0.12, "#FF9F7A", 0.5), status="#F59E0B"),
}


def build_card(slug, n, title, tagline, desc, chips, status, mock):
    th = THEMES[slug]
    mock_defs, mock_body, mock_css = mock
    defs = [
        '<clipPath id="card"><rect width="1000" height="380" rx="24"/></clipPath>',
        grad("bg", th["bg"]),
        grad("glow1", [(0, th["glow1"], th["glow1_op"]), (1, th["glow1"], 0)], radial=True),
        grad("glow2", [(0, th["glow2"], th["glow2_op"]), (1, th["glow2"], 0)], radial=True),
        grad("edge", th["edge"]),
        '<filter id="shadow" x="-20%" y="-20%" width="140%" height="160%">'
        f'<feDropShadow dx="0" dy="18" stdDeviation="18" flood-color="#000000" flood-opacity="{th["shadow"]}"/></filter>',
        '<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">'
        f'<circle cx="2" cy="2" r="1.3" fill="{th["dot"]}" fill-opacity=".07"/></pattern>',
    ] + mock_defs
    css = (mock_css
           + rule(".ping", "animation:ping 2s ease-out infinite;transform-box:fill-box;transform-origin:center")
           + keyframes("ping", [("0%", "transform:scale(1);opacity:.7"), ("100%", "transform:scale(3);opacity:0")]))
    body = ['<g clip-path="url(#card)">',
            '<rect width="1000" height="380" fill="url(#bg)"/>',
            '<rect width="1000" height="380" fill="url(#dots)"/>',
            '<circle cx="900" cy="40" r="320" fill="url(#glow1)"/>',
            '<circle cx="420" cy="430" r="300" fill="url(#glow2)"/>',
            txt(50, 74, f"FEATURED PROJECT · 0{n}", 12.5, th["accent"], 700, spacing=3),
            txt(48, 128, title, 48, th["title"], 800),
            txt(50, 162, tagline, 17, th["tagline"], 600)]
    for i, line in enumerate(desc):
        body.append(txt(50, 200 + i * 25, line, 15.5, th["muted"]))
    x = 50.0
    chip_text, chip_fill, chip_fill_op, chip_stroke, chip_stroke_op = th["chip"]
    for label in chips:
        markup, w = pill(x, 296, label, 12.5, chip_text, chip_fill, chip_fill_op, chip_stroke, chip_stroke_op, pad=12)
        body.append(markup)
        x += w + 8
    if x - 8 > 480:
        raise ValueError(f"chips overflow on {slug}: ends at {x - 8:.0f}px")
    body += [f'<circle class="ping" cx="56" cy="350" r="4.5" fill="{th["status"]}"/>',
             f'<circle cx="56" cy="350" r="4.5" fill="{th["status"]}"/>',
             txt(70, 354.5, status, 13, th["muted"], 600),
             f'<g transform="translate(495 50)" filter="url(#shadow)">{mock_body}</g>',
             "</g>",
             f'<rect x=".75" y=".75" width="998.5" height="378.5" rx="23.25" stroke="url(#edge)" '
             f'stroke-opacity="{th["edge_op"]}" stroke-width="1.5"/>']
    alt = f"{title} — {tagline}. " + " ".join(desc)
    write(f"projects/{slug}.svg", svg_doc(1000, 380, alt, defs, body, css))


def mock_web_auditor():
    defs, head, tail = chrome("win", "#000000", "#0B0D10", "#2C323A", "Auditor — Live site audit", "#8A948E")
    defs.append(grad("silver", ["#8E99A6", "#C3C9D1", "#EEF2F7"]))
    T = 10
    css = (seq("r1", 3.4, 9.3, T, dy=10) + seq("r2", 4.2, 9.3, T, dy=10) + seq("r3", 5.0, 9.3, T, dy=10)
           + rule(".prog", f"transform-box:fill-box;transform-origin:left;animation:prog {T}s ease-in-out -{LOOP_START}s infinite")
           + keyframes("prog", [("0%", "transform:scaleX(0)"), ("55%,93%", "transform:scaleX(1);opacity:1"),
                                ("100%", "transform:scaleX(1);opacity:0")]))
    parts = [
        txt(18, 62, "Auditor", 17, "url(#silver)", 700),
        txt(372, 60, "Dashboard", 11, "#C3C9D1", 500),
        txt(440, 60, "Analytics", 11, "#8A948E", 500),
        '<rect x="18" y="76" width="330" height="28" rx="8" fill="#0B0D10" stroke="#2C323A"/>',
        txt(30, 94.5, "https://your-site.com", 11, "#C3C9D1", cls="mono"),
        '<rect x="356" y="76" width="130" height="28" rx="14" fill="url(#silver)"/>',
        txt(421, 94.5, "Start Audit", 12, "#06080A", 700, "middle"),
        txt(18, 127, "Crawling pages · depth 3", 11, "#9AA3A0"),
        txt(486, 127, "120 pages", 10.5, "#C3C9D1", anchor="end", cls="mono"),
        '<rect x="18" y="134" width="468" height="6" rx="3" fill="#1B1F25"/>',
        '<rect class="prog" x="18" y="134" width="468" height="6" rx="3" fill="url(#silver)"/>',
    ]
    stats = [("Dead links", "12", "#F87171"), ("Security", "7", "#FB923C"),
             ("Accessibility", "23", "#FACC15"), ("JS bugs", "3", "#A78BFA")]
    for i, (label, num, color) in enumerate(stats):
        x = 18 + i * 119
        parts += [f'<rect x="{x}" y="152" width="111" height="46" rx="10" fill="#0B0D10" stroke="#2C323A"/>',
                  f'<circle cx="{x + 14}" cy="166" r="4" fill="{color}"/>',
                  txt(x + 24, 170, label, 10.5, "#9AA3A0"),
                  txt(x + 14, 190, num, 17, "#FFFFFF", 700)]
    parts += ['<rect x="18" y="208" width="40" height="20" rx="10" fill="url(#silver)"/>',
              txt(38, 222, "All", 10.5, "#06080A", 700, "middle")]
    x = 64
    for label in ["High", "Medium", "Low"]:
        w = len(label) * 6.5 + 20
        parts += [f'<rect x="{x}" y="208" width="{w}" height="20" rx="10" stroke="#2C323A"/>',
                  txt(x + w / 2, 222, label, 10.5, "#9AA3A0", 500, "middle")]
        x += w + 6
    parts.append(txt(486, 222, "Export JSON · PDF", 10.5, "#C3C9D1", 500, "end"))
    issues = [("#F87171", "LINK", "404 Not Found · /blog/2019/launch-party"),
              ("#FB923C", "SEC", "Missing Content-Security-Policy header"),
              ("#FACC15", "A11Y", "<img> missing alt text on /products")]
    for i, (color, tag, msg) in enumerate(issues):
        y = 238 + i * 30
        parts += [f'<g class="r{i + 1}"><rect x="18" y="{y}" width="468" height="26" rx="7" fill="#0B0D10" stroke="#1B1F25"/>',
                  f'<circle cx="32" cy="{y + 13}" r="3.5" fill="{color}"/>',
                  txt(44, y + 17, tag, 9.5, color, 700, cls="mono"),
                  txt(92, y + 17, msg, 11, "#C3C9D1"), "</g>"]
    return defs, head + "".join(parts) + tail, css


def mock_traveler():
    defs, head, tail = chrome("win", "#FFFFFF", "#F1F5F9", "#E2E8F0", "Traveler — AI trip planner", "#64748B")
    defs += [grad("sunset", ["#FF7A59", "#FFC15E"]), grad("sunsetH", ["#FF7A59", "#FFC15E"], 0, 0, 1, 0),
             '<clipPath id="map"><rect x="258" y="94" width="230" height="136" rx="12"/></clipPath>',
             '<clipPath id="typed"><rect x="46" y="52" height="24" width="270">'
             f'<animate attributeName="width" dur="10s" begin="-{LOOP_START}s" repeatCount="indefinite" '
             'keyTimes="0;0.03;0.19;0.97;1" values="0;0;270;270;0"/></rect></clipPath>']
    T = 10
    css = (seq("d1", 2.2, 9.3, T) + seq("d2", 2.7, 9.3, T) + seq("d3", 3.2, 9.3, T)
           + seq("p1", 3.6, 9.3, T, dy=-14) + seq("p2", 4.2, 9.3, T, dy=-14) + seq("p3", 4.8, 9.3, T, dy=-14)
           + seq("rc", 6.6, 9.3, T)
           + rule(".route", f"stroke-dasharray:100;animation:route {T}s ease-in-out -{LOOP_START}s infinite")
           + keyframes("route", [("0%,36%", "stroke-dashoffset:100"), ("50%,93%", "stroke-dashoffset:0;opacity:1"),
                                 ("100%", "stroke-dashoffset:0;opacity:0")])
           + rule(".bud", f"transform-box:fill-box;transform-origin:left;animation:bud {T}s ease-in-out -{LOOP_START}s infinite")
           + keyframes("bud", [("0%,52%", "transform:scaleX(0)"), ("64%,93%", "transform:scaleX(1);opacity:1"),
                               ("100%", "transform:scaleX(1);opacity:0")]))
    route = "M290 200C320 170 340 140 372 138S430 150 452 176"
    parts = [
        '<rect x="16" y="48" width="352" height="32" rx="16" fill="#FFFFFF" stroke="#E2E8F0"/>',
        '<path d="M32 56l2 6 6 2-6 2-2 6-2-6-6-2 6-2z" fill="url(#sunset)"/>',
        txt(48, 68.5, "5 days in Kyoto · $1,500 · food + hiking", 12, "#0F172A", extra='clip-path="url(#typed)"'),
        '<rect x="376" y="48" width="112" height="32" rx="16" fill="url(#sunset)"/>',
        txt(432, 68.5, "Plan my trip", 12, "#FFFFFF", 700, "middle"),
    ]
    days = [("Fushimi Inari hike", "Sunrise trail · Free"), ("Nishiki Market eats", "Food tour · $45"),
            ("Arashiyama bamboo", "Nature walk · $20")]
    for i, (title, meta) in enumerate(days):
        y = 94 + i * 58
        parts += [f'<g class="d{i + 1}"><rect x="16" y="{y}" width="230" height="50" rx="12" fill="#FFFFFF" stroke="#E2E8F0"/>',
                  f'<rect x="28" y="{y + 12}" width="46" height="26" rx="8" fill="#FFF1EB"/>',
                  txt(51, y + 29, f"DAY {i + 1}", 9.5, "#FF7A59", 800, "middle", spacing=0.5),
                  txt(86, y + 22, title, 12, "#0F172A", 700),
                  txt(86, y + 39, meta, 10.5, "#64748B"), "</g>"]
    parts += ['<g class="rc">', txt(16, 282, "Recommended for you", 10.5, "#64748B", 600),
              '<rect x="16" y="290" width="96" height="22" rx="11" fill="#F1F5F9"/>',
              txt(64, 305, "Tea ceremony", 10.5, "#334155", 500, "middle"),
              '<rect x="118" y="290" width="92" height="22" rx="11" fill="#F1F5F9"/>',
              txt(164, 305, "Gion at dusk", 10.5, "#334155", 500, "middle"), "</g>"]
    parts += ['<g clip-path="url(#map)"><rect x="258" y="94" width="230" height="136" fill="#E0F2FE"/>',
              '<path d="M258 160C300 130 340 190 390 150S470 120 488 140V230H258z" fill="#DCFCE7"/>',
              '<path d="M330 94C360 120 420 100 488 118V94z" fill="#BBF7D0" fill-opacity=".7"/>',
              '<path d="M258 120C300 140 330 110 370 125S450 170 488 160" stroke="#BAE6FD" stroke-width="7"/>',
              f'<path d="{route}" stroke="#FF7A59" stroke-opacity=".3" stroke-width="2.5" stroke-dasharray="4 5"/>',
              f'<path class="route" d="{route}" pathLength="100" stroke="#FF7A59" stroke-width="3" stroke-linecap="round"/>',
              txt(270, 112, "Kyoto", 11, "#0369A1", 700), "</g>",
              '<rect x="258" y="94" width="230" height="136" rx="12" stroke="#BAE6FD"/>']
    for i, (px, py) in enumerate([(290, 200), (372, 138), (452, 176)]):
        parts.append(f'<g class="p{i + 1}"><path d="M{px - 6} {py - 10}L{px} {py}L{px + 6} {py - 10}z" fill="#FF7A59"/>'
                     f'<circle cx="{px}" cy="{py - 14}" r="8" fill="#FF7A59"/>'
                     f'<circle cx="{px}" cy="{py - 14}" r="3" fill="#FFFFFF"/></g>')
    parts += ['<rect x="258" y="240" width="230" height="66" rx="12" fill="#FFF7ED" stroke="#FED7AA"/>',
              txt(272, 260, "Trip budget", 11, "#9A3412", 700),
              txt(474, 260, "$1,180 / $1,500", 11, "#0F172A", 700, "end"),
              '<rect x="272" y="270" width="202" height="8" rx="4" fill="#FFEDD5"/>',
              '<rect class="bud" x="272" y="270" width="160" height="8" rx="4" fill="url(#sunsetH)"/>',
              txt(272, 295, "Under budget by $320", 10.5, "#16A34A", 600)]
    return defs, head + "".join(parts) + tail, css


def build_projects():
    build_card("web-auditor", 1, "Web Auditor", "Full-stack website crawler & auditor",
               ["Crawls an entire website and audits every page",
                "for dead links, security gaps, accessibility,",
                "content quality and live JavaScript errors,",
                "with a real-time dashboard and PDF reports."],
               ["Python", "Flask", "Playwright", "asyncio", "Tailwind"], "Open source on GitHub", mock_web_auditor())
    build_card("traveler", 2, "Traveler", "Plan an entire trip from a single prompt",
               ["An all-in-one AI travel planning assistant",
                "that turns one prompt into day-by-day",
                "itineraries, budgets, and personalized",
                "recommendations, all in one place."],
               ["AI itineraries", "Budgets", "Recommendations"], "In active development", mock_traveler())


# ── V. experience, interests & goals ─────────────────────────────────────────

def build_career():
    W, H = 460, 400
    steps = [(["Manufacturing"], "Factory floor"), (["Analyst"], "Data & automation"),
             (["Full Stack", "Developer"], "UE Pro & IT")]
    T = 7
    reach = [0.0, 0.3, 0.6]
    sw, rise = 140, 96
    defs = [
        '<clipPath id="clip"><rect width="460" height="400" rx="18"/></clipPath>',
        grad("border", [AMBER, CORAL, PINK]),
        grad("step", [AMBER, CORAL], 0, 0, 0, 1),
        grad("climber", ["#FFFFFF", AMBER]),
        grad("glow", [(0, AMBER, 0.3), (1, AMBER, 0)], radial=True),
        '<filter id="soft" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="4"/></filter>',
    ]
    css = (rule(".flag", "animation:wave 1.6s ease-in-out infinite;transform-box:fill-box;transform-origin:left center")
           + keyframes("wave", [("0%,100%", "transform:skewY(0)"), ("50%", "transform:skewY(-10deg)")]))
    for i, r in enumerate(reach):
        start = "0%" if i == 0 else f"0%,{r * 100:.0f}%"
        css += rule(f".s{i}", f"animation:s{i} {T}s ease-out -{T * 0.8:.1f}s infinite") + keyframes(f"s{i}", [
            (start, "opacity:.25"), (f"{r * 100 + 4:.0f}%,94%", "opacity:1"), ("100%", "opacity:.25")])
    body = ['<g clip-path="url(#clip)">', '<rect width="460" height="400" fill="#0D1117"/>',
            '<circle cx="400" cy="60" r="200" fill="url(#glow)"/>',
            txt(22, 34, "career.climb()", 13, AMBER, 600, cls="mono"),
            txt(438, 34, "Dec 2018 → Present", 12, "#8B949E", anchor="end", cls="mono"),
            '<line x1="16" y1="372" x2="444" y2="372" stroke="#30363D"/>']
    tops = []
    for i, (role_lines, sub) in enumerate(steps):
        x, top = 16 + i * (sw + 4), 314 - i * rise
        cx = x + sw // 2
        tops.append((cx, top))
        body += [f'<rect x="{x}" y="{top}" width="{sw}" height="{372 - top}" rx="8" fill="url(#step)" '
                 f'fill-opacity="{0.2 + i * 0.15:.2f}"/>',
                 f'<rect class="s{i}" x="{x}" y="{top}" width="{sw}" height="4" rx="2" fill="{AMBER}"/>']
        y = top + 24
        for line in role_lines:
            body.append(txt(cx, y, line, 12.5, "#FFFFFF", 700, "middle"))
            y += 16
        body.append(txt(cx, y + 1, sub, 10.5, "#E6D5C3", anchor="middle"))
    fx, ftop = tops[-1][0] + sw // 2 - 14, tops[-1][1]
    body += [f'<path d="M{fx} {ftop}V{ftop - 36}" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round"/>',
             f'<path class="flag" d="M{fx} {ftop - 36}h20l-5 7 5 7h-20z" fill="{CORAL}"/>']
    path = f"M{tops[0][0]} {tops[0][1] - 10}"
    for (ax, ay), (bx, by) in zip(tops, tops[1:]):
        path += f"Q{(ax + bx) / 2} {by - 46} {bx} {by - 10}"
    # Begin mid-loop so the first frame shows the climber at the summit beside the flag.
    motion = (f'<animateMotion dur="{T}s" begin="-{T * 0.8:.1f}s" repeatCount="indefinite" path="{path}" calcMode="linear" '
              'keyPoints="0;0;0.5;0.5;1;1" keyTimes="0;0.1;0.3;0.4;0.6;1"/>')
    body += [f'<circle r="10" fill="{AMBER}" filter="url(#soft)">{motion}</circle>',
             f'<circle r="7" fill="url(#climber)">{motion}</circle>']
    body += ["</g>", '<rect x=".75" y=".75" width="458.5" height="398.5" rx="17.25" stroke="url(#border)" '
             'stroke-opacity=".6" stroke-width="1.5"/>']
    write("career-climb.svg", svg_doc(W, H, "Career climb at Logitech: Manufacturing → Analyst → "
                                      "Full Stack Developer for UE Pro & IT Software Development", defs, body, css))


def build_interests():
    W, H = 460, 280
    tiles = [("Traveling", "new places & ideas", [SKY, VIOLET]),
             ("Hiking", "trails & summits", [TEAL, "#1B7F5C"]),
             ("Learning", "always leveling up", [AMBER, CORAL])]
    defs = [grad(f"t{i}", c) for i, (_, _, c) in enumerate(tiles)]
    css = (rule(".fl", "animation:fl 4s ease-in-out infinite")
           + keyframes("fl", [("0%,100%", "transform:translateY(0)"), ("50%", "transform:translateY(-6px)")])
           + rule(".orbit", "animation:spin 6s linear infinite;transform-origin:80px 112px")
           + keyframes("spin", [("to", "transform:rotate(360deg)")])
           + rule(".sun", "animation:rise 4s ease-in-out infinite")
           + keyframes("rise", [("0%,100%", "transform:translateY(10px)"), ("50%", "transform:translateY(-4px)")])
           + rule(".trail", "stroke-dasharray:3 5;animation:trail 1.5s linear infinite")
           + keyframes("trail", [("to", "stroke-dashoffset:-16")])
           + rule(".twinkle", "animation:twinkle 2s ease-in-out infinite;transform-box:fill-box;transform-origin:center")
           + keyframes("twinkle", [("0%,100%", "transform:scale(.4);opacity:.3"), ("50%", "transform:scale(1);opacity:1")]))
    star = "M0 -7L1.8 -1.8L7 0L1.8 1.8L0 7L-1.8 1.8L-7 0L-1.8 -1.8z"
    icons = [
        # Globe with an orbiting plane.
        '<circle cx="80" cy="112" r="38" fill="#FFFFFF" fill-opacity=".14" stroke="#FFFFFF" stroke-width="3"/>'
        '<ellipse cx="80" cy="112" rx="15" ry="38" stroke="#FFFFFF" stroke-width="2.2"/>'
        '<path d="M42 112h76M48 94h64M48 130h64" stroke="#FFFFFF" stroke-width="2.2"/>'
        '<g class="orbit"><path d="M90 56L74 52L72 46L69 46L70 53L64 54L64 58L70 59L69 66L72 66L74 60z" fill="#FFFFFF"/></g>',
        # Mountains with a rising sun and a marching trail.
        '<circle class="sun" cx="252" cy="88" r="14" fill="#FFE08A"/>'
        '<path d="M182 150L220 92L258 150z" fill="#FFFFFF" fill-opacity=".55"/>'
        '<path d="M204 150L246 100L284 150z" fill="#FFFFFF"/>'
        '<path class="trail" d="M206 150C222 140 236 136 236 126S248 118 246 106" stroke="#1B7F5C" '
        'stroke-width="2.5" stroke-linecap="round"/>'
        '<path d="M176 150h112" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round"/>',
        # Open book with twinkling sparkles.
        '<path d="M340 100Q358 92 378 100V142Q358 134 340 142z" fill="#FFFFFF"/>'
        '<path d="M382 100Q402 92 420 100V142Q402 134 382 142z" fill="#FFFFFF" fill-opacity=".85"/>'
        '<path d="M348 110h22M348 119h22M348 128h16M390 110h22M390 119h22M390 128h14" stroke="#FF8A5B" '
        'stroke-width="2" stroke-linecap="round"/>'
        + "".join(f'<g transform="translate({x} {y})"><path class="twinkle" d="{star}" fill="#FFFFFF" '
                  f'style="animation-delay:-{d}s"/></g>' for x, y, d in [(352, 76, 0), (410, 70, 0.7), (384, 60, 1.3)]),
    ]
    body = []
    for i, (label, sub, _) in enumerate(tiles):
        x = 10 + i * 150
        body += [f'<g class="fl" style="animation-delay:-{i * 1.2:.1f}s">',
                 f'<rect x="{x}" y="14" width="140" height="252" rx="20" fill="url(#t{i})"/>',
                 f'<rect x="{x}" y="14" width="140" height="252" rx="20" stroke="#FFFFFF" stroke-opacity=".25"/>',
                 icons[i],
                 txt(x + 70, 210, label, 18, "#FFFFFF", 700, "middle"),
                 txt(x + 70, 232, sub, 11.5, "#FFFFFF", 500, "middle", opacity=0.88),
                 "</g>"]
    write("interests.svg", svg_doc(W, H, "Interests: Traveling, Hiking, Learning", defs, body, css))


# ── VI. contact ──────────────────────────────────────────────────────────────

def build_contact():
    W, H = 400, 300
    path = "M80 214C150 120 210 250 280 150S370 60 340 46"
    defs = ['<clipPath id="clip"><rect width="400" height="300" rx="18"/></clipPath>',
            grad("bg", ["#0B1020", "#141238", "#062B2B"]),
            grad("border", [TEAL, VIOLET, PINK]),
            grad("g1", [(0, TEAL, 0.35), (1, TEAL, 0)], radial=True),
            grad("g2", [(0, VIOLET, 0.4), (1, VIOLET, 0)], radial=True)]
    css = (rule(".cloud", "animation:drift 14s linear infinite")
           + keyframes("drift", [("from", "transform:translateX(-80px)"), ("to", "transform:translateX(460px)")])
           + rule(".path", "stroke-dasharray:4 7;animation:dash 1.6s linear infinite")
           + keyframes("dash", [("to", "stroke-dashoffset:-22")]))
    body = ['<g clip-path="url(#clip)">', '<rect width="400" height="300" fill="url(#bg)"/>',
            '<circle cx="60" cy="260" r="160" fill="url(#g1)"/>', '<circle cx="360" cy="40" r="170" fill="url(#g2)"/>']
    for y, s, d in [(70, 1, 0), (120, 0.7, -6), (40, 0.55, -10)]:
        body.append(f'<g class="cloud" style="animation-delay:{d}s;animation-duration:{14 / s:.0f}s">'
                    f'<path transform="translate(0 {y}) scale({s})" '
                    'd="M0 20a14 14 0 0 1 22-12a18 18 0 0 1 34 4a12 12 0 0 1 0 24H4a10 10 0 0 1-4-16z" '
                    'fill="#FFFFFF" fill-opacity=".1"/></g>')
    body += [f'<path class="path" d="{path}" stroke="#FFFFFF" stroke-opacity=".35" stroke-width="2" stroke-linecap="round"/>',
             '<rect x="34" y="206" width="78" height="52" rx="8" fill="#FFFFFF"/>',
             f'<path d="M36 210l37 26 37-26" stroke="{VIOLET}" stroke-width="3" stroke-linejoin="round"/>',
             f'<g><animateMotion dur="5s" repeatCount="indefinite" rotate="auto" path="{path}"/>'
             '<path d="M16 0L-12 -11L-6 0L-12 11z" fill="#FFFFFF"/><path d="M-6 0L16 0L-4 6z" fill="#C7D2FE"/></g>',
             txt(376, 266, "Let's connect", 20, "#FFFFFF", 700, "end"),
             "</g>",
             '<rect x=".75" y=".75" width="398.5" height="298.5" rx="17.25" stroke="url(#border)" '
             'stroke-opacity=".6" stroke-width="1.5"/>']
    write("contact.svg", svg_doc(W, H, "A paper plane flying out of an envelope — let's connect", defs, body, css))


def build_buttons():
    github = simple_path("github")
    icons = {
        "email": '<rect x="-8" y="-6" width="16" height="12" rx="2" stroke="#FFFFFF" stroke-width="1.8"/>'
                 '<path d="M-7.5 -5L0 1L7.5 -5" stroke="#FFFFFF" stroke-width="1.8" stroke-linejoin="round"/>',
        "website": '<circle r="8" stroke="#FFFFFF" stroke-width="1.8"/>'
                   '<ellipse rx="3.5" ry="8" stroke="#FFFFFF" stroke-width="1.6"/>'
                   '<path d="M-8 0h16" stroke="#FFFFFF" stroke-width="1.6"/>',
        "linkedin": '<rect x="-8" y="-8" width="16" height="16" rx="3.5" fill="#FFFFFF"/>'
                    + txt(0, 4.6, "in", 12, "#0A66C2", 800, "middle"),
        "github": f'<path transform="translate(-8 -8) scale(.6667)" d="{github}" fill="#FFFFFF"/>',
    }
    buttons = [("email", "hello@platmesh.com", PINK, VIOLET), ("website", "Website", TEAL, SKY),
               ("linkedin", "LinkedIn", "#0A66C2", SKY), ("github", "GitHub", "#24292F", VIOLET)]
    for slug, label, c1, c2 in buttons:
        w = round(len(label) * 15 * 0.55 + 70)
        defs = [f'<clipPath id="clip"><rect width="{w}" height="46" rx="23"/></clipPath>',
                grad("bg", [c1, c2], 0, 0, 1, 0),
                grad("sheen", [(0, "#FFFFFF", 0), (0.5, "#FFFFFF", 0.35), (1, "#FFFFFF", 0)], 0, 0, 1, 0)]
        css = (rule(".sheen", "animation:sweep 5s ease-in-out infinite")
               + keyframes("sweep", [("0%", "transform:translateX(-80px) skewX(-20deg)"),
                                     ("45%,100%", f"transform:translateX({w + 80}px) skewX(-20deg)")]))
        body = ['<g clip-path="url(#clip)">', f'<rect width="{w}" height="46" fill="url(#bg)"/>',
                '<rect class="sheen" y="-10" width="50" height="66" fill="url(#sheen)"/>', "</g>",
                '<circle cx="24" cy="23" r="15" fill="#FFFFFF" fill-opacity=".2"/>',
                f'<g transform="translate(24 23)">{icons[slug]}</g>',
                txt((48 + w - 18) / 2, 28.5, label, 15, "#FFFFFF", 700, "middle")]
        write(f"buttons/{slug}.svg", svg_doc(w, 46, label, defs, body, css))


def build_footer():
    W, H = 1000, 150

    def wave(base, amp, length, phase):
        pts = " L".join(f"{x} {base + amp * math.sin(x / length * 2 * math.pi + phase):.1f}"
                        for x in range(0, 2001, 10))
        return f"M{pts} V{H} H0z"

    defs = [grad("bg", [VIOLET, SKY, TEAL, PINK], 0, 0, 1, 0),
            '<mask id="waves">'
            f'<path class="w1" d="{wave(50, 10, 500, 0)}" fill="#FFFFFF" fill-opacity=".3"/>'
            f'<path class="w2" d="{wave(64, 12, 1000, 1.2)}" fill="#FFFFFF" fill-opacity=".5"/>'
            f'<path class="w3" d="{wave(82, 8, 500, 2.4)}" fill="#FFFFFF"/>'
            "</mask>"]
    css = "".join(rule(f".w{i}", f"animation:slide {d}s linear infinite") for i, d in [(1, 16), (2, 24), (3, 12)])
    css += keyframes("slide", [("from", "transform:translateX(0)"), ("to", "transform:translateX(-1000px)")])
    body = [f'<rect width="{W}" height="{H}" fill="url(#bg)" mask="url(#waves)"/>',
            txt(500, 124, "Thanks for stopping by!", 22, "#FFFFFF", 700, "middle")]
    write("footer.svg", svg_doc(W, H, "Thanks for stopping by!", defs, body, css))


def build_logos():
    """Small organisation tiles for the experience table."""
    logos = [
        # The "logi" wordmark is short and wide, so draw it larger than the default 5.67x.
        ("logitech", "Logitech", dict(si("logitech", "#00B8FC", "Logitech"), scale=8.5)),
        ("gdg", "Google Developer Group", si("google", "#4285F4", "Google Developer Group")),
    ]
    for slug, title, icon in logos:
        write(f"logos/{slug}.svg", svg_doc(64, 64, title, [], [
            f'<svg width="64" height="64" viewBox="0 0 256 256">{tile(icon, "l_")}</svg>']))


HEADERS = [
    ("about", "01", "About Me", "Who I am, where I've been, and what drives me", VIOLET, SKY, "user"),
    ("skills", "02", "Technical Skills & Tools", "Languages, frameworks, practices and platforms", SKY, TEAL, "code"),
    ("projects", "03", "Featured Projects", "A few things I've designed, architected and shipped", PINK, VIOLET, "rocket"),
    ("experience", "04", "Experience, Interests & Goals", "Where I've grown, what I love, and where I'm headed",
     AMBER, CORAL, "briefcase"),
    ("contact", "05", "Contact", "Get in touch", TEAL, VIOLET, "send"),
]


def main():
    print("Building README assets…")
    build_banner()
    for args in HEADERS:
        build_header(*args)
    build_about_code()
    build_education()
    build_stack("stack-languages.svg", "Languages & Frameworks", LANGUAGE_ROWS)
    build_stack("stack-platforms.svg", "Data, Cloud & Platforms", PLATFORM_ROWS)
    build_projects()
    build_career()
    build_interests()
    build_contact()
    build_buttons()
    build_logos()
    build_footer()
    print("Done.")


if __name__ == "__main__":
    main()
