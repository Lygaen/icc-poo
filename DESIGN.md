# DESIGN


## Analyse des performances :
### génération d'une carte en fonction de n, la taille de la carte en nombre de "cellules":
on parcourt chaque "cellule" de la carte pour y lire le caractère associé, et entre autres opérations en thêta(1), on appelle sur les blocs qui peuvent faire partie d'une plateforme la fonction \_\_init\_\_ de la class Path.

Cette fonction utilise Path.group, qui est en $\theta(n)$ (en vérité $\theta$ du nombre de blocs du groupe dans lequel le bloc est, donc plus petit que n), et ensuite itère sur le groupe du blocs et les directions ($\theta(4n)$), puis sur les directions et la longueur de la liste de déplacement trouvée ($\theta(4n)$, les flèches sont dans la map), ce qui nous donne au final du $\theta(9n)$ = $\theta(n)$.

On a donc au final une génération de map en $\theta(n^2)$.
### la fonction update en fonction de k, le nombre d'entités (GameObject) présentes:
Pour chacun de ces objets, on va appeler leur fonction update, qui sont au plus en $\theta(k)$ (pour vérifier les collisions potentielles avec les $k-1$ autres entités), ce qui nous donne au final une fonction en $\theta(k^2)$.