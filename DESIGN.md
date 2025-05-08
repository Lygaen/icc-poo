# DESIGN


Analyse des performances :
    génération d'une carte en fonction de n, la taille de la carte en nombre de "cellules":
        on parcourt chaque "cellule" de la carte pour y lire le caractère associé, et entre autres opérations en thêta(1), on appelle sur les blocs qui peuvent faire partie d'une plateforme la fonction __init__ de la class Path.
        cette fonction utilise Path.group, qui est en thêta(n) (en vrai thêta du nombre de blocs du groupe dans lequel le bloc est, donc plus petit que n), et ensuite itère sur le groupe du blocs et les directions (4n), puis sur les directions et la longueur de la liste de déplacement trouvée (4n, les flèches sont dans la map), ce qui nous donne au final du thêta(9n) = thêta(n)
        on a donc au final une génération de map en thâta(n^2)
    la fonction update en fonction de k, le nombre d'entités (GameObject) présentes:
        pour chacun de ces objets, on va oappeler leur fonction update, qui sont au plus en thêta(k) (pour vérifier les collisions potentielles avec les k-1 autres entités), ce qui nous donne au final une fonction en thêta(k^2)