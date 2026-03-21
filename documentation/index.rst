Bienvenue aux 24 heures du Code 2026 !

Ce sujet est proposé par l'association HAUM_, hackerspace au Mans, un groupe de
bidouilleurs multidisciplinaires ouvert au partage de connaissances. N'hésitez
pas à nous rejoindre si vous êtes du coin et à venir discuter de manière
générale.

.. figure:: _static/illustration.jpg
    :align: center
    
    Marabunta - Bataille spatiale

Il y a 8 ans, aux 24 heures du Code, des étudiants programmaient des hordes de
fourmis numériques.
Depuis, la simulation s’est emballée et les fourmis s’affrontent désormais dans
des batailles épiques à bord de vaisseaux spatiaux.
Prenez les commandes de ces armadas et venez à bout des équipes concurrentes.

Ne soyez pas l’équipe qui code le mieux, soyez celle dont les programmes
apporteront un avantage dans la bataille.
Vos idées et leur mise en œuvre feront la différence.
À vous de créer les outils de commande, de visualisation, d’assistance, d’automatisation, de communication… pour arriver à vos fins.

.. _HAUM: https://haum.org/

Vue d'ensemble
==============

Vos programmes communiquent avec un serveur de jeu, en envoyant des commandes et
recevant quelques informations sur l'environnement.

L'univers est un **tore** (une grille dont les bords se rejoignent) : sortir
d'un côté vous fait réapparaître de l'autre. Les coordonnées que vous recevez
sont toujours **relatives** à la position de votre vaisseau.

La partie se joue jusqu'à ce qu'il ne reste plus qu'une seule équipe en vie.

Un Conseil Diplomatique des Fourmis a lieu à la 42e minute de chaque heure. Il est
conseillé aux équipes d'y envoyer un émissaire.


Objets de l'univers
--------------------

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Objet
     - Description
   * - Vaisseau
     - Votre vaisseau ou celui d'un adversaire.
   * - Astéroïde
     - Obstacle indestructible. Tout vaisseau qui le percute est instantanément
       détruit. Stoppe les torpilles et les lasers.
   * - Torpille
     - Projectile se déplaçant à vitesse fixe. Inflige des dégâts au premier
       vaisseau touché.
   * - Mine
     - Explosive au contact (une fois armée). Inflige des dégâts et peut
       déclencher les mines voisines en chaîne.
   * - Ressource
     - Dépôt d'énergie récupérable en passant dessus.

.. _stats:

Statistiques des vaisseaux
---------------------------

Chaque vaisseau est défini par quatre statistiques, chacune de 0 à 9.
La somme cumulée de toutes les stats de votre flotte ne doit pas dépasser **25**.

.. list-table::
   :header-rows: 1
   :widths: 10 15 75

   * - Stat
     - Nom
     - Effet
   * - H
     - Points de vie
     - Détermine la résistance aux dégâts. Plus la valeur est haute, plus le
       vaisseau peut encaisser.
   * - A
     - Attaque / Portée
     - Augmente la portée des armes (torpille, laser, IEM).
   * - S
     - Vitesse
     - Augmente la distance maximale qui peut être parcourue à chaque commande
       de déplacement.
   * - R
     - Radar
     - Augmente le rayon de détection du radar actif et passif.

Il n'y a pas de bonne ou mauvaise répartition : à vous de choisir l'équilibre
qui correspond à votre stratégie.


Généralités sur le protocole
============================

Toutes les commandes que vous envoyez et tous les événements que vous recevez
transitent par un canal **WebSocket** sous forme de messages **JSON**. Les
messages entrant et sortant sont indépendants dans le temps et il n'y a pas
d'ordre imposé, même si certains messages déclenchent une réponse du serveur. Le
serveur peut aussi générer des messages spontannés selon les actions des autres
équipes.

En cas d'erreur, la connexion est fermée par le serveur. La raison est indiquée
dans la raison du message de fermeture. En cas de message invalide, un message
`invalid_msg` peut être envoyé pour préciser l'erreur.

Les messages sont des objets JSON, avec une clé `type` précisant le type de
message et d'éventuelles paires clé/valeur additionnelles selon les types.

Connexion et démarrage
=======================

Toutes les connexions se font sur le point d'accès WebSocket ``/ws`` du serveur.

Étape 1 — Hello
---------------

Dès la connexion, le serveur envoie automatiquement :

.. code-block::

   < {"type": "hello", "need_keys": True}

.. note::

   ``need_keys`` indique si les messages ``start`` et ``connect`` requièrent
   l'envoi de la clé d'équipe.

Étape 2 — Enregistrement de la flotte
---------------------------------------

Envoyez un message ``start`` pour créer votre flotte et placer vos vaisseaux
dans le lobby :

.. code-block::

   > {
       "type": "start",
       "team": "NomDeVotreEquipe",
       "key": "...",
       "vessels": [
           [H, A, S, R],
           [H, A, S, R],
           ...
       ]
     }

Le paramètre ``key`` avec pour valeur la clé d'équipe est requis seulement si le
message ``hello`` avait le paramètre ``need_keys`` à ``True``.

Chaque sous-tableau ``[H, A, S, R]`` décrit les statistiques d'un vaisseau
(voir la section :ref:`stats`). Le serveur répond avec les identifiants secrets
de vos vaisseaux :

.. code-block::

   < {"type": "new_vessels", "vessels": ["Equipe:1:xKpQa", "Equipe:2:mNrTs"]}

.. warning::

   Ces identifiants contiennent un token secret. **Ne les partagez pas.**

.. note::

   Si vous renvoyez un message ``start``, votre ancienne flotte est détruite.

Contraintes sur la flotte :

- De **1 à 6** vaisseaux.
- Chaque statistique est un entier entre **0 et 9**.
- La **somme totale** de toutes les statistiques de tous les vaisseaux ne doit
  pas dépasser **25**.


Étape 3 — Connexion à chaque vaisseau
--------------------------------------

Ouvrez **une connexion WebSocket par vaisseau** et envoyez :

.. code-block::

   > {"type": "connect", "id": "Equipe:1:xKpQa", "key": "..."}

Le paramètre ``key`` avec pour valeur la clé d'équipe est requis seulement si le
message ``hello`` avait le paramètre ``need_keys`` à ``True``.

.. note::

   Évidemment, adaptez l'``id`` avec les identifiants renvoyés par le message ``new_vessels``.

Le serveur répond avec les statistiques effectives du vaisseau :

.. code-block::

   < {"type": "stats", "stats": [H, A, S, R], "hp": 21}

Puis, lorsque la bataille commence (par exemple dès qu'au moins deux équipes
sont dans le lobby depuis 5 secondes en dehors des matchs officiels), le serveur
envoie :

.. code-block::

   < {"type": "start_battle"}

.. note::

   Si vous vous connectez à un vaisseau après le début d'une partie, le message
   ``start_battle`` est envoyé à la connexion pour vous informer que la partie
   est en cours.


Énergie
=======

Chaque vaisseau possède une **réserve d'énergie** (maximum : 100).
L'énergie se régénère automatiquement au fil du temps (4 unités par seconde).
Si vous n'avez pas assez d'énergie pour une action, le serveur envoie :

.. code-block::

   < {"type": "low_energy"}

.. note::

   Un petit dégât est infligé au vaisseau si vous demandez une action pour
   laquelle vous n'avez pas assez d'énergie.

Coût des actions :

.. list-table::
   :header-rows: 1
   :widths: 30 15

   * - Action
     - Coût
   * - ``move``
     - 5 (max, proportionnel à la distance)
   * - ``fire_torpedo``
     - 10
   * - ``drop_mine``
     - 10
   * - ``fire_iem``
     - 30
   * - ``fire_laser``
     - 50
   * - ``scan_radar``
     - 5

Lorsqu'un vaisseau est détruit, il laisse une **ressource** à sa position qui
peut être utilisée pour récupérer de l'énergie. En vous déplaçant sur cette
case, votre vaisseau récupère de l'énergie progresivement, jusqu'à épuisement
de la ressource.


Commandes du vaisseau
======================

Les commandes ne sont actives qu'une fois ``start_battle`` reçu.
Si votre vaisseau est sous l'effet d'une IEM, toute commande reçoit un message
de type ``iem_frozen``.

.. note::

   Un petit dégât est infligé au vaisseau si vous demandez une action alors que
   la partie n'est pas commencée ou que les systèmes du vaisseau ne sont pas
   encore rétablis après avoir reçu une IEM (signalée par un message de type
   ``iem_damage``).

move
----

Déplace le vaisseau dans une direction. La direction est un vecteur d'entiers
de la même dimension que l'univers.

.. code-block::

   > {"type": "move", "direction": [dx, dy]}
   > {"type": "move", "direction": [dx, dy, dz]}       (3D)
   > {"type": "move", "direction": [dx, dy, dz, dw]}   (4D)

Si deux vaisseaux entrent en collision, ils infligent chacun **15 dégâts** à l'autre.

.. note::

   La norme euclidienne du vecteur ne doit pas dépasser votre capacité de
   déplacement (déterminée par la stat **S**). Si le déplacement est trop
   grand, le serveur envoie un message de type ``move_aborded`` et un petit
   dégât est infligé au vaisseau.

.. note::

   Les autres vaisseaux reçoivent un signal ``passive_scan`` contenant votre
   déplacement s'ils sont à portée de radar.

fire_torpedo
------------

Tire une torpille dans la direction donnée.

.. code-block::

   > {"type": "fire_torpedo", "direction": [dx, dy]}

La torpille se déplace à chaque tick, inflige **20 dégâts** au premier vaisseau
touché, et est détruite par les astéroïdes et les mines.

drop_mine
---------

Pose une mine à votre position actuelle.

.. code-block::

   > {"type": "drop_mine", "delay": 3.0}

Le paramètre ``delay`` définit le temps en secondes avant que la
mine ne soit armée. Une mine détruite provoque une explosion qui peut faire
réagir les mines voisines en chaîne.

fire_laser
----------

Tire un rayon laser instantané dans la direction donnée.

.. code-block::

   > {"type": "fire_laser", "direction": [dx, dy]}

Le laser traverse les cellules en ligne droite jusqu'à la portée maximale
(déterminée par la stat **A**). Il inflige **20 dégâts** au premier vaisseau
touché et est stoppé par les astéroïdes, les ressources et les mines.

fire_iem
--------

Tire une impulsion électromagnétique (IEM) dans la direction donnée.

.. code-block::

   > {"type": "fire_iem", "direction": [dx, dy]}

L'IEM gèle **tous les vaisseaux** sur sa trajectoire pendant **5 secondes**.
La portée dépend de la stat **A** du vaisseau.

scan_radar
----------

Effectue un scan actif autour de votre vaisseau.

.. code-block::

   > {"type": "scan_radar"}

Pour chaque objet détecté dans votre rayon radar, vous recevez :

.. code-block::

   < {
       "type": "active_scan",
       "what": "vessel" | "asteroid" | "mine" | "torpedo" | "resource",
       "position": [dx, dy]
     }

Les positions sont **relatives** à votre vaisseau.
Si un même objet est visible plusieurs fois, seule la distance la plus courte
est indiquée.

.. note::

   Pour des raisons de performance, le radar utilise la norme Manhattan pour le rayon de
   détection, tandis que les déplacements utilisent la norme euclidienne.

autodestruction
---------------

Déclenche l'autodestruction immédiate du vaisseau.

.. code-block::

   > {"type": "autodestruction"}

Inflige **20 dégâts** à tous les vaisseaux et détruit les mines dans un rayon
de 5. La connexion WebSocket est fermée après.

broadcast
---------

Déclenche l'envoi d'un message de 128 caractères maximum broadcasté à tous les
vaisseaux dans un rayon équivalent au quart de la taille de l'univers. La
probabilité de recevoir le message diminue avec la distance. Tous les messages
indiquent la position relative entre le récepteur et l'émetteur. L'envoi d'un
message coûte 40 d'énergie et contient par défaut l'identifiant de l'émetteur.
Il est possible d'envoyer des messages de façon anonyme au double du prix.

.. code-block::

   >   { "type": "broadcast", "message": "...", "anonymous": true }

Le champ anonymous est optionnel (défaut false).

Événements reçus
================

Le serveur peut vous envoyer des messages à tout moment, indépendamment de vos
commandes.

damage
------

Votre vaisseau vient de subir des dégâts.

.. code-block::

   < {"type": "damage", "hp": 42}

``hp`` est votre niveau de vie actuel. Si ``hp`` atteint **0**, votre vaisseau
est détruit et la connexion fermée.

passive_scan
------------

Votre radar a détecté un événement à proximité.
Si un même évènement est visible plusieurs fois, seule la distance la plus
courte est indiquée.

.. code-block::

   < {"type": "passive_scan", "what": "explosion", "position": [dx, dy]}
   < {"type": "passive_scan", "what": "move", "vessel": "Equipe:3", "movement": [dx, dy]}

- ``explosion`` : une explosion s'est produite à cette position relative.
- ``move`` : un vaisseau (identifié par son nom d'équipe et numéro) s'est
  déplacé d'un certain vecteur. **La position absolue n'est pas fournie.**

resource_depleted
-----------------

Une ressource sur laquelle vous passiez vient d'être entièrement récupérée.

.. code-block::

   < {"type": "resource_depleted"}


iem_damage / iem_frozen
-----------------------

Votre vaisseau est gelé par une IEM et ne peut pas agir.

.. code-block::

   < {"type": "iem_damage"}   -- Vous venez de recevoir une IEM
   < {"type": "iem_frozen"}   -- Action impossible, gelé par IEM

low_energy
----------

Vous n'avez pas assez d'énergie pour effectuer l'action demandée.

.. code-block::

   < {"type": "low_energy"}

start_battle
------------

La bataille a commencé.

.. code-block::

   < {"type": "start_battle"}

broadcast
---------

Votre vaisseau a reçu un message envoyé par un autre vaisseau à portée.

.. code-block::

   < { "type": "broadcast", "message": "...", "position": [dx, dy], "emitter": "TeamA:1" }

Dans le cas où le message est envoyé anonymement, le champ emitter ne sera pas présent.

won / end
---------

La partie est terminée.

.. code-block::

   < {"type": "won"}   -- votre équipe a gagné
   < {"type": "end"}   -- partie terminée (vous avez perdu)

La connexion WebSocket est fermée juste après.


Ping-pong
=========

Disponible avant et pendant la partie, pour vérifier la connexion. Totalement
inutile, donc parfaitement indispensable.

.. code-block::

   > {"type": "ping"}
   > {"type": "ping", "n": 42}
   < {"type": "pong", "n": 42}
