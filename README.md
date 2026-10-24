# Maison BRB — site vitrine

Site statique : BRB AutoPro, Beaucaire Informatique, BRB Bâtiment.

## Pages
- `index.html` — accueil Maison BRB
- `brb-autopro.html`, `beaucaire-informatique.html`, `brb-batiment.html` — une page par activité
- `mentions-legales.html`, `404.html`, `sitemap.xml`, `robots.txt`

## Modifier les informations
Toutes les coordonnées (e-mail, horaires, nom, SIRET, adresse, domaine, hébergeur, médiateur)
et la liste des communes desservies se trouvent en haut de `outils/generer.py`.
Après modification : `python3 outils/generer.py`, puis remettre les fichiers en ligne.

## Mise en ligne
Renseigner le domaine dans `outils/generer.py` et relancer le script (cela ajoute `sitemap.xml`
et les liens canoniques). Déposer ensuite tout le contenu du dossier (sauf `outils/` et `README.md`) chez l'hébergeur
(OVH, o2switch, Netlify, GitHub Pages…). Puis déclarer `sitemap.xml` dans Google Search Console
et créer la fiche Google Business Profile avec le même nom, numéro et adresse que le site.
