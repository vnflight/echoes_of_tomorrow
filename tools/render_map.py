#!/usr/bin/env python3
"""Render Aethon's static site-plan underlay and navigation symbols.

The Ren'Py screen owns labels, state, and interaction. This renderer supplies
only the physical station: insulated modules, enclosed links, and exterior
structure. Room rectangles must stay aligned with the live
buttons in ``screens_game.rpy``.

    python tools/render_map.py
"""

from __future__ import annotations

from pathlib import Path
import math

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
UI = ROOT / "game" / "images" / "ui"
OUT = UI / "map_underlay.png"
MARCUS_SOURCE = (
    ROOT / "game" / "images" / "marcus neutral.png"
)

W, H, S = 650, 430, 2

CYAN = (121, 215, 255)
BLUE = (150, 181, 224)
GREEN = (127, 208, 169)
AMBER = (224, 174, 105)
RUST = (205, 128, 103)

# These are also the live button rectangles in screen observatory_map.  The
# footprint follows the exterior establishing shot: a left domestic annex, a
# long central hull beneath the dome, two right-hand service volumes, and the
# exposed array beyond them.
ROOMS = {
    "habitat": (28, 205, 126, 76, CYAN),
    "storage": (28, 294, 126, 62, CYAN),
    "telescope": (260, 68, 150, 105, BLUE),
    # Legacy geometry retained for standalone icon generation. These are not
    # station destinations and their empty shells are not baked into the map.
    "terminal": (192, 92, 128, 50, CYAN),
    "lab": (180, 180, 150, 108, CYAN),
    "central": (342, 195, 68, 78, CYAN),
    "comms": (480, 180, 120, 82, GREEN),
    "corridor": (386, 232, 124, 58, GREEN),
    "generator": (410, 276, 118, 72, AMBER),
    "gantry": (552, 288, 84, 62, RUST),
}

STATIC_ROOMS = tuple(
    name for name in ROOMS if name not in ("terminal", "corridor")
)

# Enclosed connectors between the modules. Their broad outer shell gives the
# map the same clustered footprint as the exterior backgrounds.
PASSAGES = [
    ([(91, 281), (91, 294)], CYAN),
    # The annex's one short enclosed tunnel, visible in the exterior.
    ([(154, 243), (180, 243)], CYAN),
    # The main circulation spine runs left-to-right through the central hull.
    ([(330, 234), (480, 234)], GREEN),
    # Dome access descends directly into the main building.
    ([(335, 173), (335, 186), (376, 186), (376, 195)], BLUE),
    # Utility stair/tube to the lower service housing.
    ([(410, 252), (454, 252), (454, 276)], AMBER),
]


def p(value: float) -> int:
    return int(round(value * S))


def alpha(colour: tuple[int, int, int], value: int) -> tuple[int, int, int, int]:
    return (*colour, value)


def rounded(draw: ImageDraw.ImageDraw, box, radius, *, fill, outline=None, width=1):
    draw.rounded_rectangle(tuple(p(v) for v in box), p(radius), fill=fill,
                           outline=outline, width=p(width))


def line(draw: ImageDraw.ImageDraw, points, *, fill, width=1, joint="curve"):
    draw.line([(p(x), p(y)) for x, y in points], fill=fill, width=p(width), joint=joint)


def snowfield() -> Image.Image:
    """A dark, windswept site surface rather than a drafting grid."""

    img = Image.new("RGBA", (p(W), p(H)), (3, 10, 16, 236))
    d = ImageDraw.Draw(img, "RGBA")

    # Long contour strokes suggest packed snow and prevailing wind. They are
    # deliberately irregular and low contrast, never a second information UI.
    contours = [
        [(8, 75), (92, 63), (168, 72), (230, 58), (320, 68)],
        [(336, 19), (424, 10), (526, 21), (642, 8)],
        [(4, 242), (86, 230), (164, 238), (229, 225)],
        [(392, 285), (474, 276), (553, 287), (646, 270)],
        [(8, 402), (108, 389), (208, 402), (302, 388), (401, 401)],
    ]
    for offset in (0, 5, 11):
        for points in contours:
            line(d, [(x, y + offset) for x, y in points], fill=(96, 142, 166, 14), width=1)

    # Soft drifts collect around the outside of modules.
    drift = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dd = ImageDraw.Draw(drift, "RGBA")
    for name in STATIC_ROOMS:
        x, y, w, h, colour = ROOMS[name]
        if colour == RUST:
            continue
        dd.rounded_rectangle((p(x - 7), p(y - 6), p(x + w + 8), p(y + h + 9)),
                             p(8), fill=(132, 175, 190, 15))
    drift = drift.filter(ImageFilter.GaussianBlur(p(8)))
    return Image.alpha_composite(img, drift)


def draw_passages(img: Image.Image) -> None:
    d = ImageDraw.Draw(img, "RGBA")
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow, "RGBA")

    for points, colour in PASSAGES:
        line(sd, [(x + 3, y + 4) for x, y in points], fill=(0, 0, 0, 105), width=17)
    shadow = shadow.filter(ImageFilter.GaussianBlur(p(3)))
    img.alpha_composite(shadow)

    for points, colour in PASSAGES:
        line(d, points, fill=(29, 45, 55, 255), width=15)
        line(d, points, fill=alpha(colour, 120), width=2)
        # Structural ribs turn abstract lines into enclosed transfer tubes.
        for (x1, y1), (x2, y2) in zip(points, points[1:]):
            if y1 == y2:
                for x in range(int(min(x1, x2)) + 10, int(max(x1, x2)), 18):
                    line(d, [(x, y1 - 7), (x, y1 + 7)], fill=(118, 145, 156, 70), width=1)
            else:
                for y in range(int(min(y1, y2)) + 10, int(max(y1, y2)), 18):
                    line(d, [(x1 - 7, y), (x1 + 7, y)], fill=(118, 145, 156, 70), width=1)


def draw_main_hull(img: Image.Image) -> None:
    """Unify the central rooms into the long hull seen outside."""

    d = ImageDraw.Draw(img, "RGBA")
    rounded(d, (170, 166, 485, 298), 11, fill=(17, 31, 40, 245),
            outline=alpha(CYAN, 85), width=2)
    # A continuous lower sill is the clearest silhouette cue at map scale.
    line(d, [(181, 291), (475, 291)], fill=alpha(CYAN, 55), width=2)


def dome_outline(x, y, w, h):
    """Semicircular roof over straight walls; shared by paint and hit mask."""
    radius = w / 2
    roof = [(x + radius + radius * math.cos(math.radians(angle)),
             y + radius + radius * math.sin(math.radians(angle)))
            for angle in range(180, 361, 2)]
    return roof + [(x + w, y + h), (x, y + h)]


def draw_module(img: Image.Image, name: str) -> None:
    x, y, w, h, colour = ROOMS[name]
    d = ImageDraw.Draw(img, "RGBA")

    if name == "gantry":
        rounded(d, (x, y, x + w, y + h), 3, fill=(30, 25, 25, 170),
                outline=alpha(RUST, 150), width=2)
        for offset in range(-int(h), int(w), 12):
            x1, y1 = max(x, x + offset), y + max(0, -offset)
            x2, y2 = min(x + w, x + offset + h), y + h - max(0, offset + h - w)
            if x2 > x1:
                line(d, [(x1, y1), (x2, y2)], fill=alpha(RUST, 45), width=1)
        return

    # A semicircular roof sits on a short rectangular drum.
    if name == "telescope":
        shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow, "RGBA")
        sd.polygon([(p(a), p(b)) for a, b in dome_outline(x + 4, y + 6, w, h)],
                   fill=(0, 0, 0, 145))
        shadow = shadow.filter(ImageFilter.GaussianBlur(p(4)))
        img.alpha_composite(shadow)

        outer = [(p(a), p(b)) for a, b in dome_outline(x, y, w, h)]
        inner = [(p(a), p(b)) for a, b in dome_outline(x + 7, y + 7, w - 14, h - 14)]
        d.polygon(outer, fill=(25, 41, 51, 248))
        d.line(outer + outer[:1], fill=alpha(colour, 195), width=p(2))
        d.polygon(inner, fill=(11, 25, 34, 220))
        d.line(inner + inner[:1], fill=(113, 145, 158, 60), width=p(1))
        line(d, [(x + 7, y + w / 2), (x + w - 7, y + w / 2)],
             fill=alpha(colour, 65), width=1)
        line(d, [(x + w / 2, y + 9), (x + w / 2, y + h)],
             fill=alpha(colour, 52), width=1)
        line(d, [(x + 8, y + h - 1), (x + w - 8, y + h - 1)],
             fill=alpha(colour, 90), width=2)
        return

    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow, "RGBA")
    sd.rounded_rectangle((p(x + 4), p(y + 6), p(x + w + 4), p(y + h + 6)),
                         p(7), fill=(0, 0, 0, 145))
    shadow = shadow.filter(ImageFilter.GaussianBlur(p(4)))
    img.alpha_composite(shadow)

    # Thick insulated shell, recessed roof, and a worn safety stripe.
    rounded(d, (x, y, x + w, y + h), 7, fill=(25, 41, 51, 248),
            outline=alpha(colour, 175), width=2)
    rounded(d, (x + 6, y + 6, x + w - 6, y + h - 6), 4,
            fill=(11, 25, 34, 220), outline=(113, 145, 158, 55), width=1)
    line(d, [(x + 8, y + h - 9), (x + w - 8, y + h - 9)], fill=alpha(colour, 75), width=2)

    # Roof-panel seams and attachment bolts establish physical scale.
    for sx in range(x + 26, x + w - 8, 28):
        line(d, [(sx, y + 7), (sx, y + h - 11)], fill=(130, 163, 176, 28), width=1)
    for cx, cy in ((x + 8, y + 8), (x + w - 8, y + 8),
                   (x + 8, y + h - 8), (x + w - 8, y + h - 8)):
        d.ellipse((p(cx - 1.5), p(cy - 1.5), p(cx + 1.5), p(cy + 1.5)), fill=(184, 202, 207, 90))

def draw_external_links(img: Image.Image) -> None:
    d = ImageDraw.Draw(img, "RGBA")
    # Open-air service bridge from the right-hand Comms room to the remote
    # array platform. Two rails make its exposed status unmistakable.
    line(d, [(545, 260), (574, 291)], fill=(24, 28, 30, 220), width=12)
    line(d, [(542, 262), (571, 293)], fill=alpha(RUST, 115), width=1)
    line(d, [(548, 257), (577, 288)], fill=alpha(RUST, 90), width=1)

    # A compact plan-view dish on the gantry echoes the exterior landmark.
    d.arc((p(567), p(296), p(622), p(334)), 198, 342,
          fill=alpha(RUST, 175), width=p(3))
    line(d, [(595, 316), (595, 340)], fill=alpha(RUST, 155), width=2)
    line(d, [(584, 340), (606, 340)], fill=alpha(RUST, 120), width=2)


def render_map() -> None:
    img = snowfield()
    draw_main_hull(img)
    draw_passages(img)
    for name in STATIC_ROOMS:
        draw_module(img, name)
    draw_external_links(img)

    # Keep the outer edge subdued beneath the modal frame.
    vignette = Image.new("L", img.size, 0)
    vd = ImageDraw.Draw(vignette)
    vd.rounded_rectangle((p(18), p(14), p(W - 18), p(H - 14)), p(22), fill=210)
    vignette = vignette.filter(ImageFilter.GaussianBlur(p(24)))
    shade = Image.new("RGBA", img.size, (0, 0, 0, 0))
    shade.putalpha(vignette.point(lambda value: 100 - int(value * 100 / 210)))
    img = Image.alpha_composite(img, shade)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT)
    print(f"wrote {OUT} {img.size}")
    _, _, w, h, _ = ROOMS["telescope"]
    mask = Image.new("RGBA", (p(w), p(h)), (0, 0, 0, 0))
    ImageDraw.Draw(mask).polygon(
        [(p(a), p(b)) for a, b in dome_outline(0, 0, w - 1, h - 1)],
        fill=(255, 255, 255, 255))
    mask.save(UI / "map_dome_mask.png")


def icon_canvas() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img, "RGBA")


def icon_line(d: ImageDraw.ImageDraw, points, colour, width=6):
    d.line(points, fill=(*colour, 235), width=width, joint="curve")


def render_icon(kind: str, colour: tuple[int, int, int]) -> Image.Image:
    """Flat navigation symbol: no badge, bloom, text, or decorative compass."""

    img, d = icon_canvas()
    if kind == "telescope":
        d.arc((24, 24, 104, 94), 200, 340, fill=(*colour, 235), width=7)
        icon_line(d, [(34, 79), (91, 49)], colour, 8)
        icon_line(d, [(64, 67), (64, 101)], colour)
        icon_line(d, [(45, 104), (83, 104)], colour)
    elif kind == "lab":
        d.rounded_rectangle((35, 18, 93, 87), 5, outline=(*colour, 235), width=6)
        for y in (36, 54, 72):
            icon_line(d, [(47, y), (81, y)], colour, 4)
        icon_line(d, [(27, 101), (101, 101)], colour)
        icon_line(d, [(36, 87), (31, 109)], colour, 5)
        icon_line(d, [(92, 87), (97, 109)], colour, 5)
    elif kind == "comms":
        for radius in (24, 41):
            d.arc((64 - radius, 64 - radius, 64 + radius, 64 + radius), 205, 335,
                  fill=(*colour, 225), width=5)
        d.ellipse((57, 57, 71, 71), fill=(*colour, 235))
        icon_line(d, [(64, 69), (64, 103)], colour)
        icon_line(d, [(46, 106), (82, 106)], colour)
    elif kind == "generator":
        d.rounded_rectangle((25, 25, 103, 103), 8, outline=(*colour, 235), width=6)
        icon_line(d, [(68, 37), (47, 67), (64, 67), (53, 92), (82, 57), (63, 57), (68, 37)], colour, 6)
    elif kind == "habitat":
        # Table and two chairs: the station's domestic, shared room.
        d.ellipse((35, 35, 93, 93), outline=(*colour, 235), width=6)
        icon_line(d, [(22, 50), (34, 50)], colour, 5)
        icon_line(d, [(22, 78), (34, 78)], colour, 5)
        icon_line(d, [(94, 50), (106, 50)], colour, 5)
        icon_line(d, [(94, 78), (106, 78)], colour, 5)
    elif kind == "terminal":
        # A door with light under it: the phase-3 texture, as a symbol.
        d.rounded_rectangle((36, 16, 92, 96), 4, outline=(*colour, 235), width=6)
        d.ellipse((76, 56, 84, 64), fill=(*colour, 235))
        for x1, x2 in ((22, 106), (32, 96), (44, 84)):
            icon_line(d, [(x1, 106), (x2, 106)], colour, 4)
    elif kind == "corridor":
        # An enclosed run with a cable tray along it: the bay off the link.
        icon_line(d, [(20, 34), (108, 34)], colour, 6)
        icon_line(d, [(20, 94), (108, 94)], colour, 6)
        for x in range(30, 105, 18):
            icon_line(d, [(x, 34), (x, 46)], colour, 3)
            icon_line(d, [(x, 82), (x, 94)], colour, 3)
        icon_line(d, [(24, 64), (104, 64)], colour, 5)
    elif kind == "storage":
        # Three modular requisition bins, matching the room's shelving.
        for x, y in ((24, 35), (68, 35), (24, 72), (68, 72)):
            d.rounded_rectangle((x, y, x + 36, y + 25), 3,
                                outline=(*colour, 235), width=5)
            icon_line(d, [(x + 11, y + 9), (x + 25, y + 9)], colour, 3)
    return img


def render_marcus_marker() -> None:
    """Crop the canonical sprite into a compact map-presence portrait."""

    source = Image.open(MARCUS_SOURCE).convert("RGBA")
    # Centre the v2 face tightly, with just enough collar to remain legible at
    # 42 px. The source figure sits left of the full canvas centre.
    portrait = source.crop((215, 50, 715, 550))
    portrait = portrait.resize((112, 112), Image.Resampling.LANCZOS)

    mask = Image.new("L", portrait.size, 0)
    ImageDraw.Draw(mask).ellipse((4, 4, 108, 108), fill=255)
    mask = Image.composite(mask, Image.new("L", mask.size, 0),
                           portrait.getchannel("A"))
    portrait.putalpha(mask)

    marker = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    md = ImageDraw.Draw(marker, "RGBA")
    md.ellipse((4, 4, 124, 124), fill=(7, 16, 22, 245),
               outline=(*AMBER, 245), width=6)
    marker.alpha_composite(portrait, (8, 8))
    md.ellipse((4, 4, 124, 124), outline=(*AMBER, 245), width=6)
    path = UI / "icon_marcus.png"
    marker.save(path)
    print(f"wrote {path} (128, 128)")


def render_icons() -> None:
    for kind, colour in {
        "telescope": BLUE,
        "lab": CYAN,
        "comms": GREEN,
        "generator": AMBER,
        "habitat": CYAN,
        "storage": CYAN,
        "terminal": CYAN,
        "corridor": GREEN,
    }.items():
        path = UI / f"icon_{kind}.png"
        render_icon(kind, colour).save(path)
        print(f"wrote {path} (128, 128)")
    render_marcus_marker()


def main() -> None:
    render_map()
    render_icons()


if __name__ == "__main__":
    main()
