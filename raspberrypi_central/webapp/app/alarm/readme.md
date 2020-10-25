J'ai deux solutions pour créer des mode de surveillance.
Soit je mets la logique dans l'application smart-camera, soit je la met dans webapp.

A savoir que, une ROI peut être en mode watch only tandis qu'une auture zone peut être en surveillance.
Si je le fais sur smart-camera, ça implique d'ajouter une donnée supplémentaire par ROI ou générale, un boolean surveillance ou quelque chose du style.

Mais en vrai... Qui prend la décision de broadcaster aux autres IoT la data qui dit de sonner et/ou d'allumer les lumières ect... ?
C'est l'application web!

La caméra n'a pas à savoir si c'est du watch only ou surveillance ou que sais-je encore...
Elle détecte quelqu'un ou non dans une ROI, et envoie cette data à l'application principale.

Ensuite, l'application principale récupère cette donnée, et agis en conséquence:
- surveillance? Active la scène de sécurité: sonnerie, lumières, message...
- watch only? Notification pour certains utilisateurs si configuré ainsi ect.


J'ai désormais besoin d'ajouter cette data lorsque smart-camera publie qu'il y a de la motion:
- où la motion a été détectée ? La ROI: n'envoyer que l'identifiant et le type de ROI (rectangle pour le moment)
