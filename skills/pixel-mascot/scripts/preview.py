"""Render a pixel mascot SVG to a PNG sheet: one still frame per state.

    python preview.py mascot.svg sheet.png [--scale 8] [--states idle,happy]

States are classes the root <svg> can carry (`.happy .head{...}` styles the
head in `happy`). Left to right, the sheet shows the states from --states, or
else from profile.json next to this script, or else every state the SVG's CSS
uses, in the order they first appear. Pure standard library, no installs. It
understands what pixelkit mascots use:
  - <rect> cells inside nested <g class="..."> groups,
  - fills from one-class CSS rules, `.a,.b{fill:#hex}` or `{fill:var(--x,#hex)}`
    (the fallback hex stands in for the variable),
  - visibility from opacity rules: `.x{opacity:0}` hides x in every state,
    `.happy .x{opacity:1}` shows it in one state, later rules win.
It draws the resting pose only: animations (transforms, blinks) are ignored, so
check motion in the studio. Read the PNG to look at the sprite closely.
"""
import json
import os
import re
import struct
import sys
import zlib

PROFILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "profile.json")


def load_profile():
    """Optional settings for an app that shows the mascot (SKILL.md, "profile.json")."""
    if not os.path.exists(PROFILE):
        return {}
    with open(PROFILE, encoding="utf-8") as f:
        return json.load(f)


def find_states(svg):
    """State classes in first-use order: the first class of a descendant
    selector (`.happy .head`) that no element in the drawing carries."""
    style = re.search(r"<style>(.*?)</style>", svg, re.S).group(1)
    drawing = svg.split("</style>", 1)[1]
    used = {c for attr in re.findall(r'class="([^"]*)"', drawing) for c in attr.split()}
    states = []
    for selectors in re.findall(r"([^{}]+)\{", style):
        for sel in selectors.split(","):
            words = sel.split()
            if len(words) >= 2 and re.fullmatch(r"\.[\w-]+", words[0]):
                name = words[0][1:]
                if name not in used and name not in states:
                    states.append(name)
    return states


def states_for(svg, given=None):
    """--states, else the profile's, else what the SVG uses, else one unnamed state."""
    if given:
        return given
    profile = load_profile().get("states")
    if profile:
        return [s["class"] for s in profile]
    return find_states(svg) or [""]


def visibility_rules(style, states):
    """[(state or None, class, visible)] in source order."""
    rules = []
    for selectors, value in re.findall(r"([^{}]+)\{opacity:([01])\}", style):
        for sel in selectors.split(","):
            words = sel.strip().split()
            if len(words) == 1 and words[0].startswith("."):
                rules.append((None, words[0][1:], value == "1"))
            elif len(words) == 2 and words[0][1:] in states:
                rules.append((words[0][1:], words[1][1:], value == "1"))
    return rules


def is_visible(classes, state, rules):
    for cls in classes:
        shown = True
        for rule_state, rule_cls, value in rules:
            if rule_cls == cls and rule_state in (None, state):
                shown = value
        if not shown:
            return False
    return True


def main():
    args = sys.argv[1:]
    scale, given = 8, None
    if "--scale" in args:
        i = args.index("--scale")
        scale = int(args[i + 1])
        del args[i : i + 2]
    if "--states" in args:
        i = args.index("--states")
        given = [s for s in args[i + 1].split(",") if s]
        del args[i : i + 2]
    src_path, out_path = args
    with open(src_path, encoding="utf-8") as f:
        src = f.read()
    states = states_for(src, given)
    style = re.search(r"<style>(.*?)</style>", src, re.S).group(1)
    fills = {}
    for sel, col in re.findall(r"([.\w,-]+)\{fill:(?:var\(--[\w-]+,)?(#[0-9A-Fa-f]{6})", style):
        for cls in sel.split(","):
            fills[cls.strip(".")] = col
    rules = visibility_rules(style, states)
    n = int(re.search(r'viewBox="0 0 (\d+)', src).group(1))
    side, gap = n * scale, 2 * scale
    width = len(states) * (side + gap) - gap
    page, bg = (30, 30, 29), (42, 41, 40)
    img = [[page] * width for _ in range(side)]

    for m, state in enumerate(states):
        ox = m * (side + gap)
        for y in range(side):
            for x in range(side):
                img[y][ox + x] = bg
        stack = []
        for tok in re.finditer(r'<g class="([^"]+)">|</g>|<rect x="(-?\d+)" y="(-?\d+)" width="(\d+)" height="(\d+)"/>', src):
            if tok.group(1):
                stack.append(tok.group(1).split())
                continue
            if tok.group(0) == "</g>":
                stack.pop()
                continue
            if not is_visible([c for g in stack for c in g], state, rules):
                continue
            col = next((fills[c] for g in reversed(stack) for c in g if c in fills), None)
            if not col:
                continue
            rgb = tuple(int(col[i : i + 2], 16) for i in (1, 3, 5))
            x, y, w, h = map(int, tok.group(2, 3, 4, 5))
            for yy in range(max(0, y * scale), min((y + h) * scale, side)):
                for xx in range(max(0, x * scale), min((x + w) * scale, side)):
                    img[yy][ox + xx] = rgb

    raw = b"".join(b"\0" + bytes(c for px in row for c in px) for row in img)

    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, side, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw))
        + chunk(b"IEND", b"")
    )
    with open(out_path, "wb") as f:
        f.write(png)
    print(f"wrote {out_path}: {', '.join(s or '(no state)' for s in states)}")


if __name__ == "__main__":
    main()
