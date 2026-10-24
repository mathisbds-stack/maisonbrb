#!/usr/bin/env python3
"""Génère les pages HTML statiques du site Maison BRB.

Modifier les informations dans INFOS ci-dessous, puis lancer :
    python3 outils/generer.py
Les pages sont écrites à la racine du dépôt (index.html, brb-autopro.html, …).
"""
import json
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Vos informations — remplacez chaque valeur None.
# ---------------------------------------------------------------------------
INFOS = {
    "tel": "07 81 78 73 60",
    "tel_intl": "+33781787360",
    "email": "contact.maisonbrb@gmail.com",
    "horaires": "Du lundi au samedi, de 8 h à 19 h",
    "nom": "Mathis Bordes",   # Prénom NOM de l'entrepreneur
    "siret": "981 177 272 00029",
    "adresse": "59 rue de Ponthieu, bureau 326, 75008 Paris",
    "domaine": None,          # ex. "https://www.maisonbrb.fr" (sans / final) ; sans domaine, les URL restent relatives
    "hebergeur": None,        # ex. "OVH SAS, 2 rue Kellermann, 59100 Roubaix, 1007"
    "mediateur": None,        # médiateur de la consommation : nom, adresse, site web
}

# Zone d'intervention : la première ville est mise en avant.
ZONE = [
    "Beaucaire", "Tarascon", "Fourques", "Vallabrègues", "Jonquières-Saint-Vincent",
    "Comps", "Bellegarde", "Aramon", "Montfrin", "Meynes", "Redessan", "Manduel",
    "Boulbon", "Saint-Étienne-du-Grès", "Arles", "Nîmes",
]
CP = "30300"
GEO = {"latitude": 43.8083, "longitude": 4.6436}  # centre de Beaucaire

MANQUANT = "[à compléter]"


def info(cle):
    return INFOS[cle] or MANQUANT


def domaine():
    return (INFOS["domaine"] or "").rstrip("/")


def url(page):
    if not domaine():
        return "./" if page == "index.html" else page
    return domaine() + "/" + ("" if page == "index.html" else page)


def asset(nom):
    return (domaine() + "/" if domaine() else "") + "assets/" + nom


# ---------------------------------------------------------------------------
# Éléments communs
# ---------------------------------------------------------------------------
ICONES = {
    "auto": '<svg class="ic" viewBox="0 0 31 21" aria-hidden="true"><path d="M2 15 L2 11.5 Q2 10 3.5 9.6 L7 8.8 L10 5.6 Q11 4.6 12.6 4.6 L19 4.6 Q20.6 4.6 21.6 5.8 L24 8.8 L27.5 9.6 Q29 10 29 11.5 L29 15 Z"/><path d="M7 8.8 L24 8.8"/><circle cx="8.5" cy="15.5" r="2.6" fill="{fond}"/><circle cx="22.5" cy="15.5" r="2.6" fill="{fond}"/></svg>',
    "info": '<svg class="ic" viewBox="0 0 31 21" aria-hidden="true"><rect x="5" y="2.5" width="21" height="13.5" rx="1.6"/><path d="M15.5 16 L15.5 19.5 M10.5 20 L20.5 20"/></svg>',
    "bat": '<svg class="ic" viewBox="0 0 31 21" aria-hidden="true"><path d="M4 11 L15.5 2 L27 11"/><path d="M7 9 L7 20 L24 20 L24 9"/><rect x="13" y="11.5" width="5" height="5"/><path d="M15.5 11.5 L15.5 16.5 M13 14 L18 14"/></svg>',
}


def icone(nom, fond="#fff"):
    return ICONES[nom].replace("{fond}", fond)


NAV = [
    ("index.html", "Accueil"),
    ("brb-autopro.html", "BRB AutoPro"),
    ("beaucaire-informatique.html", "Informatique"),
    ("brb-batiment.html", "Bâtiment"),
]

ADRESSE_LD = {
    "@type": "PostalAddress",
    "addressLocality": "Beaucaire",
    "postalCode": CP,
    "addressRegion": "Occitanie",
    "addressCountry": "FR",
}


def entreprise_ld(type_, nom, page, description, services):
    d = {
        "@context": "https://schema.org",
        "@type": type_,
        "@id": url(page) + "#entreprise",
        "name": nom,
        "description": description,
        "url": url(page),
        "image": asset("og-maison-brb.png"),
        "logo": asset("logo-carre.png"),
        "telephone": INFOS["tel_intl"],
        "address": ADRESSE_LD,
        "geo": {"@type": "GeoCoordinates", **GEO},
        "areaServed": [{"@type": "City", "name": v} for v in ZONE],
        "hasOfferCatalog": {
            "@type": "OfferCatalog",
            "name": "Prestations " + nom,
            "itemListElement": [
                {"@type": "Offer", "itemOffered": {"@type": "Service", "name": s}} for s in services
            ],
        },
    }
    if INFOS["email"]:
        d["email"] = INFOS["email"]
    d["openingHoursSpecification"] = [{
        "@type": "OpeningHoursSpecification",
        "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
        "opens": "08:00", "closes": "19:00",
    }]
    if page != "index.html":
        d["parentOrganization"] = {"@id": url("index.html") + "#entreprise"}
    return d


def fil_ld(page, titre):
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Maison BRB", "item": url("index.html")},
            {"@type": "ListItem", "position": 2, "name": titre, "item": url(page)},
        ],
    }


def faq_ld(faq):
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": r}}
            for q, r in faq
        ],
    }


def tete(page, titre, description, donnees=(), robots="index, follow"):
    ld = "\n".join(
        '<script type="application/ld+json">' + json.dumps(d, ensure_ascii=False) + "</script>"
        for d in donnees
    )
    og_absolu = f"""<meta property="og:url" content="{url(page)}">
<meta property="og:image" content="{asset('og-maison-brb.png')}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
""" if domaine() else ""
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{titre}</title>
<meta name="description" content="{description}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{url(page)}">
<meta name="theme-color" content="#0B0B0B">
<meta name="geo.region" content="FR-30">
<meta name="geo.placename" content="Beaucaire">
<meta name="geo.position" content="{GEO['latitude']};{GEO['longitude']}">
<meta name="ICBM" content="{GEO['latitude']}, {GEO['longitude']}">
<meta property="og:type" content="website">
<meta property="og:locale" content="fr_FR">
<meta property="og:site_name" content="Maison BRB">
<meta property="og:title" content="{titre}">
<meta property="og:description" content="{description}">
{og_absolu}<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="icon" href="assets/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="assets/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Montserrat:wght@300;400;500&display=swap">
<link rel="stylesheet" href="assets/style.css">
{ld}
</head>
<body>
<a class="skip" href="#contenu">Aller au contenu</a>
"""


def entete(page):
    liens = "\n".join(
        f'      <a href="{p}"' + (' aria-current="page"' if p == page else "") + f">{t}</a>"
        for p, t in NAV
    )
    return f"""<header>
  <div class="wrap">
    <a class="brand" href="index.html" aria-label="Maison BRB, accueil"><img src="assets/monogramme-or.svg" alt="" width="52" height="34"><span>MAISON BRB</span></a>
    <nav class="main" aria-label="Navigation principale">
{liens}
      <a href="#contact">Contact</a>
    </nav>
  </div>
</header>
"""


def contact(activite=None):
    precision = (
        f"Appelez ou écrivez pour votre besoin {activite}." if activite
        else "Appelez ou écrivez en précisant l'activité concernée."
    )
    if INFOS["email"]:
        mail = f'<a class="v" id="mail" href="mailto:{INFOS["email"]}">{INFOS["email"]}</a><button class="copy" type="button" data-copy="mail">Copier l\'adresse</button>'
    else:
        mail = f'<span class="v" id="mail">{MANQUANT}</span>'
    return f"""  <section class="band contact" id="contact">
    <div class="wrap">
      <div class="head">
        <span class="eyebrow">Contact</span>
        <h2>Parlons de votre besoin</h2>
        <p>{precision} Réponse rapide, devis gratuit et sans engagement, à Beaucaire et dans un rayon d'environ 30 km.</p>
      </div>
      <div class="card">
        <div class="row"><span class="k">Téléphone</span><a class="v" id="tel" href="tel:{INFOS['tel_intl']}">{INFOS['tel']}</a><button class="copy" type="button" data-copy="tel">Copier le numéro</button></div>
        <div class="row"><span class="k">E-mail</span>{mail}</div>
        <div class="row"><span class="k">Horaires</span><span class="v">{info('horaires')}</span></div>
      </div>
    </div>
  </section>
"""


def pied():
    villes = ", ".join(ZONE[:-1]) + " et " + ZONE[-1]
    return f"""<footer>
  <div class="wrap">
    <div class="foot-top">
      <div>
        <img class="logo" src="assets/logo-maison-brb.svg" alt="Maison BRB, l'art de prendre soin de ce qui compte" width="200" height="138">
        <p>Maison BRB : detailing automobile, dépannage informatique et petits travaux à Beaucaire ({CP}, Gard). Nous intervenons à {villes}.</p>
      </div>
      <div>
        <h2>Nos maisons</h2>
        <ul>
          <li><a href="brb-autopro.html">BRB AutoPro, detailing automobile</a></li>
          <li><a href="beaucaire-informatique.html">Beaucaire Informatique, dépannage</a></li>
          <li><a href="brb-batiment.html">BRB Bâtiment, petits travaux</a></li>
        </ul>
      </div>
      <div>
        <h2>Contact</h2>
        <ul>
          <li><a href="tel:{INFOS['tel_intl']}">{INFOS['tel']}</a></li>
          <li>{f'<a href="mailto:{INFOS["email"]}">{INFOS["email"]}</a>' if INFOS['email'] else MANQUANT}</li>
          <li>{info('horaires')}</li>
        </ul>
      </div>
    </div>
    <div class="foot-bottom">
      <span>Maison BRB · {info('nom')} EI · SIRET {info('siret')}</span>
      <a href="mentions-legales.html">Mentions légales</a>
    </div>
  </div>
</footer>
<a class="callbar" href="tel:{INFOS['tel_intl']}"><span aria-hidden="true">☎</span> Appeler · {INFOS['tel']}</a>
<script src="assets/site.js" defer></script>
</body>
</html>
"""


def zone_section(sombre=True):
    puces = "\n".join(
        f'          <li{" class=\"main\"" if i == 0 else ""}>{v}</li>' for i, v in enumerate(ZONE)
    )
    classe = "band" if sombre else "band light"
    return f"""  <section class="{classe}" id="zone">
    <div class="wrap">
      <div class="head">
        <span class="eyebrow">Zone d'intervention</span>
        <h2>Beaucaire et ses environs</h2>
        <p>Basés à Beaucaire ({CP}), nous nous déplaçons dans le Gard et les Bouches-du-Rhône voisines, entre Nîmes, Arles et Tarascon. Votre commune n'apparaît pas ? Appelez-nous, nous trouverons une solution.</p>
      </div>
      <ul class="towns">
{puces}
      </ul>
    </div>
  </section>
"""


def faq_section(faq):
    items = "\n".join(
        f"        <details><summary>{q}</summary><p>{r}</p></details>" for q, r in faq
    )
    return f"""  <section class="band light" id="questions">
    <div class="wrap">
      <div class="head">
        <span class="eyebrow">Questions fréquentes</span>
        <h2>Vos questions, nos réponses</h2>
      </div>
      <div class="faq">
{items}
      </div>
    </div>
  </section>
"""


def etapes_section(titre, intro, etapes):
    items = "\n".join(
        f'        <div class="pledge"><h3>{t}</h3><p>{d}</p></div>' for t, d in etapes
    )
    return f"""  <section class="band split">
    <div class="wrap">
      <div class="head">
        <span class="eyebrow">Notre méthode</span>
        <h2>{titre}</h2>
        <p>{intro}</p>
      </div>
      <div>
{items}
      </div>
    </div>
  </section>
"""


# ---------------------------------------------------------------------------
# Pages d'activité
# ---------------------------------------------------------------------------
ACTIVITES = [
    {
        "page": "brb-autopro.html",
        "nom": "BRB AutoPro",
        "icone": "auto",
        "type": "AutoWash",
        "titre": "BRB AutoPro · Detailing et nettoyage automobile à Beaucaire (30)",
        "description": "BRB AutoPro, detailing automobile à Beaucaire : nettoyage intérieur, lavage, polissage, rénovation des optiques et protection carrosserie. Tarascon, Nîmes, Arles. Devis gratuit.",
        "h1": "Detailing automobile à Beaucaire",
        "lead": "L'esthétique et la protection de votre véhicule, à l'intérieur comme à l'extérieur, avec le soin d'un atelier haut de gamme. Citadine, berline, SUV ou utilitaire : chaque véhicule est traité selon son état et vos attentes.",
        "activite": "en detailing automobile",
        "prestations_intro": "Des prestations à la carte ou combinées, toujours précédées d'un état des lieux de votre véhicule et d'un devis clair.",
        "prestations": [
            ("Nettoyage intérieur en profondeur", "Aspiration complète, shampoing des sièges et moquettes, nettoyage des plastiques, des vitres et des recoins. Un habitacle sain, débarrassé des taches et des odeurs."),
            ("Lavage et décontamination extérieure", "Prélavage, lavage manuel soigné, décontamination de la carrosserie et des jantes pour retirer goudron, résidus ferreux et saletés incrustées."),
            ("Polissage et correction de la peinture", "Atténuation des micro-rayures et du voile terne pour redonner profondeur et brillance à la peinture."),
            ("Rénovation des optiques", "Des phares jaunis ou opacifiés retrouvent leur transparence : un vrai gain esthétique et de visibilité la nuit."),
            ("Protection de la carrosserie", "Application d'une protection pour préserver la brillance et faciliter l'entretien face au soleil, à la pluie et à la pollution."),
            ("Préparation avant vente", "Un véhicule présenté sous son meilleur jour se vend plus vite : remise en état esthétique complète avant votre annonce."),
        ],
        "etapes_titre": "Un véhicule rendu comme on aimerait le recevoir",
        "etapes_intro": "Le detailing est une affaire de patience et de méthode. Voici comment se déroule chaque prestation.",
        "etapes": [
            ("Diagnostic", "Nous regardons ensemble l'état du véhicule et ce qui compte pour vous, puis nous établissons un devis précis."),
            ("Préparation", "Produits adaptés à chaque surface : cuir, tissu, plastiques, peinture, jantes. Rien n'est traité au hasard."),
            ("Exécution", "Travail manuel, minutieux, sans précipitation. Les zones délicates sont protégées avant intervention."),
            ("Contrôle", "Vérification finale avec vous et conseils d'entretien pour faire durer le résultat."),
        ],
        "faq": [
            ("Proposez-vous le detailing automobile à Beaucaire et aux alentours ?", "Oui. BRB AutoPro est basé à Beaucaire et intervient à Tarascon, Fourques, Vallabrègues, Bellegarde, Nîmes, Arles et dans les communes voisines. Appelez-nous pour vérifier votre secteur."),
            ("Combien de temps dure une prestation ?", "Cela dépend de l'état du véhicule et des prestations choisies : de quelques heures pour un nettoyage intérieur à une journée complète pour une rénovation avec polissage. La durée est indiquée sur le devis."),
            ("Le devis est-il gratuit ?", "Oui, le devis est gratuit et sans engagement. Il détaille chaque prestation pour que vous sachiez exactement ce qui sera fait."),
            ("Quelle différence entre un lavage et du detailing ?", "Un lavage enlève la saleté visible. Le detailing va plus loin : décontamination, correction des défauts de peinture, rénovation et protection, avec un travail minutieux sur chaque surface, intérieur compris."),
        ],
    },
    {
        "page": "beaucaire-informatique.html",
        "nom": "Beaucaire Informatique",
        "icone": "info",
        "type": "ProfessionalService",
        "titre": "Beaucaire Informatique · Dépannage informatique à domicile à Beaucaire",
        "description": "Beaucaire Informatique : dépannage et réparation d'ordinateur, installation, optimisation et assistance à domicile ou en atelier à Beaucaire, Tarascon, Nîmes et environs.",
        "h1": "Dépannage informatique à Beaucaire",
        "lead": "Un ordinateur lent, une panne, une installation à faire : intervention à domicile ou en atelier, avec des explications claires et sans jargon.",
        "activite": "en informatique",
        "prestations_intro": "Pour les particuliers comme pour les petites structures, une aide concrète et des conseils compréhensibles.",
        "prestations": [
            ("Dépannage et réparation", "Ordinateur qui ne démarre plus, écran bleu, messages d'erreur, matériel défaillant : diagnostic de la panne et réparation."),
            ("Nettoyage et optimisation", "Un ordinateur qui rame retrouve de la vitesse : suppression des logiciels inutiles, nettoyage, mises à jour et réglages."),
            ("Suppression de virus", "Recherche et élimination des logiciels malveillants, puis mise en place d'une protection adaptée."),
            ("Installation et configuration", "Mise en service d'un nouvel ordinateur, transfert de vos données, installation d'imprimante, de logiciels et de la messagerie."),
            ("Internet et Wi-Fi", "Box, réseau Wi-Fi capricieux, connexion des appareils de la maison : nous remettons tout en ordre."),
            ("Assistance et initiation", "Des explications à votre rythme pour être autonome avec votre ordinateur, votre tablette ou votre smartphone."),
        ],
        "etapes_titre": "Une aide claire, du diagnostic à la solution",
        "etapes_intro": "Vous n'avez pas besoin de connaître les termes techniques : décrivez simplement le problème.",
        "etapes": [
            ("Écoute", "Vous décrivez la panne ou le besoin par téléphone. Nous vous disons tout de suite si une intervention est utile."),
            ("Diagnostic", "Examen de la machine à domicile ou en atelier, puis devis clair avant toute réparation."),
            ("Intervention", "Réparation, nettoyage ou installation, dans le respect de vos données et de vos réglages."),
            ("Explications", "Nous vous montrons ce qui a été fait et comment éviter que le problème revienne."),
        ],
        "faq": [
            ("Faites-vous le dépannage informatique à domicile à Beaucaire ?", "Oui. Beaucaire Informatique se déplace à domicile à Beaucaire, Tarascon, Fourques, Jonquières-Saint-Vincent, Nîmes, Arles et dans les communes proches. L'intervention peut aussi se faire en atelier."),
            ("Mon ordinateur est très lent, peut-on le sauver ?", "Très souvent, oui. Un nettoyage et une optimisation suffisent dans de nombreux cas. Si une pièce est en cause, nous vous le disons et vous proposons la solution la plus raisonnable."),
            ("Mes données sont-elles en sécurité ?", "Vos fichiers sont traités avec discrétion. Avant toute intervention qui pourrait les toucher, nous vous proposons de les sauvegarder."),
            ("Le devis est-il gratuit ?", "Oui, le devis est gratuit et sans engagement. Vous savez ce qui sera fait avant que nous commencions."),
        ],
    },
    {
        "page": "brb-batiment.html",
        "nom": "BRB Bâtiment",
        "icone": "bat",
        "type": "HomeAndConstructionBusiness",
        "titre": "BRB Bâtiment · Petits travaux et montage de meubles à Beaucaire",
        "description": "BRB Bâtiment, petits travaux à Beaucaire : montage de meubles, pose d'étagères, tringles et supports TV, petites réparations et entretien de la maison. Tarascon, Nîmes, Arles.",
        "h1": "Petits travaux et entretien à Beaucaire",
        "lead": "Les petites tâches de la maison confiées à quelqu'un de soigneux, qui arrive à l'heure et laisse les lieux propres.",
        "activite": "en petits travaux",
        "prestations_intro": "Ces petits travaux qu'on repousse depuis des semaines, réalisés proprement et rapidement.",
        "prestations": [
            ("Montage de meubles", "Armoires, lits, cuisines en kit, bureaux, dressings : montage soigné, réglé et fixé au mur si nécessaire."),
            ("Fixations murales", "Étagères, tringles à rideaux, supports TV, miroirs, cadres : perçage adapté à votre mur, niveau et solidité vérifiés."),
            ("Petites réparations", "Porte qui frotte, poignée cassée, joint à refaire, silicone, petits ajustements du quotidien."),
            ("Entretien courant de l'habitat", "Petits travaux d'entretien intérieur et extérieur pour garder votre logement en bon état."),
            ("Aménagement et rangement", "Installation de rangements, patères, crochets et accessoires pour optimiser vos espaces."),
            ("Aide à l'emménagement", "Montage, fixations et finitions pour vous installer sereinement dans votre nouveau logement."),
        ],
        "etapes_titre": "Ponctuel, soigneux, et les lieux restent propres",
        "etapes_intro": "Pour les petits travaux, la confiance compte autant que le geste. Voici nos engagements.",
        "etapes": [
            ("Devis clair", "Vous décrivez le besoin, avec une photo si possible, et recevez un devis précis avant toute intervention."),
            ("Ponctualité", "Un créneau convenu ensemble et respecté. Vous êtes prévenu en cas d'imprévu."),
            ("Travail soigné", "Le bon outillage et les bonnes fixations pour un résultat solide et durable."),
            ("Lieux propres", "Protection des sols, nettoyage en fin de chantier et emballages emportés sur demande."),
        ],
        "faq": [
            ("Intervenez-vous pour les petits travaux à Beaucaire et aux alentours ?", "Oui. BRB Bâtiment intervient à Beaucaire, Tarascon, Vallabrègues, Comps, Aramon, Montfrin, Nîmes, Arles et dans les communes voisines."),
            ("Quels types de travaux réalisez-vous ?", "Les petits travaux et l'entretien de la maison : montage de meubles, fixations murales, petites réparations, aménagements de rangement. Pour un chantier plus important, contactez-nous pour en parler."),
            ("Pouvez-vous fixer une télévision au mur ?", "Oui. Nous posons votre support TV en choisissant les chevilles adaptées à votre mur, avec un résultat de niveau et solide."),
            ("Le devis est-il gratuit ?", "Oui, le devis est gratuit et sans engagement. Une photo de ce qu'il y a à faire permet souvent de vous répondre plus vite."),
        ],
    },
]


def page_activite(a):
    services = [p[0] for p in a["prestations"]]
    donnees = [
        entreprise_ld(a["type"], a["nom"], a["page"], a["description"], services),
        fil_ld(a["page"], a["nom"]),
        faq_ld(a["faq"]),
    ]
    cartes = "\n".join(
        f"""        <article class="house plain">
          <h3>{t}</h3>
          <p>{d}</p>
        </article>""" for t, d in a["prestations"]
    )
    autres = [x for x in ACTIVITES if x is not a]
    liens = "\n".join(
        f"""        <article class="house">
          {icone(x['icone'])}
          <span class="name">{x['nom']}</span>
          <h3>{x['h1'].replace(' à Beaucaire', '')}</h3>
          <p>{x['lead']}</p>
          <a class="go" href="{x['page']}"><span>Découvrir {x['nom']}</span><span aria-hidden="true">→</span></a>
        </article>""" for x in autres
    )
    corps = f"""<main id="contenu">
  <section class="hero sub">
    <div class="wrap">
      <nav class="crumbs" aria-label="Fil d'Ariane"><ol><li><a href="index.html">Maison BRB</a></li><li aria-current="page">{a['nom']}</li></ol></nav>
      {icone(a['icone'], '#151411')}
      <h1><em>{a['nom']}</em>{a['h1']}</h1>
      <div class="tri" aria-hidden="true"><i></i><i></i><i></i></div>
      <p class="lead">{a['lead']}</p>
      <div class="btns">
        <a class="btn solid" href="tel:{INFOS['tel_intl']}">Appeler · {INFOS['tel']}</a>
        <a class="btn" href="#prestations">Nos prestations <span aria-hidden="true">↓</span></a>
      </div>
    </div>
  </section>

  <section class="band light" id="prestations">
    <div class="wrap">
      <div class="head">
        <span class="eyebrow">Prestations</span>
        <h2>Ce que {a['nom']} fait pour vous</h2>
        <p>{a['prestations_intro']}</p>
      </div>
      <div class="grid">
{cartes}
      </div>
    </div>
  </section>

{etapes_section(a['etapes_titre'], a['etapes_intro'], a['etapes'])}
{faq_section(a['faq'])}
{zone_section()}
  <section class="band light">
    <div class="wrap">
      <div class="head">
        <span class="eyebrow">Maison BRB</span>
        <h2>Les autres maisons</h2>
        <p>Le même interlocuteur et la même exigence pour vos autres besoins.</p>
      </div>
      <div class="grid two">
{liens}
      </div>
    </div>
  </section>

{contact(a['activite'])}</main>
"""
    return tete(a["page"], a["titre"], a["description"], donnees) + entete(a["page"]) + corps + pied()


# ---------------------------------------------------------------------------
# Accueil
# ---------------------------------------------------------------------------
def page_accueil():
    description = "Maison BRB à Beaucaire (30) : detailing automobile, dépannage informatique et petits travaux. Un seul interlocuteur, un travail soigné, à Tarascon, Nîmes, Arles et environs."
    ld = entreprise_ld(
        "LocalBusiness", "Maison BRB", "index.html", description,
        ["Detailing automobile", "Dépannage informatique", "Petits travaux et entretien"],
    )
    ld["slogan"] = "L'art de prendre soin de ce qui compte."
    ld["department"] = [{"@id": url(a["page"]) + "#entreprise"} for a in ACTIVITES]
    site_ld = {
        "@context": "https://schema.org", "@type": "WebSite",
        "name": "Maison BRB", "url": url("index.html"), "inLanguage": "fr-FR",
    }
    cartes = []
    puces = {
        "brb-autopro.html": ["Nettoyage intérieur en profondeur", "Lavage et décontamination extérieure", "Polissage et rénovation des optiques", "Protection de la carrosserie"],
        "beaucaire-informatique.html": ["Dépannage et réparation", "Installation et configuration", "Nettoyage et optimisation", "Assistance et initiation"],
        "brb-batiment.html": ["Montage de meubles", "Fixations : étagères, tringles, supports TV", "Petites réparations ponctuelles", "Entretien courant de l'habitat"],
    }
    sous_titres = {
        "brb-autopro.html": ("Detailing automobile", "L'esthétique et la protection de votre véhicule, à l'intérieur comme à l'extérieur, avec le soin d'un atelier haut de gamme."),
        "beaucaire-informatique.html": ("Dépannage &amp; assistance", "Un ordinateur lent, une panne, une installation à faire : intervention à domicile ou en atelier, avec des explications claires."),
        "brb-batiment.html": ("Petits travaux &amp; entretien", "Les petites tâches de la maison confiées à quelqu'un de soigneux, qui arrive à l'heure et laisse les lieux propres."),
    }
    for a in ACTIVITES:
        h3, p = sous_titres[a["page"]]
        li = "".join(f"<li>{x}</li>" for x in puces[a["page"]])
        cartes.append(f"""        <article class="house">
          {icone(a['icone'])}
          <span class="name">{a['nom']}</span>
          <h3>{h3}</h3>
          <p>{p}</p>
          <ul>{li}</ul>
          <a class="go" href="{a['page']}"><span>Visiter {a['nom']}</span><span aria-hidden="true">→</span></a>
        </article>""")
    cartes = "\n".join(cartes)
    corps = f"""<main id="contenu">
  <section class="hero">
    <div class="wrap">
      <img class="mono" src="assets/monogramme-or.svg" alt="Monogramme BRB" width="360" height="238">
      <h1>MAISON BRB</h1>
      <div class="tri" aria-hidden="true"><i></i><i></i><i></i></div>
      <p class="slogan">L'art de prendre soin de ce qui compte.</p>
      <p class="lead">Votre véhicule, votre matériel informatique, votre intérieur : trois savoir-faire réunis sous une même exigence à Beaucaire, avec un seul interlocuteur du premier appel à la dernière finition.</p>
      <div class="btns">
        <a class="btn" href="#maisons">Découvrir nos trois maisons <span aria-hidden="true">↓</span></a>
        <a class="btn solid" href="tel:{INFOS['tel_intl']}">Appeler · {INFOS['tel']}</a>
      </div>
    </div>
  </section>

  <section class="band light" id="maisons">
    <div class="wrap">
      <div class="head">
        <span class="eyebrow">Nos maisons</span>
        <h2>Trois expertises, une seule exigence</h2>
        <p>Detailing automobile, dépannage informatique et petits travaux à Beaucaire et dans ses environs. Chaque activité a sa page, ses prestations et ses réponses à vos questions.</p>
      </div>
      <div class="grid">
{cartes}
      </div>
    </div>
  </section>

  <section class="band split" id="esprit">
    <div class="wrap">
      <div class="head">
        <span class="eyebrow">L'esprit Maison</span>
        <h2>Ce qui ne change pas, quelle que soit la mission</h2>
        <p>Une voiture, un ordinateur ou une étagère méritent la même attention. C'est l'idée qui réunit nos trois maisons.</p>
      </div>
      <div>
        <div class="pledge"><h3>Un seul contact</h3><p>Un même numéro pour vos trois besoins. Vous expliquez une fois, on s'occupe du reste.</p></div>
        <div class="pledge"><h3>Le soin du détail</h3><p>Un devis clair avant chaque intervention, du matériel de qualité, et un travail vérifié avant de partir.</p></div>
        <div class="pledge"><h3>Proximité</h3><p>Une entreprise locale qui se déplace chez vous, à Beaucaire, Tarascon, Nîmes, Arles et dans les communes voisines.</p></div>
      </div>
    </div>
  </section>

{zone_section(sombre=False)}
{contact()}</main>
"""
    return tete("index.html", "Maison BRB · Detailing auto, dépannage informatique et petits travaux à Beaucaire", description, [ld, site_ld]) + entete("index.html") + corps + pied()


# ---------------------------------------------------------------------------
# Mentions légales et 404
# ---------------------------------------------------------------------------
def page_mentions():
    corps = f"""<main id="contenu">
  <section class="hero sub">
    <div class="wrap">
      <nav class="crumbs" aria-label="Fil d'Ariane"><ol><li><a href="index.html">Maison BRB</a></li><li aria-current="page">Mentions légales</li></ol></nav>
      <h1>Mentions légales</h1>
      <div class="tri" aria-hidden="true"><i></i><i></i><i></i></div>
    </div>
  </section>
  <section class="band light">
    <div class="wrap">
      <div class="prose">
        <section>
          <h2>Éditeur du site</h2>
          <p>Le présent site est édité par <strong>{info('nom')}</strong>, entrepreneur individuel (EI), exerçant sous le nom commercial <strong>Maison BRB</strong> et sous les enseignes BRB AutoPro, Beaucaire Informatique et BRB Bâtiment.</p>
          <ul>
            <li>Adresse : {info('adresse')}</li>
            <li>SIRET : {info('siret')}</li>
            <li>Téléphone : <a href="tel:{INFOS['tel_intl']}">{INFOS['tel']}</a></li>
            <li>E-mail : {f'<a href="mailto:{INFOS["email"]}">{INFOS["email"]}</a>' if INFOS['email'] else MANQUANT}</li>
          </ul>
          <p>Directeur de la publication : {info('nom')}.</p>
        </section>
        <section>
          <h2>Hébergement</h2>
          <p>Le site est hébergé par : {info('hebergeur')}.</p>
        </section>
        <section>
          <h2>Propriété intellectuelle</h2>
          <p>L'ensemble des contenus de ce site (textes, logos, monogramme BRB, mise en page) est la propriété exclusive de Maison BRB, sauf mention contraire. Toute reproduction, représentation ou adaptation, totale ou partielle, sans autorisation écrite préalable est interdite.</p>
        </section>
        <section>
          <h2>Données personnelles</h2>
          <p>Ce site ne comporte ni formulaire, ni création de compte, ni outil de mesure d'audience. Aucune donnée personnelle n'y est collectée directement.</p>
          <p>Les informations que vous transmettez par téléphone ou par e-mail (nom, coordonnées, description de votre besoin) sont utilisées uniquement pour répondre à votre demande, établir un devis et réaliser la prestation. Elles ne sont ni vendues ni cédées à des tiers, et sont conservées le temps nécessaire à la relation commerciale et aux obligations comptables.</p>
          <p>Conformément au Règlement général sur la protection des données (RGPD) et à la loi Informatique et Libertés, vous disposez d'un droit d'accès, de rectification, d'effacement et d'opposition sur vos données. Pour l'exercer, contactez-nous par e-mail ou par téléphone. Vous pouvez également adresser une réclamation à la CNIL (www.cnil.fr).</p>
        </section>
        <section>
          <h2>Cookies et services tiers</h2>
          <p>Ce site ne dépose aucun cookie publicitaire ou de mesure d'audience. Les polices de caractères sont chargées depuis le service Google Fonts, ce qui implique la transmission de votre adresse IP à Google lors de l'affichage des pages.</p>
        </section>
        <section>
          <h2>Médiation de la consommation</h2>
          <p>Conformément aux articles L.611-1 et suivants du Code de la consommation, en cas de litige non résolu à l'amiable, le client consommateur peut recourir gratuitement au médiateur de la consommation suivant : {info('mediateur')}.</p>
        </section>
        <section>
          <h2>Responsabilité</h2>
          <p>Les informations présentées sur ce site sont fournies à titre indicatif et peuvent évoluer. Seul le devis remis avant chaque intervention fait foi quant au contenu et au prix des prestations.</p>
        </section>
      </div>
    </div>
  </section>
</main>
"""
    return tete("mentions-legales.html", "Mentions légales · Maison BRB", "Mentions légales du site Maison BRB : éditeur, hébergement, données personnelles et médiation de la consommation.", robots="noindex, follow") + entete("mentions-legales.html") + corps + pied()


def page_404():
    corps = f"""<main id="contenu">
  <section class="hero">
    <div class="wrap">
      <img class="mono" src="assets/monogramme-or.svg" alt="" width="240" height="159" style="width:min(240px,60vw)">
      <h1>PAGE INTROUVABLE</h1>
      <div class="tri" aria-hidden="true"><i></i><i></i><i></i></div>
      <p class="lead">La page demandée n'existe pas ou a été déplacée.</p>
      <div class="btns"><a class="btn" href="index.html">Retour à l'accueil</a><a class="btn solid" href="tel:{INFOS['tel_intl']}">Appeler · {INFOS['tel']}</a></div>
    </div>
  </section>
</main>
"""
    # Chemins absolus : la page 404 peut être servie depuis n'importe quelle URL.
    html = tete("404.html", "Page introuvable · Maison BRB", "Cette page n'existe pas.", robots="noindex") + entete("") + corps + pied()
    return html.replace('href="assets/', 'href="/assets/').replace('src="assets/', 'src="/assets/').replace('href="index.html', 'href="/').replace('href="brb-', 'href="/brb-').replace('href="beaucaire-', 'href="/beaucaire-').replace('href="mentions-', 'href="/mentions-')


def sitemap():
    pages = ["index.html"] + [a["page"] for a in ACTIVITES]
    urls = "\n".join(
        f"  <url><loc>{url(p)}</loc><priority>{'1.0' if p == 'index.html' else '0.8'}</priority></url>" for p in pages
    )
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n'


def main():
    fichiers = {
        "index.html": page_accueil(),
        "mentions-legales.html": page_mentions(),
        "404.html": page_404(),
        "robots.txt": "User-agent: *\nAllow: /\n" + (f"\nSitemap: {domaine()}/sitemap.xml\n" if domaine() else ""),
    }
    # Le plan du site exige des adresses absolues : il n'est produit qu'une fois le domaine connu.
    if domaine():
        fichiers["sitemap.xml"] = sitemap()
    else:
        (RACINE / "sitemap.xml").unlink(missing_ok=True)
    for a in ACTIVITES:
        fichiers[a["page"]] = page_activite(a)
    for nom, contenu in fichiers.items():
        (RACINE / nom).write_text(contenu, encoding="utf-8")
        print("écrit :", nom)
    manquants = [k for k, v in INFOS.items() if not v]
    if manquants:
        print("\nÀ compléter dans INFOS avant la mise en ligne :", ", ".join(manquants))


if __name__ == "__main__":
    main()
