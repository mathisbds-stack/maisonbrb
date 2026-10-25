#!/usr/bin/env python3
"""Remplace les coordonnées du verso de la carte de visite (texte vectorisé, aucune police à installer).

Usage : python3 outils/carte_visite.py DOSSIER_POLICES VERSO_ORIGINAL.svg VERSO_SORTIE.svg
DOSSIER_POLICES contient Cormorant-600.ttf, Cormorant-500i.ttf, Montserrat-400.ttf et Montserrat-500.ttf (Google Fonts).
"""
import re, sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

F = sys.argv[1]
FONTS = {
    "corm": TTFont(F + "/Cormorant-600.ttf"), "mont": TTFont(F + "/Montserrat-400.ttf"),
    "corm_i": TTFont(F + "/Cormorant-500i.ttf"), "mont_m": TTFont(F + "/Montserrat-500.ttf"),
}

def layout(font, text, size, track):
    """Glyphes posés sur la ligne de base (y vers le bas), avec approche (tracking) en unités px."""
    cmap, gs, hmtx = font.getBestCmap(), font.getGlyphSet(), font["hmtx"]
    k = size / font["head"].unitsPerEm
    x, items = 0.0, []
    for i, ch in enumerate(text):
        g = cmap[ord(ch)]
        items.append((g, x))
        x += hmtx[g][0] * k + (track if i < len(text) - 1 else 0)
    return gs, k, items

def bounds(font, text, size, track):
    gs, k, items = layout(font, text, size, track)
    bp = BoundsPen(gs)
    for g, x in items:
        gs[g].draw(TransformPen(bp, (k, 0, 0, -k, x, 0)))
    return bp.bounds  # xmin, ymin, xmax, ymax (y vers le bas)

def path(font, text, size, track):
    gs, k, items = layout(font, text, size, track)
    sp = SVGPathPen(gs, ntos=lambda v: f"{v:.3f}".rstrip("0").rstrip("."))
    for g, x in items:
        gs[g].draw(TransformPen(sp, (k, 0, 0, -k, x, 0)))
    return sp.getCommands()

def fit(font, text, h_top, width):
    """Retrouve taille et approche à partir de la boîte mesurée sur le fichier d'origine."""
    b = bounds(font, text, 100, 0)
    size = 100 * h_top / -b[1]
    b = bounds(font, text, size, 0)
    track = (width - (b[2] - b[0])) / (len(text) - 1)
    return size, track

# Mesures du verso d'origine (getBBox) : (police, texte d'origine, hauteur au-dessus de la ligne, largeur)
ORIG = {
    1: ("corm", "Prénom NOM", 29.24, 247.36),
    3: ("mont", "06 XX XX XX XX", 11.30, 128.29),
    4: ("mont", "votre@email.fr", 11.95, 125.42),
    5: ("mont", "www.votresite.fr", 11.95, 139.23),
    10: ("mont_m", "BRB BÂTIMENT", 11.97, 123.27),
    11: ("corm_i", "Rénovation & aménagement", 13.90, 203.06),
}
NEW = {
    1: "Mathis BORDES", 3: "07 81 78 73 60", 4: "contact.maisonbrb@gmail.com", 5: "maisonbrb.fr",
    10: "BRB MULTISERVICES", 11: "Petits travaux & bricolage",
}

src = open(sys.argv[2], encoding="utf-8").read()
# Seuls les tracés positionnés (logo et textes) sont numérotés, pas ceux des icônes.
paths = list(re.finditer(r'<path transform="translate[^>]*/>', src))
out, last = [], 0
for i, m in enumerate(paths):
    if i in ORIG:
        f, t, h, w = ORIG[i]
        size, track = fit(FONTS[f], t, h, w)
        print(f"#{i} {t!r}: taille {size:.2f}px, approche {track:.2f}px -> {NEW[i]!r}")
        tag = m.group(0)
        new = re.sub(r' d="[^"]*"', ' d="' + path(FONTS[f], NEW[i], size, track) + '"', tag)
        out.append(src[last:m.start()]); out.append(new); last = m.end()
out.append(src[last:])
open(sys.argv[3], "w", encoding="utf-8").write("".join(out))
