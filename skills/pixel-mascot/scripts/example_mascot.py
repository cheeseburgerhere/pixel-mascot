"""Example: Miso, an original 32x32 mascot built with pixelkit: a ginger tabby
cat with a bell collar, sitting, with a curled tail. Three states: idle
(breathing, a slow tail, a blink), happy (hopping, sparkles) and sleep (Z's).

    python example_mascot.py out.svg [state]

`state` is the one the file plays on its own (default: idle); an app shows
another by setting the root's class (`<svg class="happy">`). Run it with this
kit's folder on PYTHONPATH.

Copy this file to start a new mascot of any kind. It shows the techniques that
carry over to every type: back-to-front parts, polygons for angular shapes,
edge shading, per-state faces, secondary motion on appendages (here ears and
tail; on a person it would be hair, on an object antennae or a cable),
effects, per-part outlines and layered step animation. Nothing here is
specific to cats except the shapes.
"""
import os
import sys

from pixel_overrides import apply_overrides
from pixelkit import Sprite, ellipse, line, path, plus, polygon, rect

NAME = "miso"  # names the hand-edits file, <NAME>_overrides.json, next to this builder
N = 32
s = Sprite(N)

# Parts, back to front. Each animates as a unit and carries its own outline.
# `ears` is drawn inside the head group (below), so it rides along with every
# head move and can still flop on its own: nest an appendage in what it is
# attached to.
for name in ("tail", "body", "ears", "head"):
    s.part(name)

# --- tail: an appendage behind the body, its base hidden, so it can wag.
tail = [(21, 28), (25, 27), (28, 24), (29, 20), (28, 16), (26, 14)]
s.paint("tail", path(tail, thick=2), "fur")
s.paint("tail", path(tail[-2:], thick=2), "belly")                         # light tip
s.paint("tail", {(26, 26), (28, 22), (29, 18)}, "fur-dark", only={"fur"})  # tabby rings

# --- body: sitting, cropped by the frame, cream belly and front paws.
s.paint("body", ellipse(16, 27.5, 8.5, 6), "fur")
s.paint("body", ellipse(16, 28.5, 4.5, 4.5), "belly")
s.paint("body", rect(11, 29, 13, N + 1) | rect(19, 29, 21, N + 1), "belly")
s.paint("body", {(12, 31), (20, 31)}, "fur-dark")                         # toe gaps

# --- ears: polygons, pink inside.
s.paint("ears", polygon([(4, 11), (6, 0), (15, 7)]) | polygon([(17, 7), (26, 0), (28, 11)]), "fur")
s.paint("ears", polygon([(6, 8), (7, 2.5), (12, 6.5)]) | polygon([(20, 6.5), (25, 2.5), (26, 8)]), "ear-inner")

# --- head: big and round (the face is what reads at 128 px).
s.paint("head", ellipse(16, 14.5, 11, 9.5), "fur")
s.paint("head", ellipse(16, 18.5, 6.5, 4.5), "belly")                      # muzzle
for x0, y0, y1 in ((14, 7, 9), (16, 6, 9), (18, 7, 9)):                    # forehead stripes
    s.paint("head", line(x0, y0, x0, y1), "fur-dark", only={"fur"})
s.paint("head", {(5, 14), (6, 15), (26, 15), (27, 14)}, "fur-dark", only={"fur"})  # cheek stripes
s.paint("head", line(7, 19, 9, 19) | line(7, 21, 9, 20) | line(22, 19, 24, 19) | line(22, 20, 24, 21), "whisker", only={"fur", "belly"})
# Soft shading on the lower edge of the head, against the body.
s.shade_edges("head", "fur", "fur-dark", against={None}, sides=((0, 1),))
# Collar and bell under the chin: one bold accessory reads better than many small ones.
s.paint("head", line(9, 23, 23, 23) | line(11, 24, 21, 24), "collar")
s.paint("head", rect(15, 24, 17, 26), "bell")
s.paint("head", {(15, 24)}, "bell-shine")
s.paint("head", {(16, 26)}, "bell-dark")

s.outline()

# --- faces, one group per state, toggled by opacity.
NOSE = {(15, 18): "nose", (16, 18): "nose"}
EYES = [(10, 13), (19, 13)]  # top-left of each 4x5 eye


def round_eye(ex, ey):
    """Round cat eye with a big shine."""
    rows = [
        [None, "pupil", "pupil", None],
        ["shine", "shine", "pupil", "pupil"],
        ["shine", "iris", "pupil", "pupil"],
        ["iris", "iris", "iris", "pupil"],
        [None, "iris", "iris", None],
    ]
    return {(ex + dx, ey + dy): cls for dy, row in enumerate(rows) for dx, cls in enumerate(row) if cls}


def arc_eye(ex, ey, up):
    """^ when up (happy), u when down (asleep, or a blink)."""
    if up:
        return {(ex, ey + 3): "lash", (ex + 1, ey + 2): "lash", (ex + 2, ey + 2): "lash", (ex + 3, ey + 3): "lash"}
    return {(ex, ey + 2): "lash", (ex + 1, ey + 3): "lash", (ex + 2, ey + 3): "lash", (ex + 3, ey + 2): "lash"}


def merge(*maps):
    out = {}
    for m in maps:
        out.update(m)
    return out


W_MOUTH = {c: "mouth" for c in {(13, 19), (14, 20), (15, 19), (16, 19), (17, 20), (18, 19)}}
faces = {
    "f-open": merge(*(round_eye(*e) for e in EYES), NOSE, W_MOUTH),
    "f-blink": merge(*(arc_eye(*e, up=False) for e in EYES), NOSE, W_MOUTH),
    "f-happy": merge(*(arc_eye(*e, up=True) for e in EYES), NOSE,
                     {c: "mouth" for c in rect(14, 19, 17, 20)}, {(15, 20): "tongue", (16, 20): "tongue"},
                     {c: "blush" for c in {(8, 18), (9, 18), (22, 18), (23, 18)}}),
    "f-sleep": merge(*(arc_eye(*e, up=False) for e in EYES), NOSE, {(15, 20): "mouth", (16, 20): "mouth"}),
}

effects = (
    s.fx("fx-spark", "spark", [plus(2, 4), plus(2, 24), plus(29, 2)])
    + s.fx("fx-zz", "zz", [rect(26, 0, 29, 0) | {(28, 1), (27, 2)} | rect(26, 3, 29, 3), rect(29, 5, 31, 5) | {(30, 6)} | rect(29, 7, 31, 7)])
)

# Colors live in CSS classes. Motion is steps(1) and whole cells. Appendages
# lag a quarter cycle at most: half a cycle reads as a trail. The first state
# the CSS styles (here idle) comes first in the studio and the preview.
STYLE = """
.outline{fill:#412402}
.fur{fill:#EF9F27}.fur-dark{fill:#BA7517}.belly{fill:#FAEEDA}.ear-inner{fill:#F4C0D1}.whisker{fill:#FFFFFF}
.collar{fill:#D85A30}.bell{fill:#FAC775}.bell-shine{fill:#FFFFFF}.bell-dark{fill:#BA7517}
.pupil{fill:#173404}.iris{fill:#639922}.shine{fill:#FFFFFF}.lash{fill:#412402}
.nose{fill:#D4537E}.mouth{fill:#712B13}.tongue{fill:#ED93B1}.blush{fill:#F4C0D1}
.spark,.zz{fill:#7F77DD}
.idle .rig{animation:hop 1.6s steps(1) infinite}
.idle .tail{animation:wag 1.6s steps(1) -.4s infinite}
.idle .f-open{animation:shut 3.2s steps(1) infinite}
.idle .f-blink{animation:open 3.2s steps(1) infinite}
.f-blink,.f-happy,.f-sleep,.fx-spark,.fx-zz{opacity:0}
.happy .f-open,.sleep .f-open{opacity:0}
.happy .f-happy,.happy .fx-spark,.sleep .f-sleep,.sleep .fx-zz{opacity:1}
.happy .rig{animation:hop .5s steps(1) infinite}
.happy .ears{animation:hop .5s steps(1) -.125s infinite}
.happy .tail{animation:wag .5s steps(1) infinite}
.happy .s1{animation:blink .5s steps(1) infinite}
.happy .s2{animation:blink .5s steps(1) -.25s infinite}
.happy .s3{animation:blink 1s steps(1) infinite}
.sleep .rig{animation:hop 3.6s steps(1) infinite}
.sleep .s1,.sleep .s2{animation:float 2.4s steps(1) infinite}
.sleep .s2{animation-delay:-1.2s}
@keyframes hop{50%{transform:translateY(-1px)}}
@keyframes wag{0%{transform:translateX(-1px)}50%{transform:translateX(1px)}}
@keyframes float{50%{transform:translateY(-1px)}}
@keyframes blink{50%{opacity:0}}
@keyframes shut{94%{opacity:0}}
@keyframes open{0%{opacity:0}94%{opacity:1}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
""".strip()

head = (
    '<g class="head">'
    + s.group("ears")
    + s.by_class(s.parts["head"])
    + "".join(s.group(name, cells) for name, cells in faces.items())
    + "</g>"
)
body = '<g class="rig">' + s.group("tail") + s.group("body") + head + "</g>" + effects
state = sys.argv[2] if len(sys.argv) > 2 else "idle"
svg = s.svg(body, STYLE, title="Miso the cat", size=128, state=state)
# Hand edits from the studio's pixel editor (studio/server.py) go on last, so
# rebuilding never loses them.
svg = apply_overrides(svg, os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{NAME}_overrides.json"))
with open(sys.argv[1], "w", encoding="utf-8", newline="\n") as f:  # same bytes on every OS
    f.write(svg)
print(f"wrote {sys.argv[1]}: {len(svg)} characters")
