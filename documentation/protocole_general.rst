Généralités
-----------

La communication s'effectue en échangeant des messages JSON sur une liaison
websocket à l'adresse `/ws` du serveur. Les messages entrant et sortant sont
indépendants dans le temps et il n'y a pas d'ordre imposé, même si certains
messages déclenchent une réponse du serveur. Le serveur peut aussi générer des
messages spontannés selon les actions des autres équipes.

En cas d'erreur, la connexion est fermée par le serveur. La raison est indiquée
dans la raison du message de fermeture. En cas de message invalide, un message
`invalid_msg` peut être envoyé pour préciser l'erreur.

Les messages sont des objets JSON, avec une clé `type` précisant le type de
message et d'éventuelles paires clé/valeur différentes additionnelles selon les
types.

Les commandes des administrateurs ne sont pas documentées.


À la connexion au websocket, le serveur envoie un message de type `hello` sans
donnée.
