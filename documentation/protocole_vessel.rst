Vaisseau
--------

Les commandes de vaisseau ne sont pas actives tant que le jeu n'a pas démarré.
Le démarrage est signalé par le messge `start_battle` sans donnée, message
répété à la connexion si elle intervient en milieu de partie.

En cas de victoire, le message `won` est envoyé sans donnée avant la
déconnexion.

autodestruction
"""""""""""""""

Réalise l'autodestruction immédiate du vaisseau.

JSON-schema
'''''''''''

.. code-block::

  {
      "properties": {
          "type": {
              "const": "autodestruction"
          },
      },
      "required": ["type"],
      "additionalProperties": False
  }

Example
'''''''

.. code-block::

  > {"type": "autodestruction"} 
  CLOSED 1000 Vessel destroyed 
