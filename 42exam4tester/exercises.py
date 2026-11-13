"""Définition des 7 exercices : référence, exemples du sujet, cas limites,
générateurs aléatoires, tests de performance et fonctions interdites."""

from dataclasses import dataclass, field
from typing import Callable


def default_check(args, got, expected):
    if type(got) is not type(expected) or got != expected:
        return f"obtenu {got!r}"[:300]
    return None


@dataclass
class Exercise:
    name: str
    level: int
    signature: str
    ref: Callable
    examples: list            # [(args_tuple, expected)]
    edge_cases: list          # [args_tuple] (attendu = ref)
    gen: Callable             # rng -> args_tuple
    n_random: int = 300
    perf: list = field(default_factory=list)   # [(rng -> args_tuple, timeout)]
    forbidden: list = field(default_factory=list)
    check: Callable = default_check
    timeout: float = 2.0

    @property
    def nargs(self) -> int:
        return self.ref.__code__.co_argcount


EXERCISES: dict[str, Exercise] = {}


def register(ex: Exercise) -> None:
    EXERCISES[ex.name] = ex


# ==========================================================================
# Level 1 — array_rotation_detector
# ==========================================================================

def ref_rotation(arr1, arr2):
    if len(arr1) != len(arr2):
        return False
    if not arr1:
        return True
    return any(arr1[i:] + arr1[:i] == arr2 for i in range(len(arr1)))


def gen_rotation(rng):
    n = rng.randint(0, 12)
    a = [rng.randint(0, rng.choice([2, 5, 50])) for _ in range(n)]
    mode = rng.random()
    if mode < 0.5 and n:
        k = rng.randint(0, n)
        return a, a[k:] + a[:k]
    b = a[:]
    if mode < 0.65 and n >= 2:
        i, j = rng.sample(range(n), 2)
        b[i], b[j] = b[j], b[i]
    elif mode < 0.75:
        b = b[::-1]
    elif mode < 0.85 and n:
        b[rng.randrange(n)] += 1
    elif mode < 0.92:
        b = b + [rng.randint(0, 5)]
    else:
        rng.shuffle(b)
    if n and rng.random() < 0.5:
        k = rng.randint(0, len(b))
        b = b[k:] + b[:k]
    return a, b


register(Exercise(
    name="array_rotation_detector",
    level=1,
    signature="def array_rotation_detector(arr1: list, arr2: list) -> bool:",
    ref=ref_rotation,
    examples=[
        (([1, 2, 3, 4, 5], [4, 5, 1, 2, 3]), True),
        (([1, 2, 3, 4, 5], [5, 1, 2, 3, 4]), True),
        (([1, 2, 3], [3, 2, 1]), False),
        (([1, 2], [1, 2, 3]), False),
        (([], []), True),
    ],
    edge_cases=[
        ([], [1]), ([1], []), ([1], [1]), ([1], [2]),
        ([1, 2, 3], [1, 2, 3]),            # rotation de 0
        ([1, 2, 3], [2, 3, 1]),            # rotation à gauche
        ([1, 2, 3], [3, 1, 2]),            # rotation à droite
        ([1, 1, 2], [1, 2, 1]), ([1, 1, 2], [2, 1, 1]), ([1, 1, 2], [1, 2, 2]),
        ([1, 2, 1, 2], [2, 1, 2, 1]), ([1, 2, 1, 2], [1, 1, 2, 2]),
        ([0, 0, 0], [0, 0, 0]), ([0, 0, 0], [0, 0]),
        ([1, 2, 3, 4], [1, 3, 2, 4]), ([1, 2, 3], [1, 2, 3, 1]),
        (["a", "b", "c"], ["c", "a", "b"]), (["a", "b", "c"], ["a", "c", "b"]),
        ([None, 0], [0, None]), ([1, "1"], ["1", 1]),
        ([-1, -2, -3], [-3, -1, -2]),
        ([1, 2, 3, 1, 2, 4], [1, 2, 4, 1, 2, 3]),
        ([1, 2, 3, 1, 2, 4], [1, 2, 3, 1, 2, 4][::-1]),
        (list(range(100)), list(range(37, 100)) + list(range(37))),
        (list(range(100)), list(range(37, 100)) + list(range(36))),
    ],
    gen=gen_rotation,
    forbidden=[".rotate"],
))


# ==========================================================================
# Level 1 — constellation_mapper
# ==========================================================================

def ref_constellation(stars, dim):
    grid = [["."] * dim for _ in range(dim)]
    for r, c in stars:
        if 0 <= r < dim and 0 <= c < dim:
            grid[r][c] = "*"
    return ["".join(row) for row in grid]


def gen_constellation(rng):
    dim = rng.randint(0, 8)
    stars = [(rng.randint(-3, dim + 2), rng.randint(-3, dim + 2))
             for _ in range(rng.randint(0, 12))]
    if stars and rng.random() < 0.3:
        stars.append(rng.choice(stars))
    return stars, dim


register(Exercise(
    name="constellation_mapper",
    level=1,
    signature="def constellation_mapper(stars: list[tuple[int, int]], dim: int) -> list[str]:",
    ref=ref_constellation,
    examples=[
        (([(0, 0), (1, 1), (2, 2)], 3), ["*..", ".*.", "..*"]),
        (([(1, 1), (0, 1), (2, 1), (1, 0), (1, 2)], 3), [".*.", "***", ".*."]),
        (([], 2), ["..", ".."]),
        (([(0, 0), (0, 0), (1, 1)], 2), ["*.", ".*"]),
        (([(0, 0), (5, 5)], 3), ["*..", "...", "..."]),
        (([(1, 0), (1, 1), (1, 2)], 3), ["...", "***", "..."]),
    ],
    edge_cases=[
        ([], 0), ([(0, 0)], 0), ([], 1), ([(0, 0)], 1), ([(1, 0)], 1), ([(0, 1)], 1),
        ([(0, 2)], 3),                     # (row, col) : pas (x, y)
        ([(2, 0)], 3),
        ([(-1, 0)], 2), ([(0, -1)], 2), ([(-1, -1)], 2),   # négatifs ignorés
        ([(3, 0), (0, 3), (3, 3)], 3),     # juste hors grille
        ([(0, 0)] * 5, 2),
        ([(r, c) for r in range(4) for c in range(4)], 4),
        ([(i, 9 - i) for i in range(10)], 10),
        ([(2, 2), (-3, -3), (100, 0)], 5),
    ],
    gen=gen_constellation,
    forbidden=["import:*"],   # sujet : "Allowed functions: None"
))


# ==========================================================================
# Level 2 — list_intersection_finder
# ==========================================================================

def ref_intersection(lists):
    if not lists:
        return []
    common = set(lists[0])
    for lst in lists[1:]:
        common &= set(lst)
    return sorted(common)


def gen_intersection(rng):
    lo, hi = rng.choice([(0, 6), (-5, 15), (-50, 50)])
    return ([sorted(rng.randint(lo, hi) for _ in range(rng.randint(0, 12)))
             for _ in range(rng.randint(0, 5))],)


register(Exercise(
    name="list_intersection_finder",
    level=2,
    signature="def list_intersection_finder(lists: list[list[int]]) -> list[int]:",
    ref=ref_intersection,
    examples=[
        (([[1, 2, 3], [2, 3, 4], [2, 3, 5]],), [2, 3]),
        (([[1, 2, 3, 4], [2, 4, 6, 8], [4, 8, 12]],), [4]),
        (([[1, 1, 2, 3], [1, 2, 2, 3], [1, 2, 3, 3]],), [1, 2, 3]),
        (([[1, 2, 3], [4, 5, 6]],), []),
        (([],), []),
        (([[1, 2, 3], []],), []),
        (([[5]],), [5]),
    ],
    edge_cases=[
        ([[]],), ([[], []],), ([[], [1]],), ([[1, 1, 1]],), ([[1, 1, 2, 2]],),
        ([[0]],), ([[1, 2], [1, 2]],), ([[1, 2, 3], [3], [1, 2, 3]],),
        ([[1, 2, 3], [2, 3], []],), ([[-3, -1, 0], [-3, 0, 2]],),
        ([[1, 2, 3, 4, 5], [5]],), ([[5], [1, 2, 3, 4, 5]],),
        ([[2, 2, 2], [2]],), ([[1, 3], [2, 4]],),
        ([list(range(100)), list(range(50, 150)), list(range(0, 200, 2))],),
    ],
    gen=gen_intersection,
    forbidden=["import:*"],   # sujet : "Allowed functions: None"
))


# ==========================================================================
# Level 2 — merge_sorted_lists
# ==========================================================================

def ref_merge(lists):
    return sorted(x for lst in lists for x in lst)


def gen_merge(rng):
    lo, hi = rng.choice([(0, 3), (-20, 20), (-1000, 1000)])
    return ([sorted(rng.randint(lo, hi) for _ in range(rng.randint(0, 10)))
             for _ in range(rng.randint(0, 8))],)


def perf_merge_two(rng):
    return ([sorted(rng.randint(-10**6, 10**6) for _ in range(20000)) for _ in range(2)],)


def perf_merge_many(rng):
    return ([sorted(rng.randint(-10**6, 10**6) for _ in range(100)) for _ in range(300)],)


register(Exercise(
    name="merge_sorted_lists",
    level=2,
    signature="def merge_sorted_lists(lists: list[list[int]]) -> list[int]:",
    ref=ref_merge,
    examples=[
        (([[1, 3, 5], [2, 4, 6]],), [1, 2, 3, 4, 5, 6]),
        (([[1, 5, 9], [2, 3, 8], [4, 6, 7]],), [1, 2, 3, 4, 5, 6, 7, 8, 9]),
        (([[5], [1, 3], [2, 4]],), [1, 2, 3, 4, 5]),
        (([[1, 1, 2], [2, 3, 3]],), [1, 1, 2, 2, 3, 3]),
        (([[], [1, 2, 3]],), [1, 2, 3]),
        (([[]],), []),
        (([[-5, -1, 0], [-3, 2, 4]],), [-5, -3, -1, 0, 2, 4]),
        (([[10], [10], [10]],), [10, 10, 10]),
    ],
    edge_cases=[
        ([],), ([[], []],), ([[], [], []],), ([[1, 2, 3]],), ([[-1]],), ([[0, 0, 0]],),
        ([[1], [], [0]],), ([[-5, -5], [-5]],), ([[1, 2], [3, 4]],), ([[3, 4], [1, 2]],),
        ([[1, 2, 3], []],), ([[], [], [7]],), ([[1, 10, 100], [2], [50, 60]],),
        ([[-10**9, 0, 10**9], [-1, 1]],), ([[i] for i in range(20, 0, -1)],),
        ([list(range(0, 50, 2)), list(range(1, 50, 2))],),
    ],
    gen=gen_merge,
    perf=[(perf_merge_two, 5.0), (perf_merge_many, 5.0)],
    forbidden=["sorted", ".sort", "heapq.merge"],
))


# ==========================================================================
# Level 3 — palindrome_partitioner
# ==========================================================================

def ref_palindrome(s):
    n = len(s)
    if n <= 1:
        return 0
    pal = [[False] * n for _ in range(n)]
    cuts = [0] * n
    for i in range(n):
        best = i
        for j in range(i + 1):
            if s[j] == s[i] and (i - j < 2 or pal[j + 1][i - 1]):
                pal[j][i] = True
                best = 0 if j == 0 else min(best, cuts[j - 1] + 1)
        cuts[i] = best
    return cuts[-1]


def gen_palindrome(rng):
    alphabet = rng.choice(["a", "ab", "ab", "abc", "abcd", "abcdefghij"])
    return ("".join(rng.choice(alphabet) for _ in range(rng.randint(0, 16))),)


register(Exercise(
    name="palindrome_partitioner",
    level=3,
    signature="def palindrome_partitioner(s: str) -> int:",
    ref=ref_palindrome,
    examples=[
        (("aab",), 1),
        (("aba",), 0),
        (("abc",), 2),
    ],
    edge_cases=[
        ("",), ("a",), ("aa",), ("ab",), ("aaa",), ("aaaa",), ("abba",), ("abcba",),
        ("racecar",), ("racecarx",), ("xracecar",), ("abacaba",), ("cdd",), ("efe",),
        ("coder",), ("noonabbad",), ("ababbbabbababa",), ("abcdefghij",),
        ("aabbaa",), ("aabbc",), ("banana",), ("Aa",), ("a a",), ("12321",),
        ("leetcode",), ("abababababab",),
    ],
    gen=gen_palindrome,
    perf=[
        (lambda rng: ("".join(rng.choice("ab") for _ in range(500)),), 5.0),
        (lambda rng: ("a" * 500,), 5.0),
        (lambda rng: ("".join(rng.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(500)),), 5.0),
    ],
    forbidden=["import:*"],   # sujet : "Allowed functions: None"
))


# ==========================================================================
# Level 3 — package_dependency_resolver
# ==========================================================================

def _graph(packages):
    indeg = {p: 0 for p in packages}
    dependents = {p: [] for p in packages}
    for pkg, deps in packages.items():
        for d in deps:
            if d in packages:
                indeg[pkg] += 1
                dependents[d].append(pkg)
    return indeg, dependents


def resolver_levels(packages):
    """Kahn par niveaux : chaque vague de paquets prêts est triée alphabétiquement."""
    indeg, dependents = _graph(packages)
    level = sorted(p for p in packages if indeg[p] == 0)
    order = []
    while level:
        order += level
        nxt = []
        for p in level:
            for q in dependents[p]:
                indeg[q] -= 1
                if indeg[q] == 0:
                    nxt.append(q)
        level = sorted(nxt)
    return order if len(order) == len(packages) else []


def resolver_fifo(packages, sort_dependents):
    """Kahn avec file FIFO initialisée triée."""
    indeg, dependents = _graph(packages)
    queue = sorted(p for p in packages if indeg[p] == 0)
    order = []
    while queue:
        p = queue.pop(0)
        order.append(p)
        deps = sorted(dependents[p]) if sort_dependents else dependents[p]
        for q in deps:
            indeg[q] -= 1
            if indeg[q] == 0:
                queue.append(q)
    return order if len(order) == len(packages) else []


def check_resolver(args, got, expected):
    (packages,) = args
    if type(got) is not list:
        return f"type de retour {type(got).__name__}, attendu list"
    variants = [resolver_levels(packages), resolver_fifo(packages, True),
                resolver_fifo(packages, False)]
    if got in variants:
        return None
    if not variants[0]:
        return f"obtenu {got!r} alors qu'il y a un cycle (attendu [])"[:300]
    if sorted(got) != sorted(packages):
        return f"obtenu {got!r} : il manque des paquets ou il y en a en trop"[:300]
    pos = {p: i for i, p in enumerate(got)}
    for pkg, deps in packages.items():
        for d in deps:
            if d in packages and pos[d] > pos[pkg]:
                return f"obtenu {got!r} : '{pkg}' installé avant sa dépendance '{d}'"[:300]
    return (f"obtenu {got!r} : ordre valide mais pas déterministe/alphabétique "
            f"(Kahn, sources triées par ordre alphabétique)")[:300]


NAMES = ["api", "app", "auth", "cache", "core", "db", "driver", "log", "net",
         "orm", "ui", "utils", "web", "x", "y", "z", "A", "B", "C"]


def gen_resolver(rng):
    nodes = rng.sample(NAMES, rng.randint(0, 9))
    packages = {}
    for i, n in enumerate(nodes):
        deps = rng.sample(nodes[:i], rng.randint(0, min(i, 3)))
        if rng.random() < 0.15:
            deps.append("missing_" + rng.choice("abc"))
        packages[n] = deps
    if nodes and rng.random() < 0.25:            # cycle
        a = rng.choice(nodes)
        b = rng.choice(nodes)
        if b not in packages[a]:
            packages[a].append(b)
        later = nodes[nodes.index(b):]
        if a not in later and a != b:
            if a not in packages[b]:
                packages[b].append(a)
    items = list(packages.items())
    rng.shuffle(items)
    return (dict(items),)


def perf_resolver(rng):
    nodes = [f"pkg{i:05d}" for i in range(3000)]
    packages = {n: [nodes[j] for j in rng.sample(range(i), min(i, 3))]
                for i, n in enumerate(nodes)}
    items = list(packages.items())
    rng.shuffle(items)
    return (dict(items),)


register(Exercise(
    name="package_dependency_resolver",
    level=3,
    signature="def package_dependency_resolver(packages: dict[str, list[str]]) -> list[str]:",
    ref=resolver_levels,
    examples=[
        (({"app": ["database"], "database": ["driver"], "driver": []},),
         ["driver", "database", "app"]),
        (({"A": [], "B": ["A"], "C": ["A", "B"]},), ["A", "B", "C"]),
        (({},), []),
        (({"X": ["Y"], "Y": ["X"]},), []),
        (({"web": [], "api": [], "frontend": ["web"], "backend": ["api"]},),
         ["api", "web", "backend", "frontend"]),
    ],
    edge_cases=[
        ({"a": []},), ({"a": ["a"]},), ({"a": [], "b": ["b"]},),
        ({"a": ["missing"]},), ({"b": [], "a": []},), ({"c": [], "b": [], "a": []},),
        ({"a": ["b"], "b": ["c"], "c": ["a"]},),
        ({"ok": [], "x": ["y"], "y": ["x"]},),
        ({"c": ["a"], "b": ["a"], "a": []},),
        ({"x": ["y"], "y": ["z"], "z": []},),
        ({"x": ["y", "ghost"], "y": ["ghost2"], "z": []},),
        ({"a": ["b", "c"], "b": ["d"], "c": ["d"], "d": []},),
        ({"lib": [], "app": ["lib", "lib2"], "lib2": ["lib"]},),
        ({"B": [], "a": [], "A": []},),            # tri sensible à la casse
    ],
    gen=gen_resolver,
    perf=[(perf_resolver, 5.0)],
    forbidden=["import:graphlib", "TopologicalSorter"],
    check=check_resolver,
))


# ==========================================================================
# Level 4 — sliding_window_maximum
# ==========================================================================

def ref_window(nums, k):
    if k <= 0 or k > len(nums):
        return []
    dq, res = [], []          # indices, valeurs décroissantes (O(n) amorti)
    head = 0
    for i, x in enumerate(nums):
        while len(dq) > head and nums[dq[-1]] <= x:
            dq.pop()
        dq.append(i)
        if dq[head] <= i - k:
            head += 1
        if i >= k - 1:
            res.append(nums[dq[head]])
    return res


def gen_window(rng):
    n = rng.randint(0, 15)
    nums = [rng.randint(-10, 10) for _ in range(n)]
    return nums, rng.randint(-1, n + 1)


def perf_window(n, k):
    def make(rng):
        return [rng.randint(-10**6, 10**6) for _ in range(n)], k
    return make


register(Exercise(
    name="sliding_window_maximum",
    level=4,
    signature="def sliding_window_maximum(nums: list[int], k: int) -> list[int]:",
    ref=ref_window,
    examples=[
        (([1, 3, -1, -3, 5, 3, 6, 7], 3), [3, 3, 5, 5, 6, 7]),
        (([1, 2, 3, 4, 5], 2), [2, 3, 4, 5]),
        (([5, 4, 3, 2, 1], 1), [5, 4, 3, 2, 1]),
        (([1, 2, 3], 3), [3]),
        (([1, 2, 3], 4), []),
        (([], 2), []),
        (([1, 2, 3], 0), []),
    ],
    edge_cases=[
        ([], 0), ([], -1), ([1], 1), ([1], 2), ([1, 2, 3], -1), ([1, 2, 3], -5),
        ([4, 4, 4], 2), ([-1, -2, -3], 2), ([-3, -2, -1], 2), ([9, 8, 7, 1, 2, 3], 3),
        ([1, 3, 1, 2, 0, 5], 3), ([7, 2, 4], 2), ([1, -1], 1), ([1, -1], 2),
        ([-7, -8, 7, 5, 7, 1, 6, 0], 4), ([0, 0, 0, 0], 4), ([5, 1, 1, 1, 1], 2),
        ([1, 1, 1, 1, 5], 4), (list(range(20)), 20), (list(range(20, 0, -1)), 5),
    ],
    gen=gen_window,
    perf=[
        (perf_window(100_000, 10_000), 3.0),
        (lambda rng: (list(range(100_000, 0, -1)), 50_000), 3.0),
        (lambda rng: (list(range(100_000)), 50_000), 3.0),
    ],
    forbidden=["import:*"],   # sujet : "Allowed functions: None"
))
