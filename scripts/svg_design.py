"""Small dependency-free SVG vocabulary for the engineering lab."""

from html import escape

BG = "#080D18"
SURFACE = "#111C2E"
BLUE = "#3B82F6"
HIGHLIGHT = "#60A5FA"
TEXT = "#F8FAFC"
MUTED = "#94A3B8"
BORDER = "#25344A"


def text(x, y, value, size=20, color=TEXT, weight=400, mono=False, anchor=None, spacing=None):
    attrs = f' x="{x}" y="{y}" fill="{color}" font-size="{size}" font-weight="{weight}"'
    if mono:
        attrs += ' font-family="ui-monospace, SFMono-Regular, Consolas, Liberation Mono, monospace"'
    if anchor:
        attrs += f' text-anchor="{anchor}"'
    if spacing is not None:
        attrs += f' letter-spacing="{spacing}"'
    return f'<text{attrs}>{escape(str(value))}</text>'


def line(x1, y1, x2, y2, color=BORDER, width=1, extra=""):
    return f'<path d="M{x1} {y1}H{x2}" fill="none" stroke="{color}" stroke-width="{width}" {extra}/>' if y1 == y2 else f'<path d="M{x1} {y1}L{x2} {y2}" fill="none" stroke="{color}" stroke-width="{width}" {extra}/>'


def path(d, color=BORDER, width=1.5, extra=""):
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round" {extra}/>'


def rect(x, y, w, h, fill=SURFACE, stroke=BORDER, radius=10, extra=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}" {extra}/>'


def circle(x, y, r=3, fill=HIGHLIGHT, extra=""):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" {extra}/>'


def label(x, y, value, size=14):
    return text(x, y, value, size, MUTED, 500, mono=True, spacing=1.5)


def node(x, y, w, h, title, subtitle=None, accent=False, size=18):
    s = rect(x, y, w, h, stroke=BLUE if accent else BORDER, radius=5)
    s += line(x + 10, y + 10, x + 20, y + 10, HIGHLIGHT if accent else MUTED, 1, 'opacity=".6"')
    s += text(x + w / 2, y + (h / 2 + 6 if not subtitle else h / 2 - 3), title, size, weight=500, anchor="middle")
    if subtitle:
        s += text(x + w / 2, y + h / 2 + 19, subtitle, 14, MUTED, mono=True, anchor="middle")
    return s


def svg(width, height, title, description, body, motion=False):
    definitions = []
    if "url(#grid)" in body:
        definitions.append(f'<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" stroke="{BORDER}" stroke-opacity=".26" stroke-width=".7"/></pattern>')
    if "url(#light)" in body:
        definitions.append(f'<radialGradient id="light"><stop stop-color="{BLUE}" stop-opacity=".15"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></radialGradient>')
    if "url(#arrow)" in body:
        definitions.append(f'<marker id="arrow" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M1 1L7 4L1 7" stroke="{HIGHLIGHT}" stroke-width="1.3" fill="none"/></marker>')
    defs = "<defs>" + "".join(definitions) + "</defs>" if definitions else ""
    style = ""
    if motion:
        style = '''<style>
        @keyframes process { 0%,19%,27%,100% {opacity:.25} 23% {opacity:1} }
        @keyframes background { 0%,74%,91%,100% {opacity:.25} 82% {opacity:1} }
        @keyframes cursor { 0%,45% {opacity:1} 55%,100% {opacity:0} }
        .process {animation:process 14s ease-in-out infinite}
        .process-worker {animation:background 14s ease-in-out infinite}
        .cursor {animation:cursor 1.8s step-end infinite}
        @media (prefers-reduced-motion:reduce) {
          .motion {display:none} .process,.process-worker,.cursor {animation:none}
        }
        </style>'''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title>
<desc id="desc">{escape(description)}</desc>
{defs}
{style}
<g font-family="Arial, Helvetica, Liberation Sans, sans-serif">
{rect(.5, .5, width - 1, height - 1, BG, BORDER, 14)}
{body}
</g>
</svg>
'''


def packet(d, start, end):
    """One edge's part of a calm 14s request cycle; invisible if SMIL is unavailable."""
    return f'''<g class="motion"><circle r="4" fill="{TEXT}" opacity="0">
<animateMotion dur="14s" repeatCount="indefinite" path="{d}" keyPoints="0;0;1;1" keyTimes="0;{start};{end};1" calcMode="linear"/>
<animate attributeName="opacity" dur="14s" repeatCount="indefinite" values="0;0;1;1;0;0" keyTimes="0;{start};{start + .005:.3f};{end - .005:.3f};{end};1"/>
</circle></g>'''
