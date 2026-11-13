"""Testeur exam rank 04 Python.

Usage :
    uv run tester.py chemin/vers/py_merge_sorted_lists.py
    uv run tester.py mon_dossier/          # teste tous les fichiers reconnus
    uv run tester.py fichier.py --exo merge_sorted_lists
    uv run tester.py --list
"""

import argparse
import ast
import copy
import importlib.util
import io
import random
import signal
import sys
import time
from contextlib import redirect_stdout
from pathlib import Path

from exercises import EXERCISES

USE_COLOR = sys.stdout.isatty()


def color(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if USE_COLOR else text


def green(t): return color("32", t)
def red(t): return color("31", t)
def yellow(t): return color("33", t)
def bold(t): return color("1", t)
def dim(t): return color("2", t)


def short(value, limit: int = 160) -> str:
    text = repr(value)
    return text if len(text) <= limit else text[:limit] + f"... ({len(text)} chars)"


class Timeout(BaseException):
    """BaseException pour ne pas être avalée par un `except Exception`."""


def _on_alarm(signum, frame):
    raise Timeout()


def call_with_timeout(fn, args, timeout: float):
    signal.signal(signal.SIGALRM, _on_alarm)
    signal.setitimer(signal.ITIMER_REAL, timeout)
    try:
        return fn(*args)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


# --------------------------------------------------------------------------
# Analyse statique : fonctions / modules interdits
# --------------------------------------------------------------------------

def static_check(tree: ast.AST, forbidden: list[str]) -> list[str]:
    """Règles :  "name"  -> utilisation du builtin `name`
                 ".attr" -> appel de méthode `.attr(...)`
                 "mod.attr" -> `mod.attr` (alias compris) ou `from mod import attr`
                 "import:mod" -> tout import du module `mod`
                 "import:*" -> aucun import autorisé"""
    # alias d'import : `import heapq as h` -> aliases["heapq"] = {"heapq", "h"}
    aliases: dict[str, set[str]] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                aliases.setdefault(a.name, {a.name}).add(a.asname or a.name)

    problems = []
    for node in ast.walk(tree):
        line = getattr(node, "lineno", "?")
        for rule in forbidden:
            if rule == "import:*":
                if isinstance(node, ast.Import):
                    names = ", ".join(a.name for a in node.names)
                    problems.append(f"ligne {line}: import interdit '{names}' (aucun import autorisé)")
                elif isinstance(node, ast.ImportFrom):
                    problems.append(f"ligne {line}: import interdit '{node.module}' (aucun import autorisé)")
                elif isinstance(node, ast.Name) and node.id == "__import__":
                    problems.append(f"ligne {line}: __import__ interdit (aucun import autorisé)")
            elif rule.startswith("import:"):
                mod = rule[7:]
                if isinstance(node, ast.Import) and any(
                    a.name == mod or a.name.startswith(mod + ".") for a in node.names
                ):
                    problems.append(f"ligne {line}: import du module interdit '{mod}'")
                if isinstance(node, ast.ImportFrom) and node.module and (
                    node.module == mod or node.module.startswith(mod + ".")
                ):
                    problems.append(f"ligne {line}: import du module interdit '{mod}'")
            elif rule.startswith("."):
                attr = rule[1:]
                if isinstance(node, ast.Attribute) and node.attr == attr:
                    problems.append(f"ligne {line}: utilisation interdite de '.{attr}'")
            elif "." in rule:
                mod, attr = rule.split(".", 1)
                if (isinstance(node, ast.Attribute) and node.attr == attr
                        and isinstance(node.value, ast.Name)
                        and node.value.id in aliases.get(mod, {mod})):
                    problems.append(f"ligne {line}: utilisation interdite de '{rule}'")
                if (isinstance(node, ast.ImportFrom) and node.module == mod
                        and any(a.name in (attr, "*") for a in node.names)):
                    problems.append(f"ligne {line}: import interdit de '{rule}'")
            else:
                if isinstance(node, ast.Name) and node.id == rule:
                    problems.append(f"ligne {line}: utilisation interdite de '{rule}'")
    return sorted(set(problems), key=lambda p: (int(p.split()[1].rstrip(":")) if p.split()[1].rstrip(":").isdigit() else 0, p))


# --------------------------------------------------------------------------
# Exécution des tests
# --------------------------------------------------------------------------

def run_case(fn, ex, args, expected, timeout):
    """Retourne (ok, message_erreur, sortie_stdout)."""
    pristine = copy.deepcopy(args)
    call_args = copy.deepcopy(args)
    buf = io.StringIO()
    t0 = time.perf_counter()
    try:
        with redirect_stdout(buf):
            got = call_with_timeout(fn, call_args, timeout)
    except Timeout:
        return False, f"TIMEOUT (> {timeout}s)", buf.getvalue()
    except RecursionError:
        return False, "RecursionError (récursion trop profonde)", buf.getvalue()
    except SystemExit:
        return False, "la fonction appelle exit()/sys.exit()", buf.getvalue()
    except BaseException as e:  # noqa: BLE001
        return False, f"exception {type(e).__name__}: {e}", buf.getvalue()
    elapsed = time.perf_counter() - t0

    if expected is None:
        expected = ex.ref(*copy.deepcopy(pristine))
    error = ex.check(pristine, got, expected)
    if error is None and isinstance(got, list) and any(
        got is a or (isinstance(a, list) and any(got is x for x in a)) for a in call_args
    ):
        error = "retourne une liste d'entrée au lieu d'une nouvelle liste"
    if error is None and call_args != pristine:
        error = f"les arguments d'entrée ont été modifiés : {short(call_args)}"
    if error is None:
        return True, f"{elapsed:.3f}s", buf.getvalue()
    return False, error, buf.getvalue()


def fmt_call(ex, args) -> str:
    return f"{ex.name}({', '.join(short(a, 120) for a in args)})"


def test_file(path: Path, exo_name: str | None, seed: int, verbose: bool) -> bool:
    source = path.read_text()
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        print(red(f"\n✗ {path}: SyntaxError ligne {e.lineno}: {e.msg}"))
        return False

    if exo_name is None:
        exo_name = detect_exercise(path, tree)
    if exo_name is None:
        print(red(f"\n✗ {path}: impossible de déterminer l'exercice (utilise --exo)"))
        return False
    ex = EXERCISES[exo_name]

    print(bold(f"\n━━━ {ex.name}  (level {ex.level}) ━━━  {dim(str(path))}"))
    all_ok = True

    # 1. Statique
    problems = static_check(tree, ex.forbidden)
    if problems:
        all_ok = False
        print(red("  ✗ Fonctions interdites :"))
        for p in problems:
            print(red(f"      {p}"))
    elif ex.forbidden:
        rules = ", ".join("aucun import" if r == "import:*" else r for r in ex.forbidden)
        print(green(f"  ✓ Aucune fonction interdite ({rules})"))

    # 2. Import
    spec = importlib.util.spec_from_file_location(f"user_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            call_with_timeout(spec.loader.exec_module, (module,), 5)
    except BaseException as e:  # noqa: BLE001
        print(red(f"  ✗ Erreur à l'import du fichier : {type(e).__name__}: {e}"))
        return False
    if buf.getvalue():
        print(yellow(f"  ⚠ Le fichier affiche quelque chose à l'import : {short(buf.getvalue(), 80)}"))

    fn = getattr(module, ex.name, None)
    if not callable(fn):
        print(red(f"  ✗ Fonction '{ex.name}' introuvable dans le fichier"))
        return False
    nparams = fn.__code__.co_argcount if hasattr(fn, "__code__") else None
    if nparams is not None and nparams != ex.nargs:
        print(red(f"  ✗ Signature : {nparams} paramètre(s), attendu {ex.nargs}"))
        print(dim(f"      attendu : {ex.signature}"))
        return False
    print(green(f"  ✓ Fonction trouvée : {ex.signature}"))

    # 3. Tests
    rng = random.Random(seed)
    suites = [
        ("Exemples du sujet", [(a, e, ex.timeout) for a, e in ex.examples]),
        ("Cas limites", [(a, None, ex.timeout) for a in ex.edge_cases]),
        (f"Aléatoires (seed={seed})",
         [(ex.gen(rng), None, ex.timeout) for _ in range(ex.n_random)]),
    ]
    if ex.perf:
        suites.append(("Performance", [(f(random.Random(seed)), None, t) for f, t in ex.perf]))

    printed_output = False
    for title, cases in suites:
        failures = []
        passed = 0
        slowest = 0.0
        for args, expected, timeout in cases:
            ok, msg, out = run_case(fn, ex, args, expected, timeout)
            if out and not printed_output:
                printed_output = True
                print(yellow(f"  ⚠ La fonction affiche sur stdout : {short(out, 80)}"))
            if ok:
                passed += 1
                slowest = max(slowest, float(msg[:-1]))
            else:
                failures.append((args, expected, msg))
        total = len(cases)
        extra = dim(f"  (max {slowest:.3f}s)") if title == "Performance" and not failures else ""
        if failures:
            all_ok = False
            print(red(f"  ✗ {title} : {passed}/{total}"))
            for args, expected, msg in failures[: None if verbose else 3]:
                if expected is None:
                    try:
                        expected = ex.ref(*copy.deepcopy(args))
                    except Exception:  # noqa: BLE001
                        expected = "?"
                print(f"      {dim('appel   :')} {fmt_call(ex, args)}")
                print(f"      {dim('attendu :')} {short(expected)}")
                print(f"      {dim('erreur  :')} {red(msg)}")
            if not verbose and len(failures) > 3:
                print(dim(f"      ... et {len(failures) - 3} autre(s) échec(s) (-v pour tout voir)"))
        else:
            print(green(f"  ✓ {title} : {passed}/{total}") + extra)

    print(bold(green("  ➜ SUCCESS")) if all_ok else bold(red("  ➜ FAILURE")))
    return all_ok


def detect_exercise(path: Path, tree: ast.AST) -> str | None:
    stem = path.stem.lower()
    stem = stem[3:] if stem.startswith("py_") else stem
    if stem in EXERCISES:
        return stem
    defined = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    found = [name for name in EXERCISES if name in defined]
    return found[0] if len(found) == 1 else None


def collect(paths: list[str]) -> list[Path]:
    files = []
    for p in map(Path, paths):
        if p.is_dir():
            for f in sorted(p.rglob("*.py")):
                stem = f.stem.lower().removeprefix("py_")
                if stem in EXERCISES:
                    files.append(f)
        elif p.is_file():
            files.append(p)
        else:
            print(red(f"✗ {p} : introuvable"))
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description="Testeur exam rank 04 Python (42)")
    parser.add_argument("paths", nargs="*", help="fichiers .py ou dossiers à tester")
    parser.add_argument("--exo", choices=sorted(EXERCISES), help="forcer l'exercice")
    parser.add_argument("--seed", type=int, default=None, help="seed des tests aléatoires")
    parser.add_argument("-v", "--verbose", action="store_true", help="afficher tous les échecs")
    parser.add_argument("--list", action="store_true", help="lister les exercices")
    args = parser.parse_args()

    if args.list or not args.paths:
        print(bold("Exercices supportés :"))
        for ex in sorted(EXERCISES.values(), key=lambda e: (e.level, e.name)):
            print(f"  level {ex.level}  py_{ex.name}.py   {dim(ex.signature)}")
        if not args.paths and not args.list:
            print(dim("\nUsage : uv run tester.py <fichier.py | dossier> [...]"))
        return 0

    if args.exo and len(args.paths) != 1:
        parser.error("--exo s'utilise avec un seul fichier")

    seed = args.seed if args.seed is not None else random.randrange(1_000_000)
    files = collect(args.paths)
    if not files:
        print(red("Aucun fichier d'exercice trouvé."))
        return 1

    results = [(f, test_file(f, args.exo, seed, args.verbose)) for f in files]

    if len(results) > 1:
        print(bold("\n━━━ Résumé ━━━"))
        for f, ok in results:
            print(f"  {green('✓') if ok else red('✗')} {f}")
    return 0 if all(ok for _, ok in results) else 1


if __name__ == "__main__":
    sys.exit(main())
