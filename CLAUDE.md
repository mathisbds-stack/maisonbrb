# Maison BRB — consignes pour Claude

- Après chaque modification du site : relancer `python3 outils/generer.py`, vérifier le rendu,
  puis committer et pousser sur GitHub sans attendre de confirmation.
- Les coordonnées et la zone d'intervention se modifient uniquement dans `INFOS` / `ZONE`
  (et l'adresse du site propre de chaque maison dans le champ `"site"` de `ACTIVITES`)
  en haut de `outils/generer.py` ; ne pas éditer les pages HTML générées à la main.
- Charte à respecter : noir #0B0B0B, or #C7A774, crème #F8F6EF ; Cormorant Garamond et Montserrat.
- Hébergement : Netlify (configuration dans `netlify.toml`). Domaine actuel : https://maisonbrb.netlify.app ;
  domaines achetés chez IONOS : maisonbrb.fr (site principal), brbmultiservices.fr (redirigé vers la page
  Multiservices), beaucaireinformatique.fr (site Beaucaire Informatique). Passer `INFOS["domaine"]` à
  https://maisonbrb.fr seulement quand le DNS pointe vers Netlify. Encore à renseigner dans `INFOS` : médiateur de la consommation.
