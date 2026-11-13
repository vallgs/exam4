"""Mode exam : un exo aléatoire par niveau, on ne passe au suivant qu'une fois réussi.

Usage :
    uv run exam.py           # démarre ou reprend l'exam
    uv run exam.py --reset   # recommence de zéro (efface exam/)
"""

import argparse
import json
import random
import shutil
import sys
import time
from pathlib import Path

from exercises import EXERCISES
from subjects import SUBJECTS
from tester import bold, dim, green, red, test_file, yellow

ROOT = Path(__file__).resolve().parent / "exam"
RENDU = ROOT / "rendu"
SUBJECT_DIR = ROOT / "subjects"
STATE = ROOT / ".state.json"
MAX_LEVEL = max(ex.level for ex in EXERCISES.values())


def load_state() -> dict | None:
    try:
        return json.loads(STATE.read_text())
    except (OSError, ValueError):
        return None


def save_state(state: dict) -> None:
    STATE.write_text(json.dumps(state, indent=2))


def setup_exercise(state: dict) -> None:
    """Tire un exo au hasard du niveau courant et prépare les fichiers."""
    pool = [ex.name for ex in EXERCISES.values() if ex.level == state["level"]]
    name = random.choice(pool)
    state["exo"] = name
    state["attempts"] = 0
    save_state(state)
    SUBJECT_DIR.mkdir(parents=True, exist_ok=True)
    RENDU.mkdir(parents=True, exist_ok=True)
    (SUBJECT_DIR / f"{name}.txt").write_text(SUBJECTS[name])
    rendu = RENDU / f"py_{name}.py"
    if not rendu.exists():
        rendu.touch()


def elapsed(state: dict) -> str:
    s = int(time.time() - state["start"])
    return f"{s // 3600}h{s % 3600 // 60:02d}m{s % 60:02d}s"


def show_assignment(state: dict) -> None:
    name = state["exo"]
    SUBJECT_DIR.mkdir(parents=True, exist_ok=True)
    (SUBJECT_DIR / f"{name}.txt").write_text(SUBJECTS[name])   # toujours à jour
    print(bold(f"\n══════ Level {state['level']}/{MAX_LEVEL} : {name} ══════"))
    print(SUBJECTS[name])
    print(f"  Sujet  : {SUBJECT_DIR / (name + '.txt')}")
    print(f"  Rendu  : {bold(str(RENDU / ('py_' + name + '.py')))}")
    print(dim(f"  Temps écoulé : {elapsed(state)}"))


def show_help() -> None:
    print(dim("  Commandes : grademe (g) | subject (s) | status | help (h) | quit (q)"))


def grademe(state: dict) -> bool:
    name = state["exo"]
    rendu = RENDU / f"py_{name}.py"
    state["attempts"] += 1
    save_state(state)
    if not rendu.exists() or not rendu.read_text().strip():
        print(red(f"\n✗ {rendu} est vide ou absent."))
        return False
    ok = test_file(rendu, name, random.randrange(1_000_000), verbose=False)
    state["history"].append({"exo": name, "level": state["level"],
                             "ok": ok, "at": elapsed(state)})
    save_state(state)
    return ok


def finish(state: dict) -> None:
    state["finished"] = True
    save_state(state)
    print(bold(green(f"\n🎉 Exam réussi ! {MAX_LEVEL}/{MAX_LEVEL} niveaux en {elapsed(state)}")))
    tries = len(state["history"])
    print(dim(f"   {tries} grademe au total. Relance avec --reset pour un nouvel exam."))


def main() -> int:
    parser = argparse.ArgumentParser(description="Mode exam rank 04 Python")
    parser.add_argument("--reset", action="store_true", help="recommencer un exam neuf")
    args = parser.parse_args()

    if args.reset and ROOT.exists():
        answer = input(yellow(f"Effacer {ROOT} (tes rendus inclus) ? [o/N] ")).strip().lower()
        if answer not in ("o", "oui", "y", "yes"):
            return 0
        shutil.rmtree(ROOT)

    state = load_state()
    if state is None:
        ROOT.mkdir(parents=True, exist_ok=True)
        state = {"level": 1, "start": time.time(), "history": [], "finished": False}
        setup_exercise(state)
        print(bold("Nouvel exam démarré. Bonne chance !"))
    else:
        print(bold("Reprise de l'exam en cours."))

    if state.get("finished"):
        finish(state)
        return 0

    show_assignment(state)
    show_help()

    while True:
        try:
            cmd = input(bold(f"\n[level {state['level']} | {state['exo']}] > ")).strip().lower()
        except (EOFError, KeyboardInterrupt):
            print(dim("\nExam en pause, relance `uv run exam.py` pour reprendre."))
            return 0

        if cmd in ("g", "grademe"):
            if grademe(state):
                print(bold(green(f"\n✓ Level {state['level']} validé !")))
                if state["level"] >= MAX_LEVEL:
                    finish(state)
                    return 0
                state["level"] += 1
                setup_exercise(state)
                show_assignment(state)
            else:
                print(red(f"\n✗ Échec (tentative {state['attempts']}). "
                          "Corrige ton fichier et relance grademe."))
        elif cmd in ("s", "subject"):
            show_assignment(state)
        elif cmd == "status":
            print(f"  Level {state['level']}/{MAX_LEVEL} — {state['exo']} — "
                  f"tentatives : {state['attempts']} — temps : {elapsed(state)}")
            for h in state["history"]:
                mark = green("✓") if h["ok"] else red("✗")
                print(f"    {mark} level {h['level']} {h['exo']}  ({h['at']})")
        elif cmd in ("q", "quit", "exit"):
            print(dim("Exam en pause, relance `uv run exam.py` pour reprendre."))
            return 0
        elif cmd in ("h", "help", ""):
            show_help()
        else:
            print(red(f"  Commande inconnue : {cmd}"))
            show_help()


if __name__ == "__main__":
    sys.exit(main())
