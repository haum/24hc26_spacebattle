Idée
----

Les participants vont s'affronter dans un univers où ils pilotent des vaisseaux
spaciaux. À eux de se fabriquer leur cockpit et leurs outils pour naviguer et
exploser les vaisseaux adverses, de manière manuelle, semi-automatisée ou
totalement automatisée.

Idées en vrac :

- Le monde est un tore/hypertore

  - D'abord 2D, puis 3D, puis 4D
  - Les coordonnées sont en relatif par rapport à la position actuelle du
    vaisseau
  - Les éléments de jeu sont sur une grille à coordonnées entières

- Ils dialoguent avec un serveur en websocket

  - les commandes sont envoyées via ce canal
  - les notifications du serveur passent par ce canal
  - commandes et notifications n'ont pas de relation temporelle

- Les radars ont des précisions différentes selon la portée

  - très précis à courte portée

  - blocks de 8^n plus loin, etc.

- Le vaisseau a des HP

- Les vaisseaux sont identifiés par des ID et ID d'équipe

- Plusieurs types d'armes ont des portées, dégâts et temps de recharge
  différents

  - les vaisseaux peuvent aussi poser des mines et savoir quand elles explosent

- Des asteroides peuvent infliger des dégâts

- Certaines actions révèlent la position

  - Tirer est vu par les radars avec plus ou moins de prévision

  - Une détonation de mine est détectée par les vaisseaux

  - Recharger à fond toutes ses ressources révèle la position exacte à tout le
    monde

- Stock initial de ressource de construction pour équiper leur vaisseau

  - pour choisir entre vitesse, HP, dégâts

- Ils ont des requêtes limitées

  - s'ils en font plus, ils infligent des dégâts à leur vaisseau

- Les déplacements relatifs sont connus par tous, mais à eux de corréler à
  d'autres informations pour pouvoir utiliser l'info.


Idées techniques:

- Avoir une clé admin pour recevoir toutes les notifications

- Utiliser aiohttp et asyncio

- un kd-tree pour stocker les éléments du jeu?

- Une adresse de websocket unique avec un premier message pour se connecter à
  un vaisseau.
