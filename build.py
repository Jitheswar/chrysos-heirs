#!/usr/bin/env python3
"""
Chrysos Heirs — an Omarchy theme.

Builds ONE theme (~/.config/omarchy/themes/chrysos-heirs) holding all fourteen
wallpapers and fourteen palettes (heirs/<heir>/). The theme's colors.toml is a
copy of whichever heir's wallpaper is on screen; bin/chrysos-heirs-sync swaps it
when the wallpaper changes. Every heir's active window border is a gradient
from their own colour into the colour of the one they are bound to.

Only colour files, icons, a preview and wallpapers are written; Omarchy renders
every app config from colors.toml, so your own config is never touched.

Usage:  python3 build.py [--out DIR] [--no-preview]
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WALLS = HERE / "wallpapers"
SERIF = "C059-Roman"
SERIF_ITALIC = "C059-Italic"

# ---------------------------------------------------------------------------
# Palettes. Every hex below was picked from a k-means sample of the matching
# wallpaper, then nudged only as far as needed for terminal contrast.
# ---------------------------------------------------------------------------

HEIRS = [
    dict(
        slug="phainon", name="Phainon", wall="phainon.jpg",
        epithet="The Deliverer", flame="Kephale · Worldbearing",
        bond="cyrene",
        bond_text="Cyrene walked beside him through every return of the cycle; "
                  "the border runs from his moonlit azure into her rose.",
        also="Mydei — brother-in-arms (his red is Mydei's crimson banner). "
             "Khaslana — the name he carries when the cycle remembers.",
        icons="Yaru-blue",
        border=["eae4f0", "6199e4", "ddacd2"],
        c=dict(
            background="#0e1530", dark_background="#0b1126", darker_background="#070b1a",
            lighter_background="#1a2448", selection="#283a80", muted="#4a5590",
            foreground="#eae4f0", dark_foreground="#7580be", light_foreground="#bab1c8",
            bright_foreground="#fbf8ff", accent="#7aaef0",
            red="#e8706e", orange="#f0a050", yellow="#f0c878", green="#8fd0b0",
            cyan="#9ad4f0", blue="#6f9fe8", magenta="#c696d6", brown="#a26c96",
        ),
    ),
    dict(
        slug="khaslana", name="Khaslana", wall="kaslana.jpg",
        epithet="The Name Beneath the Cycles", flame="Kephale · Worldbearing",
        bond="phainon",
        bond_text="Khaslana is Phainon, worn down by countless returns; the border "
                  "bleeds his molten gold through the night into the azure he once was.",
        also="Cyrene — the one who remembered him by both names.",
        icons="Yaru-yellow",
        border=["e2b84a", "24294d", "6199e4"],
        c=dict(
            background="#0d0b0a", dark_background="#0a0807", darker_background="#060504",
            lighter_background="#1c1916", selection="#2a2e4f", muted="#5a4f4d",
            foreground="#e6e2df", dark_foreground="#857668", light_foreground="#ccb7a1",
            bright_foreground="#f7f4f1", accent="#e2b84a",
            red="#d0624a", orange="#d08a48", yellow="#e2c070", green="#a8b47a",
            cyan="#8ab4c4", blue="#7a84c4", magenta="#b48ab8", brown="#985b30",
        ),
    ),
    dict(
        slug="cyrene", name="Cyrene", wall="cyrene.jpg",
        epithet="She Who Remembers Every Cycle", flame="Amphoreus' memory",
        bond="phainon",
        bond_text="The golden figures circling her are everyone she carried through "
                  "the loops; the border runs from her rose-light into Phainon's azure.",
        also="Every heir — the gold in this palette is the gold of their silhouettes.",
        icons="Yaru-magenta",
        border=["f2e5e9", "ddacd2", "6199e4"],
        c=dict(
            background="#170a1f", dark_background="#12071a", darker_background="#0c0412",
            lighter_background="#26143a", selection="#43285a", muted="#6a4e70",
            foreground="#f4e6ee", dark_foreground="#a87aa9", light_foreground="#ddacd2",
            bright_foreground="#fff4f8", accent="#e39ad8",
            red="#f07a9c", orange="#f0a888", yellow="#f2d48a", green="#a8d8b0",
            cyan="#9fd8f0", blue="#9a9cf0", magenta="#d97fd9", brown="#956474",
        ),
    ),
    dict(
        slug="aglaea", name="Aglaea", wall="aglaea.png",
        epithet="The Goldweaver", flame="Mnestia · Romance",
        bond="cipher",
        bond_text="Aglaea's golden threads reach every corner of Okhema — and Cipher "
                  "is the thread she sends into the dark; gold runs into Cipher's blue.",
        also="Tribbie — the two pillars who hold Okhema together.",
        icons="Yaru-yellow",
        border=["f0d6a5", "d4a069", "6297c1"],
        c=dict(
            background="#1a1315", dark_background="#140e10", darker_background="#0e0a0b",
            lighter_background="#2a1f21", selection="#4a3530", muted="#6d5654",
            foreground="#f0e6d2", dark_foreground="#9a8478", light_foreground="#d4c3a8",
            bright_foreground="#fbf5e8", accent="#e2b46e",
            red="#d97a5e", orange="#d4a069", yellow="#f0d6a5", green="#b4b87a",
            cyan="#9cc4b8", blue="#a6a8d4", magenta="#cf9bb6", brown="#976e57",
        ),
    ),
    dict(
        slug="tribbie", name="Tribbie", wall="tribbie.png",
        epithet="The Three-in-One", flame="Janus · Passages",
        bond="tribbie",
        bond_text="Trinnon, Tribios and Trianne — one oracle in three bodies. The border "
                  "is three colours that are really one: sunset hair, cream robes, lilac.",
        also="Aglaea — together they keep the gates of Okhema.",
        icons="Yaru",
        border=["e8784a", "f2dfbf", "9474c2"],
        c=dict(
            background="#1a1216", dark_background="#140e11", darker_background="#0d090b",
            lighter_background="#2a1d24", selection="#4a2c34", muted="#6c4e63",
            foreground="#f2e2cc", dark_foreground="#a283a0", light_foreground="#d3a79f",
            bright_foreground="#fbf3e6", accent="#e8784a",
            red="#e06048", orange="#df9c60", yellow="#f0c070", green="#a8c48a",
            cyan="#9cc8e0", blue="#8a9ee0", magenta="#b48ad8", brown="#a54625",
        ),
    ),
    dict(
        slug="mydei", name="Mydei", wall="Mydei.jpg",
        epithet="Prince of Kremnos", flame="Nikador · Strife",
        bond="castorice",
        bond_text="Death cannot take Mydei, so Castorice's fatal touch is safe in his "
                  "hands; the border runs from his war banner's crimson into her violet.",
        also="Phainon — rival, friend, brother-in-arms.",
        icons="Yaru-red",
        border=["eac17c", "d65040", "9c60c3"],
        c=dict(
            background="#1a120f", dark_background="#140d0b", darker_background="#0d0807",
            lighter_background="#2a1d18", selection="#4a2e25", muted="#6a584b",
            foreground="#eee0cc", dark_foreground="#a3806a", light_foreground="#cfb193",
            bright_foreground="#faf0e0", accent="#e2604c",
            red="#de5a48", orange="#cf9e75", yellow="#eac17c", green="#a8b47a",
            cyan="#9cc0b8", blue="#8aa0c0", magenta="#c08aa6", brown="#9b533c",
        ),
    ),
    dict(
        slug="castorice", name="Castorice", wall="castorice.png",
        epithet="The Mourning Maiden", flame="Thanatos · Death",
        bond="mydei",
        bond_text="Everything she touches withers — except Mydei, who cannot die. "
                  "The border runs from her violet butterflies into his crimson.",
        also="Hyacine — the healer who keeps her company (her green is the life she protects).",
        icons="Yaru-purple",
        border=["d1a8e8", "9c60c3", "c4503c"],
        c=dict(
            background="#0f0b1d", dark_background="#0b0816", darker_background="#07050f",
            lighter_background="#1d1633", selection="#3a2a5c", muted="#5a5080",
            foreground="#ece0f7", dark_foreground="#8a7aa9", light_foreground="#d1b8e8",
            bright_foreground="#f8f0ff", accent="#b98ae0",
            red="#e07a9a", orange="#e0a37a", yellow="#e8d29a", green="#9fd1b4",
            cyan="#9ec8e8", blue="#8a8ff0", magenta="#c77ddb", brown="#7a5a66",
        ),
    ),
    dict(
        slug="anaxa", name="Anaxa", wall="anaxa.jpg",
        epithet="The Unbelieving Scholar", flame="Cerces · Reason",
        bond="hyacine",
        bond_text="Both came out of the Grove of Epiphany — reason and remedy. "
                  "The border runs from his eclipse-teal into Hyacine's dawn pink.",
        also="The red of this palette is the red mark on his hand and the cards he deals.",
        icons="Yaru-prussiangreen",
        border=["64cdd2", "c2cebb", "e87392"],
        c=dict(
            background="#141b20", dark_background="#10161a", darker_background="#0b0f12",
            lighter_background="#1f2a31", selection="#2c3e48", muted="#4f606a",
            foreground="#e6ebe3", dark_foreground="#78909a", light_foreground="#c2cebb",
            bright_foreground="#f6f8f1", accent="#64cdd2",
            red="#e06a5a", orange="#d88c5a", yellow="#d8bd80", green="#9cc4a2",
            cyan="#64cdd2", blue="#7aa2c8", magenta="#b49ac9", brown="#947359",
        ),
    ),
    dict(
        slug="hyacine", name="Hyacine", wall="hyacine.png",
        epithet="Daughter of the Sky", flame="Aquila · Sky",
        bond="castorice",
        bond_text="The healer and the girl whose touch is death — friends anyway. "
                  "A dawn-sky light theme; the border runs pink → sky → Castorice's violet.",
        also="Anaxa — the Grove of Epiphany. Ica — the little winged companion.",
        icons="Yaru-magenta",
        border=["e87392", "6d99ad", "9c60c3"],
        c=dict(
            mode="light",
            background="#fbf0f3", dark_background="#f4e2e8", darker_background="#ecd2db",
            lighter_background="#fff8fa", selection="#f1b5c9", muted="#b88a9a",
            foreground="#4a1a26", dark_foreground="#9c6a7c", light_foreground="#6e3a48",
            bright_foreground="#2e0d16", accent="#c42f51",
            red="#c42f51", orange="#a8481c", yellow="#86590a", green="#2f7a4c",
            cyan="#14727f", blue="#3a72a8", magenta="#a8408a", brown="#9c5d69",
            bright_red="#a8203f", bright_yellow="#6f4a06", bright_green="#246340",
            bright_cyan="#0f5f6a", bright_blue="#2d6094", bright_magenta="#923478",
        ),
    ),
    dict(
        slug="cipher", name="Cipher", wall="cipher.png",
        epithet="The Thief of Dawncloud", flame="Zagreus · Trickery",
        bond="aglaea",
        bond_text="A cat-quick thief who works Aglaea's threads; the border runs "
                  "from her cloak's night-blue into Aglaea's gold.",
        also="The ruby she's holding up is the accent. Of course she stole it.",
        icons="Yaru-red",
        border=["6297c1", "e2b45c", "f0d6a5"],
        c=dict(
            background="#0b0c18", dark_background="#080912", darker_background="#05050c",
            lighter_background="#171a2e", selection="#26305a", muted="#4a4c66",
            foreground="#f0ebe8", dark_foreground="#7a80a8", light_foreground="#cfbab7",
            bright_foreground="#ffffff", accent="#ec5560",
            red="#ec5560", orange="#e08a5a", yellow="#e2b45c", green="#7ad48a",
            cyan="#7fc0e8", blue="#6a9fd0", magenta="#b08ad8", brown="#a98a7a",
        ),
    ),
    dict(
        slug="cerydra", name="Cerydra", wall="cerydra.jpg",
        epithet="She Who Moves the Pieces", flame="Talanton · Law",
        bond="hysilens",
        bond_text="Hysilens was her friend — and, in some cycles, the hand that ended her. "
                  "The border runs across the chessboard into a single coral-red line.",
        also="The pale pink is the dawn at the bottom of her board.",
        icons="Yaru-blue",
        border=["b4b2cb", "6f8aae", "d0566e"],
        c=dict(
            background="#121722", dark_background="#0e121b", darker_background="#0a0d14",
            lighter_background="#1e2536", selection="#2f3a55", muted="#525a72",
            foreground="#e6e0ea", dark_foreground="#7f88a6", light_foreground="#b4b2cb",
            bright_foreground="#f5f0f7", accent="#8fa8d8",
            red="#e48aa0", orange="#e0a080", yellow="#e2c99a", green="#9bc4b0",
            cyan="#9ad0e0", blue="#7f9cd0", magenta="#b49ad8", brown="#8a788e",
        ),
    ),
    dict(
        slug="hysilens", name="Hysilens", wall="hysilens.jpg",
        epithet="Song of the Sea", flame="Phagousa · Sea",
        bond="cerydra",
        bond_text="Her song kept Cerydra's secrets and, in some cycles, ended her. "
                  "The border runs from deep water through coral into Cerydra's silver.",
        also="Pearls and sand dollars are the yellow of this palette.",
        icons="Yaru-blue",
        border=["579fc8", "e0607a", "b4b2cb"],
        c=dict(
            background="#0c1426", dark_background="#09101f", darker_background="#060a15",
            lighter_background="#16233d", selection="#263f66", muted="#435480",
            foreground="#e2dcee", dark_foreground="#7276a8", light_foreground="#a3a6d0",
            bright_foreground="#f4f0fb", accent="#67b6e0",
            red="#e0607a", orange="#e88a6a", yellow="#e8d0a0", green="#7fd0c0",
            cyan="#7fd8f0", blue="#6aa0e8", magenta="#b08ad0", brown="#9d4a68",
        ),
    ),
    dict(
        slug="evernight", name="Evernight", wall="evernight.jpg",
        epithet="Beneath the Crimson Umbrella", flame="Oronyx · Time",
        bond="dan-heng",
        bond_text="March 7th's reflection in Amphoreus, and Dan Heng her oldest companion; "
                  "the border runs from her umbrella's crimson, through pink, into his jade.",
        also="The red moon in Dan Heng's sky is the same red as her umbrella.",
        icons="Yaru-red",
        border=["ee2226", "e8a2e3", "5fa8a0"],
        c=dict(
            background="#160c13", dark_background="#11090f", darker_background="#0b050a",
            lighter_background="#2a1724", selection="#4a2236", muted="#644868",
            foreground="#f2e2f4", dark_foreground="#ab78a6", light_foreground="#e8a2e3",
            bright_foreground="#fff2fc", accent="#f0454a",
            red="#f0454a", orange="#f08060", yellow="#f0c48a", green="#a6d4b0",
            cyan="#9fd0f0", blue="#8ea0e0", magenta="#e070c8", brown="#8a4a50",
        ),
    ),
    dict(
        slug="dan-heng", name="Dan Heng", wall="dangheng.jpg",
        epithet="Permansor Terrae", flame="Georios · Earth",
        bond="evernight",
        bond_text="Jade mountains, a sea of gold, and one red moon. The border runs "
                  "from his gold through dragon-teal into Evernight's crimson.",
        also="The Astral Express — the companions who came to Amphoreus with him.",
        icons="Yaru-olive",
        border=["e4d799", "5fa8a0", "d8323a"],
        c=dict(
            background="#0f1718", dark_background="#0b1213", darker_background="#070c0d",
            lighter_background="#1b2829", selection="#2e4544", muted="#55665a",
            foreground="#ece4c4", dark_foreground="#7a937f", light_foreground="#c4c8a7",
            bright_foreground="#f8f2d8", accent="#d8c169",
            red="#d65a4a", orange="#e0a050", yellow="#e4d799", green="#8fbf8a",
            cyan="#6fc0b4", blue="#7aa0c8", magenta="#a898d0", brown="#a29b63",
        ),
    ),
]

UMBRELLA = dict(
    slug="", name="Chrysos Heirs", wall=None,
    epithet="The Flame-Chase of Amphoreus", flame="Fourteen heirs · one golden thread",
    bond=None,
    bond_text="One theme, fourteen heirs. Change the wallpaper and the whole desktop — "
              "terminal, borders, bar, lock screen — takes on that heir's palette.",
    also="Each heir's window border is a gradient into the colour of the one they are bound to.",
    icons="Yaru-yellow",
    border=["f0d6a5", "d4a069", "9a5937"],
    c=dict(
        background="#100e14", dark_background="#0c0a10", darker_background="#07060a",
        lighter_background="#1d1a22", selection="#3a3040", muted="#5c5260",
        foreground="#ede3cc", dark_foreground="#8f8576", light_foreground="#d4c3a8",
        bright_foreground="#faf4e4", accent="#e0b45a",
        red="#d9705a", orange="#e0965a", yellow="#e8c37a", green="#a3b86c",
        cyan="#7cc4bf", blue="#7fa4d8", magenta="#c792c9", brown="#976e57",
    ),
)

# ---------------------------------------------------------------------------

BY_SLUG = {h["slug"]: h for h in HEIRS}


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def luminance(h):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(v) for v in hex_rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def lighten(h, amt):
    r, g, b = hex_rgb(h)
    return "#%02x%02x%02x" % tuple(round(v + (255 - v) * amt) for v in (r, g, b))


def theme_dir_name(t):
    return "chrysos-heirs" + (f"-{t['slug']}" if t["slug"] else "")


def colors_toml(t):
    c = dict(t["c"])
    mode = c.pop("mode", "dark")
    for k in ("red", "orange", "yellow", "green", "cyan", "blue", "magenta"):
        c.setdefault(f"bright_{k}", lighten(c[k], 0.18))
    border = " ".join(f"rgba({x}ee)" for x in t["border"]) + " 45deg"
    inactive = f"rgba({c['muted'].lstrip('#')}aa)"
    bond = BY_SLUG.get(t["bond"]) if t["bond"] else None

    lines = [
        f"# Chrysos Heirs — {t['name']}" + (f", {t['epithet']}" if t["slug"] else ""),
        f"# {t['flame']}",
    ]
    if bond and bond is not t:
        lines.append(f"# Bond: {bond['name']}. The active border is the thread between them.")
    lines += [
        "",
        f'mode = "{mode}"',
        "",
        f'accent = "{c["accent"]}"',
        f'selection = "{c["selection"]}"',
        f'muted = "{c["muted"]}"',
        "",
    ]
    for k in ("background", "dark_background", "darker_background", "lighter_background"):
        lines.append(f'{k} = "{c[k]}"')
    lines.append("")
    for k in ("foreground", "dark_foreground", "light_foreground", "bright_foreground"):
        lines.append(f'{k} = "{c[k]}"')
    lines += [
        "",
        f'hyprland_active_border = "{border}"',
        f'hyprland_inactive_border = "{inactive}"',
        "",
    ]
    for k in ("red", "yellow", "orange", "green", "cyan", "blue", "magenta", "brown"):
        lines.append(f'{k} = "{c[k]}"')
    lines.append("")
    for k in ("red", "yellow", "green", "cyan", "blue", "magenta"):
        lines.append(f'bright_{k} = "{c["bright_" + k]}"')
    return "\n".join(lines) + "\n", c


def check_contrast(t, c):
    bg = c["background"]
    warn = []
    if contrast(c["foreground"], bg) < 7:
        warn.append(f"foreground {contrast(c['foreground'], bg):.1f}")
    for k in ("red", "orange", "yellow", "green", "cyan", "blue", "magenta", "accent"):
        r = contrast(c[k], bg)
        if r < 4.5:
            warn.append(f"{k} {r:.1f}")
    if warn:
        print(f"  ! low contrast in {theme_dir_name(t)}: {', '.join(warn)}", file=sys.stderr)


def readme(t):
    bond = BY_SLUG.get(t["bond"]) if t["bond"] else None
    out = [f"# Chrysos Heirs — {t['name']}", "", f"*{t['epithet']}* · {t['flame']}", ""]
    if bond and bond is not t:
        out += [f"**Bond:** {bond['name']}", ""]
    out += [t["bond_text"], "", t["also"], "",
            "Part of the Chrysos Heirs collection for Omarchy. "
            "Ships only colors.toml, icons.theme, a preview and wallpaper(s); "
            "everything else is rendered by Omarchy from colors.toml.", ""]
    return "\n".join(out)


def lock_json(t, c):
    """Read by the theme-gated lock overlay (see lock/ChrysosOverlay.qml)."""
    bond = BY_SLUG.get(t["bond"]) if t["bond"] else None
    if bond and bond is not t:
        bond_line = f"bound to {bond['name']}"
    elif t["slug"] == "tribbie":
        bond_line = "three selves, one oracle"
    else:
        bond_line = "every heir · one golden thread"
    return json.dumps(dict(
        name=t["name"], epithet=t["epithet"], flame=t["flame"], bond=bond_line,
        mode=t["c"].get("mode", "dark"), background=c["background"],
        foreground=c["bright_foreground"], subtle=c["light_foreground"],
        accent=c["accent"], thread=[f"#{x}" for x in t["border"]],
    ), indent=2) + "\n"


def write_lock_files(t, c, d):
    (d / "chrysos-lock.json").write_text(lock_json(t, c))
    shutil.copy2(HERE / "assets" / "hsr-logo.png", d / "chrysos-lock-logo.png")


def link_or_copy(src, dst):
    if dst.exists():
        dst.unlink()
    try:
        os.link(src, dst)
    except OSError:
        shutil.copy2(src, dst)


def render_preview(t, c, wall, out):
    """2560x1440 card: wallpaper, a veil in the theme's background, name in
    serif, the bond line, the palette as a row of flames and the border thread."""
    W, H = 2560, 1440
    bg = c["background"]
    fg = c["bright_foreground"]
    sub = c["light_foreground"]
    acc = c["accent"]
    grad = [f"#{x}" for x in t["border"]]

    swatches = [c[k] for k in ("red", "orange", "yellow", "green", "cyan", "blue", "magenta", "accent")]
    sw_cmds = []
    x0, y0, size, gap = 160, 1222, 70, 24
    for i, col in enumerate(swatches):
        x = x0 + i * (size + gap)
        sw_cmds += ["-fill", col, "-stroke", c["muted"], "-strokewidth", "2",
                    "-draw", f"roundrectangle {x},{y0} {x + size},{y0 + size} 18,18"]

    bond = BY_SLUG.get(t["bond"]) if t["bond"] else None
    bond_line = (f"bound to {bond['name']}" if bond and bond is not t
                 else ("three selves, one oracle" if t["slug"] == "tribbie"
                       else "every heir · one golden thread"))

    grad_img = out.parent / ".grad.png"
    stops = []
    for i in range(len(grad) - 1):
        stops.append(f"( -size {2240 // (len(grad) - 1)}x6 gradient:{grad[i]}-{grad[i + 1]} )")
    subprocess.run(["magick", *" ".join(stops).split(), "+append",
                    "-resize", "2240x6!", str(grad_img)], check=True)

    cmd = [
        "magick", str(wall), "-resize", f"{W}x{H}^", "-gravity", "center", "-extent", f"{W}x{H}",
        # veil rising from the bottom in the theme background (alpha ramp)
        "(", "-size", f"{W}x820", f"xc:{bg}",
        "(", "-size", f"{W}x820", "gradient:black-white", "-evaluate", "pow", "0.55",
        "-evaluate", "multiply", "0.95", ")",
        "-alpha", "off", "-compose", "copyopacity", "-composite", ")",
        "-compose", "over", "-gravity", "south", "-composite",
        "-gravity", "northwest",
        str(grad_img), "-geometry", "+160+1176", "-composite",
        # -annotate offsets are the text's top-left under northwest gravity
        "-font", SERIF, "-fill", fg, "-pointsize", "150", "-annotate", "+150+905",
        t["name"],
        "-font", SERIF_ITALIC, "-fill", acc, "-pointsize", "50", "-annotate", "+162+1092",
        f"{t['epithet']}  ·  {bond_line}",
        "-font", SERIF, "-fill", sub, "-pointsize", "38",
        "-gravity", "northeast", "-annotate", "+160+1238", t["flame"].upper(),
        "-gravity", "northwest",
        *sw_cmds,
        "-strip", str(out),
    ]
    subprocess.run(cmd, check=True)
    grad_img.unlink(missing_ok=True)


def render_umbrella_preview(t, c, walls, out):
    """Mosaic of every heir under the umbrella title."""
    tmp = out.parent / ".tiles"
    tmp.mkdir(exist_ok=True)
    tiles = []
    for i, w in enumerate(walls):
        p = tmp / f"{i:02d}.png"
        subprocess.run(["magick", str(w), "-resize", "366x720^", "-gravity", "center",
                        "-extent", "366x720", str(p)], check=True)
        tiles.append(str(p))
    rows = [tiles[:7], tiles[7:]]
    row_imgs = []
    for i, r in enumerate(rows):
        p = tmp / f"row{i}.png"
        subprocess.run(["magick", *r, "+append", "-resize", "2560x720!", str(p)], check=True)
        row_imgs.append(str(p))
    mosaic = tmp / "mosaic.png"
    subprocess.run(["magick", *row_imgs, "-append", str(mosaic)], check=True)
    render_preview(t, c, mosaic, out)
    shutil.rmtree(tmp)


THEME = "chrysos-heirs"
ACTIVE_FILES = ("colors.toml", "chrysos-lock.json", "icons.theme")


def build(out_root, previews=True, first="phainon"):
    """One theme. Every heir's palette lives in heirs/<slug>/; the theme's own
    colors.toml / chrysos-lock.json / icons.theme are a copy of whichever heir's
    wallpaper is on screen. bin/chrysos-heirs-sync keeps them in step."""
    d = out_root / THEME
    d.mkdir(parents=True, exist_ok=True)
    for old in ("backgrounds", "heirs"):
        if (d / old).exists():
            shutil.rmtree(d / old)
    (d / "backgrounds").mkdir()
    (d / "bin").mkdir(exist_ok=True)

    walls = []
    for i, h in enumerate(HEIRS, 1):
        hd = d / "heirs" / h["slug"]
        hd.mkdir(parents=True)
        toml, c = colors_toml(h)
        check_contrast(h, c)
        (hd / "colors.toml").write_text(toml)
        (hd / "chrysos-lock.json").write_text(lock_json(h, c))
        (hd / "icons.theme").write_text(h["icons"] + "\n")
        (hd / "README.md").write_text(readme(h))
        src = WALLS / h["wall"]
        link_or_copy(src, d / "backgrounds" / f"{i:02d}-{h['slug']}{src.suffix.lower()}")
        walls.append(src)
        print(f"  ✓ {h['name']}")

    # Keep whichever heir is already active across rebuilds.
    active = (d / "active-heir").read_text().strip() if (d / "active-heir").exists() else first
    if active not in BY_SLUG:
        active = first
    for f in ACTIVE_FILES:
        shutil.copy2(d / "heirs" / active / f, d / f)
    (d / "active-heir").write_text(active + "\n")

    shutil.copy2(HERE / "assets" / "hsr-logo.png", d / "chrysos-lock-logo.png")
    for name in ("chrysos-heirs-sync", "chrysos-heirs-watch"):
        shutil.copy2(HERE / "bin" / name, d / "bin" / name)
        (d / "bin" / name).chmod(0o755)
    (d / "README.md").write_text(readme(UMBRELLA))
    if previews or not (d / "preview.png").exists():
        _, c = colors_toml(UMBRELLA)
        render_umbrella_preview(UMBRELLA, c, walls, d / "preview.png")
    print(f"  ✓ theme '{THEME}' (active heir: {active})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path.home() / ".config/omarchy/themes"))
    ap.add_argument("--no-preview", action="store_true")
    a = ap.parse_args()
    build(Path(a.out), previews=not a.no_preview)
