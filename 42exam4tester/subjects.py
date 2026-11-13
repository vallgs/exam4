"""Énoncés (résumés) des exercices, affichés en mode exam."""

SUBJECTS = {
    "array_rotation_detector": """\
Fichier à rendre : py_array_rotation_detector.py
Interdit         : collections.deque.rotate()

Écrire une fonction qui détermine si arr2 est une rotation (gauche ou droite)
de arr1. Une rotation décale les éléments de façon circulaire :
[1, 2, 3] décalé d'un cran vers la droite donne [3, 1, 2].

- Retourne True si arr2 est une rotation de arr1, False sinon.
- Des listes de longueurs différentes ne sont jamais des rotations.
- Deux listes vides sont des rotations l'une de l'autre.

def array_rotation_detector(arr1: list, arr2: list) -> bool:

Exemples :
  array_rotation_detector([1, 2, 3, 4, 5], [4, 5, 1, 2, 3])  -> True
  array_rotation_detector([1, 2, 3, 4, 5], [5, 1, 2, 3, 4])  -> True
  array_rotation_detector([1, 2, 3], [3, 2, 1])              -> False
  array_rotation_detector([1, 2], [1, 2, 3])                 -> False
  array_rotation_detector([], [])                            -> True
""",
    "constellation_mapper": """\
Fichier à rendre : py_constellation_mapper.py
Autorisé         : aucune fonction (pas d'import)

Écrire une fonction qui place des étoiles sur une grille carrée dim x dim
et retourne la grille sous forme de liste de chaînes.

- stars : liste de coordonnées (ligne, colonne), (0, 0) en haut à gauche.
- Une étoile s'affiche '*', une case vide '.'.
- Les coordonnées hors de la grille sont ignorées.
- Les doublons n'apparaissent qu'une fois.

def constellation_mapper(stars: list[tuple[int, int]], dim: int) -> list[str]:

Exemples :
  constellation_mapper([(0, 0), (1, 1), (2, 2)], 3)                  -> ['*..', '.*.', '..*']
  constellation_mapper([(1, 1), (0, 1), (2, 1), (1, 0), (1, 2)], 3)  -> ['.*.', '***', '.*.']
  constellation_mapper([], 2)                                        -> ['..', '..']
  constellation_mapper([(0, 0), (0, 0), (1, 1)], 2)                  -> ['*.', '.*']
  constellation_mapper([(0, 0), (5, 5)], 3)                          -> ['*..', '...', '...']
  constellation_mapper([(1, 0), (1, 1), (1, 2)], 3)                  -> ['...', '***', '...']
""",
    "list_intersection_finder": """\
Fichier à rendre : py_list_intersection_finder.py
Autorisé         : aucune fonction (pas d'import)

Écrire une fonction qui calcule l'intersection de plusieurs listes triées :
les éléments présents dans TOUTES les listes.

- Résultat trié par ordre croissant, sans doublons.
- Entrée vide -> [] ; si une des listes est vide -> [].

def list_intersection_finder(lists: list[list[int]]) -> list[int]:

Exemples :
  list_intersection_finder([[1, 2, 3], [2, 3, 4], [2, 3, 5]])           -> [2, 3]
  list_intersection_finder([[1, 2, 3, 4], [2, 4, 6, 8], [4, 8, 12]])    -> [4]
  list_intersection_finder([[1, 1, 2, 3], [1, 2, 2, 3], [1, 2, 3, 3]])  -> [1, 2, 3]
  list_intersection_finder([[1, 2, 3], [4, 5, 6]])                      -> []
  list_intersection_finder([])                                          -> []
  list_intersection_finder([[1, 2, 3], []])                             -> []
  list_intersection_finder([[5]])                                       -> [5]
""",
    "merge_sorted_lists": """\
Fichier à rendre : py_merge_sorted_lists.py
Interdit         : sorted(), .sort(), heapq.merge()

Écrire une fonction qui fusionne plusieurs listes d'entiers triées en une
seule liste triée (ordre croissant), de façon efficace.

- Les listes d'entrée sont triées par ordre croissant.
- Les doublons sont tous conservés ; les nombres négatifs sont gérés.
- Les listes vides sont ignorées ; entrée vide -> [].
- Une seule liste en entrée -> une COPIE de cette liste.
- Doit rester efficace sur de grosses entrées.

def merge_sorted_lists(lists: list[list[int]]) -> list[int]:

Exemples :
  merge_sorted_lists([[1, 3, 5], [2, 4, 6]])           -> [1, 2, 3, 4, 5, 6]
  merge_sorted_lists([[1, 5, 9], [2, 3, 8], [4, 6, 7]]) -> [1, 2, 3, 4, 5, 6, 7, 8, 9]
  merge_sorted_lists([[5], [1, 3], [2, 4]])            -> [1, 2, 3, 4, 5]
  merge_sorted_lists([[1, 1, 2], [2, 3, 3]])           -> [1, 1, 2, 2, 3, 3]
  merge_sorted_lists([[], [1, 2, 3]])                  -> [1, 2, 3]
  merge_sorted_lists([[]])                             -> []
  merge_sorted_lists([[-5, -1, 0], [-3, 2, 4]])        -> [-5, -3, -1, 0, 2, 4]
  merge_sorted_lists([[10], [10], [10]])               -> [10, 10, 10]
""",
    "palindrome_partitioner": """\
Fichier à rendre : py_palindrome_partitioner.py
Autorisé         : aucune fonction (pas d'import)

Étant donné une chaîne s, trouver le nombre minimum de coupes nécessaires
pour la découper en morceaux qui sont tous des palindromes.
Avec c coupes, on obtient c + 1 morceaux.

- Chaîne vide ou de longueur 1 -> 0.
- Chaîne déjà palindrome -> 0.
- Pire cas (tous les caractères différents) -> len(s) - 1.

def palindrome_partitioner(s: str) -> int:

Exemples :
  palindrome_partitioner("aab") -> 1
  palindrome_partitioner("aba") -> 0
  palindrome_partitioner("abc") -> 2
""",
    "package_dependency_resolver": """\
Fichier à rendre : py_package_dependency_resolver.py
Interdit         : graphlib.TopologicalSorter

Écrire une fonction qui donne un ordre d'installation valide de paquets
(dépendances d'abord) par tri topologique (ex. algorithme de Kahn).

- packages : dict {nom_du_paquet: [dépendances]}.
- Retourne les paquets dans l'ordre d'installation.
- Dépendance circulaire (y compris un paquet qui dépend de lui-même) -> [].
- Entrée vide -> [].
- Les dépendances absentes du dictionnaire sont ignorées.
- Sortie déterministe : quand plusieurs paquets sont prêts, on les traite
  par ordre alphabétique.

def package_dependency_resolver(packages: dict[str, list[str]]) -> list[str]:

Exemples :
  package_dependency_resolver({"app": ["database"], "database": ["driver"], "driver": []})
      -> ["driver", "database", "app"]
  package_dependency_resolver({"A": [], "B": ["A"], "C": ["A", "B"]})  -> ["A", "B", "C"]
  package_dependency_resolver({})                                     -> []
  package_dependency_resolver({"X": ["Y"], "Y": ["X"]})               -> []
  package_dependency_resolver({"web": [], "api": [], "frontend": ["web"], "backend": ["api"]})
      -> ["api", "web", "backend", "frontend"]
""",
    "sliding_window_maximum": """\
Fichier à rendre : py_sliding_window_maximum.py
Autorisé         : aucune fonction (pas d'import)

Écrire une fonction qui fait glisser une fenêtre de taille k sur la liste
et retourne le maximum de chaque position de la fenêtre.

- Liste vide, k <= 0 ou k > len(nums) -> [].

def sliding_window_maximum(nums: list[int], k: int) -> list[int]:

Exemples :
  sliding_window_maximum([1, 3, -1, -3, 5, 3, 6, 7], 3) -> [3, 3, 5, 5, 6, 7]
  sliding_window_maximum([1, 2, 3, 4, 5], 2)            -> [2, 3, 4, 5]
  sliding_window_maximum([5, 4, 3, 2, 1], 1)            -> [5, 4, 3, 2, 1]
  sliding_window_maximum([1, 2, 3], 3)                  -> [3]
  sliding_window_maximum([1, 2, 3], 4)                  -> []
  sliding_window_maximum([], 2)                         -> []
  sliding_window_maximum([1, 2, 3], 0)                  -> []
""",
}
