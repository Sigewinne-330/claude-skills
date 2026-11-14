"""Tiny helper kit for Sidspark blog figures (inline SVG inside a WordPress Custom HTML block).

Usage in a per-post figure script:

    import sys; sys.path.insert(0, "/abs/path/to/sidspark-blog-post/scripts")   # this skill's scripts/ folder
    from svgkit import *
    def fig_setup():
        b = [defs(marker("s1r", RED))]          # marker ids MUST be unique across the whole post
        b.append(floor(40, 600, 300))
        b.append(arrow(104, 205, 58, 205, RED, "s1r"))
        b.append(text(80, 192, "recoils", 13, RED, italic=False, family=SANS))
        b.append(text(170, 268, sub("m", "1"), 18))   # italic m with upright subscript 1
        return svg(640, 330, "".join(b), "Alt text describing the figure")
    save("figs/setup.svg", fig_setup())

Then render to check:  rsvg-convert -w 1000 -b white figs/setup.svg -o figs/setup.png  (and Read the PNG).

Rules baked in (why they matter):
- No <style> element: inline SVG CSS would leak into the whole blog page.
- Marker ids are page-global once inlined: prefix them per figure (s1r, s2b, ...).
- Never put "$" or "\\(" in <text>: Simple MathJax would try to typeset it.
- Fonts are set per <text> (Georgia italic for symbols, Helvetica for annotations), and
  subscripts use dy shifts rather than baseline-shift so every renderer agrees.
"""
import math

INK, BLUE, RED, GREY, FILL, WHITE = "#1f2328", "#2563a8", "#c2410c", "#8a8f98", "#efe9dc", "#ffffff"
SERIF = "Georgia, serif"
SANS = "Helvetica, Arial, sans-serif"


def defs(*items):
    return "<defs>" + "".join(items) + "</defs>"


def marker(mid, color):
    """Arrowhead; use with marker-end / marker-start (auto-start-reverse flips it for the start)."""
    return (f'<marker id="{mid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
            f'markerHeight="7" orient="auto-start-reverse"><path d="M0,1 L10,5 L0,9 z" fill="{color}"/></marker>')


def line(x1, y1, x2, y2, color=INK, w=1.5, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{w}"{d}/>'


def arrow(x1, y1, x2, y2, color, mid, w=2.2, dash=None, both=False):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    s = f' marker-start="url(#{mid})"' if both else ''
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" '
            f'stroke-width="{w}"{d}{s} marker-end="url(#{mid})"/>')


def circle(cx, cy, r, fill=WHITE, stroke=INK, w=2):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>'


def dot(cx, cy, r=3, color=INK):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{color}"/>'


def path(d, fill="none", stroke=INK, w=2, dash=None):
    ds = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"{ds}/>'


def rect_rot(cx, cy, w, h, deg, fill=WHITE, stroke=INK, sw=2):
    """Rectangle centred at (cx, cy) rotated by deg (e.g. a block on an incline)."""
    return (f'<rect x="{cx-w/2:.1f}" y="{cy-h/2:.1f}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{sw}" transform="rotate({deg:.2f} {cx:.1f} {cy:.1f})"/>')


def text(x, y, s, size=17, color=INK, italic=True, anchor="middle", family=SERIF, weight="normal"):
    st = ' font-style="italic"' if italic else ''
    wt = f' font-weight="{weight}"' if weight != "normal" else ''
    an = '' if anchor == "middle" else f' text-anchor="{anchor}"'
    return (f'<text x="{x:.0f}" y="{y:.0f}" font-family="{family}" font-size="{size}" fill="{color}"'
            f'{st}{wt}{an}>{s}</text>')


def sub(main, s, size=12):
    """main followed by an upright subscript (dy shift, then restore)."""
    return f'{main}<tspan dy="4" font-size="{size}" font-style="normal">{s}</tspan><tspan dy="-4"></tspan>'


def bold(s):
    """Bold glyph inside a text() string, e.g. vectors: text(x, y, sub(bold('r'), '1'))."""
    return f'<tspan font-weight="bold">{s}</tspan>'


def angle_arc(cx, cy, r, a0_deg, a1_deg, color=INK, w=1.3):
    """Arc of radius r around (cx, cy) from screen angle a0 to a1 (degrees, y axis pointing DOWN,
    0 = +x, 90 = straight down). Sweep goes in the direction of increasing angle."""
    a0, a1 = math.radians(a0_deg), math.radians(a1_deg)
    x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
    x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
    large = 1 if abs(a1_deg - a0_deg) > 180 else 0
    sweep = 1 if a1_deg > a0_deg else 0
    return f'<path d="M{x0:.1f},{y0:.1f} A{r},{r} 0 {large} {sweep} {x1:.1f},{y1:.1f}" fill="none" stroke="{color}" stroke-width="{w}"/>'


def floor(x0, x1, y, step=18):
    """Ground line with hatching below (one compact <path> instead of dozens of lines)."""
    d = "".join(f"M{x:g},{y:g}l-11,12" for x in range(int(x0) + 10, int(x1) + 1, step))
    return line(x0, y, x1, y, INK, 1.8) + f'<path d="{d}" stroke="{GREY}" stroke-width="1.2"/>'


def svg(w, h, body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{label}" '
            f'style="max-width:100%;height:auto;display:block;margin:0 auto" text-anchor="middle">{body}</svg>')


def save(fname, content):
    assert "<style" not in content, "no <style> in inline SVG"
    assert "$" not in content, "no $ in SVG text (MathJax would grab it)"
    with open(fname, "w", encoding="utf-8") as fh:
        fh.write(content)
