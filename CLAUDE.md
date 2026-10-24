# Maison BRB — consignes pour Claude

- Après chaque modification du site : relancer `python3 outils/generer.py`, vérifier le rendu,
  puis committer et pousser sur GitHub sans attendre de confirmation.
- Les coordonnées et la zone d'intervention se modifient uniquement dans `INFOS` / `ZONE`
  en haut de `outils/generer.py` ; ne pas éditer les pages HTML générées à la main.
- Charte à respecter : noir #0B0B0B, or #C7A774, crème #F8F6EF ; Cormorant Garamond et Montserrat.
- Hébergement : Netlify (configuration dans `netlify.toml`). Domaine : https://maisonbrb.netlify.app. Encore à renseigner dans `INFOS` : médiateur de la consommation.
