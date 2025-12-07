Game
----

start
"""""

Crée une flotte de vaisseaux dans l'univers lobby.

Répond avec un message `new_vessels` contenant la liste des vaisseaux créés.

.. note::

   Si votre flotte est engagée dans un univers, tous ses vaisseaux sont détruits
   et de nouveaux vaisseaux sont créés dans le lobby.


JSON-schema
'''''''''''

.. code-block::

  {
      "properties": {
          "type": {
              "const": "start"
              },
          "team": {
              "type": "string"
              },
          "vessels": {
              "type": "array",
              "minItems": 1,
              "maxItems": MAX_VESSELS,
              "items": {
                  "type": "array",
                  "minItems": STAT_SZ,
                  "maxItems": STAT_SZ,
                  "items": {
                      "type": "integer",
                      "minimum": 0,
                      "maximum": MAX_STAT
                      }
                  }
              }
          },
      "required": ["type", "team", "vessels"],
      "additionalProperties": False
  }

.. note::

   De plus, la somme des statistiques de tous les vaisseaux ne doit pas dépasser
   MAX_RESOURCES

Exemple
'''''''

.. code-block::

  > {"type": "start", "team": "MyTeam", "vessels": [[1, 1, 1, 1], [1, 2, 3, 4]]} 
  < {"type": "new_vessels", "vessels": ["MyTeam:1:hAsxE", "MyTeam:2:uKNaQ"]} 


connect
"""""""

Connecte le websocket à un vaisseau créé par la commande `start`.

Répond avec un message `stats` contenant la configuration du vaisseau.


.. note::

  Si l'`id` ne correspond pas à un vaisseau ou que celui-ci a été détruit, la
  commande renvoie une erreur et déconnecte le websocket

JSON-schema
'''''''''''

.. code-block::

  {
      "properties": {
          "type": {
              "const": "connect"
          },
          "id": {
              "type": "string"
          },
          "required": ["type", "id"],
          "additionalProperties": False
      }
  }

Exemple
'''''''

.. code-block::

  > {"type": "connect", "id": "MyTeam:2:uKNaQ"} 
  < {"type": "stats", "hp": 1, "attack": 2, "speed": 3, "detection": 4} 


ping
""""

Envoie un ping au serveur, pour vérifier la connexion au niveau applicatif.

Répond avec un message `pong` contenant la valeur du paramètre `n`.


.. note::

  Cette commande fonctionne aussi pour un vaisseau.

JSON-schema
'''''''''''

.. code-block::

  {
    "properties": {
        "type": {
            "const": "ping"
        },
        "n": {
            "type": ["string", "number"]
        }
    },
    "required": ["type"],
    "additionalProperties": False
  }

Exemple
'''''''

.. code-block::

  > {"type": "ping", "n": 4} 
  < {"type": "pong", "n": 4}
