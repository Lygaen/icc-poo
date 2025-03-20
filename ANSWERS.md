# ANSWERS
## Semaine 1
> Aucune question cette semaine...

## Semaine 2
> Comment avez-vous conçu la lecture du fichier ? Comment l’avez-vous structurée de sorte à pouvoir la tester de manière efficace ?
La lecture du fichier se fait dans la classe `map`. La lecture se fait en 3 parties :
- Tout d'abord, `reload()` est appelé, lis le fichier dans son entiereté et le place dans un buffer. Le buffer est séparé en deux selon le premier "`---`", en header et en map.
- Ensuite, `parse_header` est appelé, lisant les différentes variables à partir du string. Il retourne une classe `Metadata` qui contient les différentes informations
- Ensuite `parse_map` est appelé, lisant la 2ème partie du buffer, obtenant les informations variés de `Metadata` passé en argument et ajoute le tout à `self`.

Ainsi, la séparation entre les différentes étapes de chargement de la map ont permis à tester efficacement le code, en particulier en le séparant.

> Comment avez-vous adapté vos tests existants au fait que la carte ne soit plus la même qu’au départ ? Est-ce que vos tests résisteront à d’autres changements dans le futur ? Si oui, pourquoi ? Si non, que pensez-vous faire plus tard ?

Nos tests sont désormais isolés, s'attaquant chacun à une fonctionnalité différente. Ainsi, ils résisteront aux changement futurs.
Au besoin futurs d'ajouter d'autres fonctionnalités, il suffirat d'ajouter de nouveau fichier tests.
Dû à la charge de travail, seulement quelques tests ont pû être ajouté cette semaine.

De plus, la technique ancestrale de "lancer le jeu" est particulièrement efficace pour un début de projet comme celui-ci.

> Le code qui gère la lave ressemble-t-il plus à celui de l’herbe, des pièces, ou des blobs ? Expliquez votre réponse.
Nous avons mis en place un système de classe abstraite : le `GameObject`. Cela se fait ainsi :
- `GameView` gère l'HID, etc.
- `Map` contient plusieurs `GameObject`
- Chaque `GameObject` contient la logique interne de l'entité (mouvement, dégâts, etc.)

Ce fonctionnement permet d'isoler la fonctionnalité, notamment celles entre les entités. En particulier, du code utilitaire peut-être ajouté dans les `GameObjects`.

Pour des données partagées (joueur principal, score, ...) les `GameObject` ont accès à une réference de la `Map` qui elle a une réference de `GameView`. Ainsi, cela permet de sauvgarder des données qui dépendent des niveaux (ex. niveau suivant) et des données générales sur le jeu (ex. score, ...).

Ainsi, le code pour l'herbe ressemble celui des pièces et des blobs dans la mesure où ils sont des `GameObjects`. Après, le code pour les pièces ressemble plus celui des blobs dans la mesure où ils vérifient les collisions avec le joueur pour l'un, les autres GOs pour l'autre.

Chaque GO à pour fonction `#on_damage(#DamageSource, #float)` qu'il peut implémenter pour autoriser son entité à recevoir des dégâts. De cette façon, les blobs traversent les `GameObject`, appelant `#on_damage` dessus avec pour source `MONSTER`. Les dégâts sont multipliés par `delta_time` afin de permettre des dégâts consistant, quel que soit le framerate.

Les pièces elles, ne se vérifient que face au joueur pour vérifier si elle sont rentrés en collision.

L'herbe ne fait rien.

> Comment détectez-vous les conditions dans lesquelles les blobs doivent changer de direction ?

Les blobs contiennent une fonction `check_collision_direction` qui vérifient une collision dans une direction donnée.
Celle-ci instantie une sphère de rayon 1 à l'endroit calculé de la direction.

Les directions possibles sont :
- Devant le blob (y'a-t-il une caisse devant lui ?)
- Devant, en diagonale descendante (y'a-t-il du vide devant ?)

En fonction du résultat de ces 2 checks, le slime fait demi-tour ou continue d'avancer.

Ainsi `check_collision_direction` utilise `change_x` en interne pour savoir la direction dans lequel le blob se déplace.

## Semaine 3
> Quelles formules utilisez-vous exactement pour l’épée ? Comment passez-vous des coordonnées écran aux coordonnées monde ?
Les formules utilisés sont les suivantes, en pseudo-code

```python
direction = player_position - unproject(mouse_position)
direction = direction.normalize()

angle = math.asin(dir.x) - (pi / 4)

if dir.y < 0:
    angle = -angle + (pi / 2)
sword.radians = angle
```

Ainsi, les seules formules sont :
- `unproject` qui transforme les coordonées d'écran en coordonées du monde, selon notre caméra principale
- `normalize` qui change notre vecteur position en vecteur unitaire
- `asin(...) - pi/4` qui calcule l'angle en radians

> Comment testez-vous l’épée ? Comment testez-vous que son orientation est importante pour déterminer si elle touche un monstre ?
L'épée appelle `on_damage` sur les `GameObjects` avec lesquels elle rentre en contact.

Cette fonction est appelée avec `DamageSource.PLAYER` en argument, et ainsi les `GameObject` voulant prendre des dégâts de la part de l'épée peuvent implémenter la-dite fonction, vérifiant le `DamageSource`.

La rotation se faisant au niveau du sprite, `arcade.check_collision` effectue en interne la rotation de la boîte de collision, aucun code supplémentaire n'a été ajouté à ce niveau là.

> Comment transférez-vous le score de la joueuse d’un niveau à l’autre ?
Le score de la joueuse est sauvegardé dans le `GameView`, ce qui permet, au rechargement d'une nouvelle map, de le garder tel qu'il était.

> Où le remettez-vous à zéro ? Avez-vous du code dupliqué entre les cas où la joueuse perd parce qu’elle a touché un ou monstre ou de la lave ?
Le score de la joueuse est remis à zéro lors de sa mort. En particulier, quand elle reçoit des dégâts qui dépassent ses point de vie actuels.

Dans `on_damage`, `Player#HP` est décrementé, jusque atteindre `HP <= 0` ce qui réinitialise la map actuelle, et le score.

Dans cette même fonction, si le dégâts provient de la lave plutôt que du monstre, `HP` est directement mis à zéro, ce qui déclenche la réinitialisation.

Il n'y a donc pas de code dupliqué entre la lave et le monstre.

> Comment modélisez-vous la “next-map” ? Où la stockez-vous, et comment la traitez-vous quand la joueuse atteint le point E ?
L'argument `next-map` est sauvegardé dans les `Metadata` lors du chargement de la map. Lorsque celle-ci est construite, une `GameObject` spécial de type `Exit` est construit, prenant `next-map` comme argument.

Lorsque ce GO est touché, il charge la prochaine map en appelant `Map#change_maps` avec le chemin relatif en question.

Le chemin est donc stocké dans le sprite de sortie, ce qui permettra à terme d'avoir plusieurs chemins possibles.

> Que se passe-t-il si la joueuse atteint le E mais la carte n’a pas de next-map ?
Au moment de la construction de la map, si la map ne contient pas de `Metadata#next_map` mais contient une sortie, une erreur est soulevée.

Cette erreur permet de régler les oublis accidentels des modifications de la map qui ont rajouté une sortie sans spécifier où est-ce qu'elle allait.

Ce cas où la joueuse attendrait une sortie sans `next-map` est donc impossible par design.

## Semaine 4
> Quelles formules utilisez-vous exactement pour l’arc et les flèches ?
L'arc fait apparaître une flèche au moment du clic, cette flèche est un `GameObject` à part entière. Cette flèche, à chaque `update`, se fait retirer de la vitesse verticale.

Finalement, à partir d'un temps variable, la flèche disparait.

Ainsi la formule en question est :
```
Vitesse_y -= GRAVITE * delta_time
```

Où `delta_time` est le temps entre deux frames, afin que le jeu soit consistant quelque soit les FPS.

> Quelles formules utilisez-vous exactement pour le déplacement des chauves-souris (champ d’action, changements de direction, etc.) ?
La chauve-souris se déplace librement dans un cercle centré autour de son point d'apparition.

Elle a sa vitess en coordonées polaires. Ainsi, cela permet des petites corrections (en utilisant le module `random`) à l'angle sans que cela change radicalement son orientation. La norme de la vitesse, elle, reste inchangée.

Lorsque la chauve-souris s'apprête à sortir du cercle, elle effectue un demi-tour afin de pouvoir re-rentrer dedans. Ainsi, les seules demi-tours que la chauve-souris effectue sont dans les cas limites où la chauve-souris pourrait partir trop loin de son point d'apparition.

Ces 2 effets combinés permettent à la chauve-souris de se déplacer de façon plausible. Elle ne rentre pas en collision avec le reste de la map comme demandé.

> Comment avez-vous structuré votre programme pour que les flèches puissent poursuivre leur vol ?
Grâce au système de `GameObject`, il suffit d'ajouter les flèches à la scène actuelle pour qu'elle deviennent indépendantes.

Ensuite, lors d'une collision, la flèche nullifie sa vitesse et applique des dégâts si applicable. Ainsi le système de flèches devient indépendant de l'arc une fois apparût.

> Comment gérez-vous le fait que vous avez maintenant deux types de monstres, et deux types d’armes ? Comment faites-vous pour ne pas dupliquer du code entre ceux-ci ?
En plus système de `GameObject`, les armes et les monstres héritent respectivement d'une classe `Weapon` et `Monster`.

Cela permet, pour le premier, d'obtenir une abstraction pour les différentes armes qui est instantiable dans la classe `Player`. Elle permet aussi d'orienter automatiquement les armes aux côtés du joueur afin d'éviter la duplication de ce code là.

Pour `Monster`, cela permet d'avoir des fonctions utiles telle que `check_collision`, gérer le système de PV, gérer les dégâts etc.
Ainsi, le seul code présent dans les classe intantiant `Weapon` et `Monster` sont des fonctionnalités spécifiques aux-dites classes.
