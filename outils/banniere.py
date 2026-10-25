#!/usr/bin/env python3
"""Remplace « BÂTIMENT » par « MULTISERVICES » dans la ligne d'activités de la bannière Facebook.

Usage : python3 outils/banniere.py DOSSIER_POLICES BANNIERE_ORIGINALE.svg BANNIERE_SORTIE.svg
Texte vectorisé en Montserrat Regular 16 px, approche 0,28 em, comme l'original ; la ligne reste centrée.
"""
import re, sys
from pathlib import Path

# Fonctions de mise en forme partagées avec le script de la carte de visite.
g = {}
src = (Path(__file__).parent / "carte_visite.py").read_text(encoding="utf-8")
sys_argv, sys.argv = sys.argv, [sys.argv[0], sys.argv[1], "", ""]
exec(src[:src.index("# Mesures du verso")], g)
sys.argv = sys_argv

FONT, TAILLE, APPROCHE = g["FONTS"]["mont"], 16.0, 4.48
CENTRE, NB_SUBPATHS_ANCIEN_MOT = 820.0, 12  # « BÂTIMENT » = 12 contours en fin de tracé

svg = Path(sys.argv[2]).read_text(encoding="utf-8")
m = re.search(r'<path transform="translate\(([\d.]+),([\d.]+)\)" d="([^"]*)" fill="#C7A774"/>', svg)
ty, d = m.group(2), m.group(3)
contours = re.findall(r"M[^M]*", d)
gardes = contours[:-NB_SUBPATHS_ANCIEN_MOT]

# Positions mesurées dans l'original (getBBox) : bord gauche de la ligne et du « B » de BÂTIMENT.
DEBUT_LIGNE, BORD_B = 1.824, 602.512
origine = BORD_B - g["bounds"](FONT, "B", TAILLE, 0)[0]

gs, k, items = g["layout"](FONT, "MULTISERVICES", TAILLE, APPROCHE)
pen = g["SVGPathPen"](gs, ntos=lambda v: f"{v:.3f}".rstrip("0").rstrip("."))
for glyphe, x in items:
    gs[glyphe].draw(g["TransformPen"](pen, (k, 0, 0, -k, origine + x, 0)))
nouveau = pen.getCommands()
fin = origine + g["bounds"](FONT, "MULTISERVICES", TAILLE, APPROCHE)[2]
tx = CENTRE - (DEBUT_LIGNE + fin) / 2

nouveau_tag = f'<path transform="translate({tx:.3f},{ty})" d="{"".join(gardes)}{nouveau}" fill="#C7A774"/>'
Path(sys.argv[3]).write_text(svg.replace(m.group(0), nouveau_tag), encoding="utf-8")
print(f"mot placé à x={origine:.1f}, ligne {DEBUT_LIGNE:.1f}–{fin:.1f}, recentrée avec translate x={tx:.3f}")
