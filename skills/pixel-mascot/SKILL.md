---
name: pixel-mascot
description: "Make, edit or fix an animated pixel-art sprite as one SVG file: a mascot, character, animal, creature or object, with animation states the user names (default: one idle loop). Builds it from a Python builder script, renders a PNG preview, and opens a local studio that shows every state animating side by side with a pixel editor. Use when someone asks for a pixel mascot, sprite or avatar, wants an existing one to look or move differently, wants to hand-edit its pixels or watch it animate in a browser, or reports one that is frozen, misdrawn or leaves trails."
---

# Making a pixel mascot

A mascot is one SVG file of pixel art with CSS step animation. It can have
several **states** (idle, happy, sleep, walk, attack…), each a class on the
root element: `<svg class="happy">` plays `happy`. Build mascots with code,
never by hand-editing hundreds of `<rect>`s: this skill's `scripts/` folder
(`<kit>` below) holds a small kit and a worked example. Everything is Python
standard library; nothing to install.

Read `LESSONS.md` beside this file before drawing anything. It lists, with
the symptom, the cause and the fix, what went wrong while the first mascots
were made, and most of it will go wrong again if skipped.

## Where things go

Ask the user where to keep the mascot. If they have no preference, use
`~/pixel-mascots/<name>/` (on Windows `%USERPROFILE%\pixel-mascots\<name>\`):

| File | What it is |
| --- | --- |
| `make_<name>.py` | the builder: every change is an edit here and a re-run |
| `<name>.svg` | the build output, the mascot itself |
| `<name>_overrides.json` | the user's hand edits from the studio, applied last by the builder |
| `sheet.png` | the preview, one still frame per state |

`<name>` is lowercase letters, digits and hyphens. Never put a user's files in
`<kit>`: it belongs to the installed plugin and is replaced on update.

## Running the scripts

Use whichever Python the machine has: `python3` (macOS, Linux), `python`
(Windows), or `uv run python` where a shim blocks bare `python`. Builders
import the kit, so put `<kit>` on `PYTHONPATH` when running one:

```bash
PYTHONPATH="<kit>" python3 make_<name>.py <name>.svg
```

```powershell
$env:PYTHONPATH = "<kit>"; python make_<name>.py <name>.svg
```

`preview.py` and the studio need no `PYTHONPATH`; the studio sets it for the
builders it runs.

## What the SVG must do

1. One state per root class. Style each state with `.<state> .part{...}`
   selectors; the class names are the user's state names (lowercase,
   hyphens). The builder writes a default state onto the root
   (`s.svg(..., state="idle")`), so the file animates on its own in a browser
   or an `<img>`; an app shows another state by changing the root's class.
   With no states named, make one: `idle`.
2. Put every color in a CSS class inside its own `<style>`. A CSS variable
   (`var(--accent,#hex)`) works only there, never as a `fill=` attribute.
3. Animate with `steps(1)` keyframes that move whole cells (`translateY(-1px)`
   in a viewBox of cells) or blink opacity.
4. Have a `<title>` (alt text) and no `<script>`, no `on…=`, no external
   images, fonts or links, so it is safe to show anywhere.
5. Set its drawn size with `width`/`height` on the root, a whole multiple of
   the grid: 32 cells at 128 px (4 px per cell), 20 cells at 80 px.
6. Respect reduced motion unless the user says otherwise:
   `@media (prefers-reduced-motion:reduce){*{animation:none!important}}`.

## The workflow

1. **Pin down what the mascot is, its states, and its 3-5 identity
   features.** Ask what makes it recognizable at 128 px, exaggerate exactly
   those, and drop everything else. Ask which states it needs; with no
   answer, make one idle loop. The user's idea decides, not the example here.
   If the user shares other artists' art, use it for direction only
   (proportions, outline style, how a feature is drawn): never copy their
   pixels, and never put a copyrighted character into a build that is shared
   or published.

2. **Find its type in this table.** It says which parts to split (each part
   animates on its own) and what can carry secondary motion, which is what
   makes a mascot feel alive rather than a sticker that bounces.

   | Type | Typical identity features | Parts, back to front | Secondary motion |
   | --- | --- | --- | --- |
   | Humanoid character | hair shape and color, eyes, one accessory, outfit, a held item | `hair-back`, `body`, `head` (face, bangs, front locks), `prop` | head bob/nod, hair follow-through, prop swing |
   | Animal | ears, markings, tail, muzzle, eye color | `tail`, `body`, `ears` (nested in head), `head` | ears flop, tail wag, head tilt |
   | Object (lamp, mug, plant, robot vacuum) | silhouette, one signature detail | `back` (cable, stand), `body`, `face` (a face drawn on it), `moving bits` | steam or leaf wiggle, light blink, wheels step |
   | Creature / blob / robot | silhouette, one odd feature (horn, antenna, visor, glow) | `back`, `body`, `head`, `appendage` | squash and stretch, antenna wobble, glow blink |

   Mascots without a face still need readable states: change the pose, the
   effects and the speed instead of the expression.

3. **Choose the canvas.** 20×20 for a simple shape with few features; 32×32
   for anything with several features or a face that must emote. Crop at the
   chest or seat for characters: the face and the identity features need the
   room more than legs do. Draw at 4 px per cell.

4. **Copy the template**, `<kit>/example_mascot.py` (Miso, a cat with three
   states), to `make_<name>.py` in the mascot's folder, set `NAME`, and
   replace the shapes and states. Keep the builder: the SVG is a build
   output. Keep the template's last step, `apply_overrides(...)`: it applies
   the user's hand edits from the studio (step 10), so rebuilding never
   loses them.

5. **Draw back to front**, one part per thing that moves on its own. Nest an
   appendage inside what it is attached to (ears inside the head), so it
   follows that part's motion and can still move on its own. Kit tools:
   `rect`, `ellipse`, `polygon` (ears, fins, horns), `path` (tails, cables,
   stems), `line`, `zigzag_bottom` (hair or fringe edges), `paint(...,
   only=...)` to draw details onto existing shapes, `shade_edges` for shadows
   and edges. Call `s.outline()` once at the end, so every part carries its
   own outline. For characters with hair, follow "Characters with hair" in
   LESSONS.md.

6. **One face (or pose) per state**, as groups toggled with opacity rules:
   `f-open` by default, plus whatever fits each state. Reactions read best
   when they differ in shape, not just in color: closed `^ ^` eyes,
   half-lidded eyes, an open mouth, a shadow band. Faces drawn on a character
   with bangs skip the hair cells.
   - Fit each state to the character. When a state doesn't suit them, ask,
     and offer moments from their own story: a signature gesture or scene.
     Big silhouette changes read at 128 px; small details (a 2-pixel gem, a
     mouth that opens and shuts) don't.
   - A state may swap whole parts, not just faces: an accessory on or off, a
     hat pulled down for sleep. Make each swappable piece its own part and
     hide or show it with `.<state> .part{opacity:…}`. Scope every such rule
     to a state, so the other states keep their parts.
   - When the user is unsure, build alternatives instead of arguing for one:
     let the builder take a variant name as an argument, build each to its
     own file, and show them side by side. Keep the variant the user liked
     before: a revert should be one argument.

7. **Effects** with `s.fx(name, cls, frames)`: sparkles, speed lines, Z's,
   wobble marks, sweat drops. Frames become `s1`, `s2`… to animate out of
   step.

8. **Motion**: `steps(1)` keyframes and whole-cell moves (pixel art should
   step, not glide). The whole figure sits in a `.rig` group that hops or
   sways; on top of that:
   - the head bobs, tilts or nods on its own (up to 2 cells);
   - appendages (hair, ears, tail, antenna) follow at most a quarter cycle
     late; half a cycle puts them on the opposite side and reads as a trail;
   - props and moving bits run slightly off-beat.
   An idle loop is slow and small: breathing, a blink, a tail.

9. **Build and look at it** before showing anyone (commands as in "Running
   the scripts"):
   ```bash
   PYTHONPATH="<kit>" python3 make_<name>.py <name>.svg
   python3 <kit>/preview.py <name>.svg sheet.png
   ```
   then read `sheet.png`: one still per state, left to right. The preview
   shows resting poses only. To see the motion, start the studio in the
   background and open `http://127.0.0.1:8765/` in a browser (the built-in
   browser pane, if there is one):
   ```bash
   python3 <kit>/studio/server.py --svg <name>.svg --build make_<name>.py
   ```
   It shows each state animating in its own frame. `--states a,b` picks and
   orders the states (default: every state the CSS uses, in the order they
   first appear); `--port` changes the port. Users review from screenshots
   and often mark problems in red: map the marks to cells by lining them up
   with features you know (the eye row, the mouth), then redraw along them.
   After a refactor that should change nothing visible, build the old and the
   new version and compare the files byte for byte (`cmp` or `fc /b`).

10. **Hand edits.** When the user wants to fix pixels themselves, send them
    to the studio's `/editor.html`: paint, erase and pick colors per state,
    undo, then save, which writes `<name>_overrides.json` and rebuilds. Each
    pixel belongs to a part and moves with it; the editor says which part and
    which states show it. A mascot without a builder works too (omit
    `--build`): the studio keeps an untouched copy and the edits in
    `<name>_studio/` beside the SVG and writes the result into the SVG. After
    the user edits, read their overrides file and the rebuilt preview before
    changing anything else, and say if an edit looks accidental (a lone pixel
    far from the rest).

11. **Hand it over**: say where the SVG is, which state it plays by default,
    and how to show another (set the root's class; an `<img>` can't, so an
    app that switches states inlines the SVG or loads it in an `<object>` or
    `<iframe>`).

## profile.json (for an app that shows the mascot)

An app may need more than root classes: CSS variables on the root, extra
classes, fixed state labels. A `profile.json` placed in `<kit>` next to
`preview.py` tells the preview and the studio. Every key is optional:

```json
{
  "states": [{ "class": "happy", "name": "happy", "label": "happy · on success", "style": "--speed:.5s" }],
  "rootClass": "always-animate",
  "swatches": { "var": "--accent", "label": "accent", "colors": ["#8FA8E8", "#ED93B1"] },
  "workdir": "~/my-app/studio"
}
```

`states` fixes the order, the button names, the captions and a root style per
state; `rootClass` is added to the root in every frame; `swatches` adds color
buttons that set a CSS variable; `workdir` replaces `<name>_studio/` for
mascots without a builder. This plugin ships none.

## Files in this skill

| File | What it is |
| --- | --- |
| `LESSONS.md` | What worked and what didn't, with causes and fixes. Read first. |
| `scripts/pixelkit.py` | Shapes (rect, ellipse, polygon, path, line), parts, shading, per-part outlines, SVG output. |
| `scripts/example_mascot.py` | Miso: a 32×32 cat with idle, happy and sleep; the template to copy. |
| `scripts/preview.py` | PNG sheet, one still per state, standard library only. |
| `scripts/pixel_overrides.py` | Applies hand edits to a finished SVG; builders call it last. |
| `scripts/studio/` | `server.py` + `site/`: every state animating, and a pixel editor, for any mascot. Local only (127.0.0.1). |
