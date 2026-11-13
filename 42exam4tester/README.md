# exam4tester

Testeur pour les 7 exercices Python de l'exam rank 04 (https://rank04.42exam.net/).

## Utilisation

```bash
uv run tester.py                                  # liste les exercices
uv run tester.py mes_exos/py_merge_sorted_lists.py
uv run tester.py mes_exos/                        # teste tous les py_*.py reconnus
uv run tester.py solution.py --exo palindrome_partitioner
uv run tester.py mes_exos/ --seed 42 -v           # seed fixe, tous les échecs affichés
```

L'exercice est détecté depuis le nom du fichier (`py_<nom>.py` ou `<nom>.py`),
sinon depuis le nom de la fonction définie dedans.

## Ce qui est vérifié pour chaque exo

1. **Fonctions interdites** (analyse AST), d'après le site :
   - `array_rotation_detector` : `deque.rotate()`
   - `merge_sorted_lists` : `sorted()`, `.sort()`, `heapq.merge()` (alias `import heapq as h` compris)
   - `package_dependency_resolver` : `graphlib.TopologicalSorter`
   - `constellation_mapper`, `list_intersection_finder`, `palindrome_partitioner`,
     `sliding_window_maximum` : « Allowed functions: None » → **aucun import** accepté
     (les builtins comme `len`, `range`, `max`, `set`, `sorted` restent permis)
2. **Import** du fichier, présence de la fonction et nombre de paramètres.
3. **Exemples du sujet** (sortie exacte, type compris).
4. **Cas limites** écrits à la main (vides, négatifs, doublons, cycles, k <= 0…).
5. **300 tests aléatoires** comparés à une solution de référence.
6. **Performance** (merge, palindrome, resolver, sliding window) avec timeout.

Pour chaque appel, le testeur vérifie aussi que la fonction ne modifie pas ses
arguments, ne renvoie pas une liste d'entrée au lieu d'une copie, et n'affiche rien.

Code de sortie : 0 si tout passe, 1 sinon.

## Note sur `package_dependency_resolver`

Le sujet demande un ordre « alphabétique quand il y a le choix ». L'exemple
`{"web": [], "api": [], "frontend": ["web"], "backend": ["api"]}` → `["api", "web", "backend", "frontend"]`
exclut la version avec min-heap. Sont acceptés : Kahn avec une file FIFO initialisée
triée, ou Kahn par niveaux (chaque vague triée).

## Mode exam

```bash
uv run exam.py           # démarre ou reprend l'exam
uv run exam.py --reset   # recommence de zéro (efface exam/, rendus compris)
```

Un exo est tiré au hasard dans ton niveau (1 à 4). Le sujet est affiché et
écrit dans `exam/subjects/`, et un fichier vide `exam/rendu/py_<exo>.py` est
créé : tu le remplis, puis tu tapes `grademe`. Tant que l'exo n'est pas réussi,
tu restes dessus (les traces des tests ratés sont affichées). Une fois réussi,
tu passes au niveau suivant.

Commandes : `grademe` (g), `subject` (s), `status`, `help` (h), `quit` (q).
La progression est sauvegardée : `quit` ou Ctrl+C met en pause, relancer reprend.
