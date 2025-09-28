#!/usr/bin/env python3
"""
NORMAL MODE runner:
Simulate Wordle with information-first strategy:
- Early turns: choose ANY guess (not just candidates) to maximize information.
- Late turns: switch to answer-only guesses to finish quickly.

Heuristics:
- Optionally force 2 info-rich openers (AROSE, TULIP) for 10 unique letters.
- Otherwise, pick max-entropy from the full guess list.
- Switch to answer-only when |candidates| <= FINISH_SWITCH (default 12).
"""

import sys
from collections import Counter
from typing import List

import new_advanced_solver as solver  # adjust import name if needed

# --- Config ---
FORCE_OPENERS: bool = True
OPENERS: List[str] = ["arose", "tulip"]  # 10 unique letters in 2 turns
FINISH_SWITCH: int = 12  # when candidates <= this, restrict guesses to answers only
SHOW_PROGRESS_EVERY: int = 100


def color_word(guess: str, answer: str) -> str:
    pattern = solver.feedback_pattern(guess, answer)  # '2','1','0'
    pieces = []
    for ch, p in zip(guess, pattern):
        if p == "2":
            pieces.append(f"\033[92m{ch.upper()}\033[0m")  # green
        elif p == "1":
            pieces.append(f"\033[93m{ch.upper()}\033[0m")  # yellow
        else:
            pieces.append(f"\033[90m{ch.upper()}\033[0m")  # gray
    return "".join(pieces)


def simulate_one(
    answer: str, answers: List[str], guesses: List[str], verbose: bool = False
) -> int:
    """
    Normal mode: returns number of guesses (1..6) or 7 if unsolved.
    `answers` is the candidate answer set; `guesses` is the full allowed guess list.
    They can be the same list if you only have one file.
    """
    positions_list: list[tuple[str, int, bool]] = []
    excluded_letters: str = ""
    present_counts_by_turn: list[Counter] = []
    upper_bounds_by_turn: list[dict[str, int]] = []

    guess = OPENERS[0] if FORCE_OPENERS and OPENERS else guesses[0]

    for turn in range(6):
        pattern = solver.feedback_pattern(guess, answer)

        if verbose:
            print(
                f"Attempt {turn + 1}/6  Guess: {color_word(guess, answer)}  Pattern: {pattern}"
            )

        if pattern == "22222":
            return turn + 1

        # Build per-turn counts
        guess_counts = Counter(guess)
        turn_present = Counter(ch for ch, p in zip(guess, pattern) if p in ("1", "2"))
        present_counts_by_turn.append(Counter(turn_present))

        # Upper bounds this turn (duplicates probe)
        ub_this_turn = {}
        for ch, gcount in guess_counts.items():
            pcnt = turn_present[ch]
            if gcount > pcnt:
                ub_this_turn[ch] = pcnt
        upper_bounds_by_turn.append(ub_this_turn)

        # Update constraints
        for idx, (ch, p) in enumerate(zip(guess, pattern)):
            if p == "2":
                positions_list.append((ch, idx, True))
            elif p == "1":
                positions_list.append((ch, idx, False))
            else:
                if ch not in turn_present:
                    excluded_letters += ch

        # Compute current candidate answers given constraints
        candidates = solver.solvable_words(
            answers,
            letters="",  # legacy arg
            positions=positions_list,
            excluded_letters_string=excluded_letters,
            present_counts_by_turn=present_counts_by_turn,
            upper_bounds_by_turn=upper_bounds_by_turn,
        )

        if not candidates:
            # No answers consistent with feedback -> mark unsolved (defensive)
            if verbose:
                print("No candidates remain under constraints.")
            return 7

        # Pick next guess:
        # 1) If forcing openers, use them for the first few turns unless we are already in finishing range
        if (
            FORCE_OPENERS
            and turn + 1 < len(OPENERS)
            and len(candidates) > FINISH_SWITCH
        ):
            guess = OPENERS[turn + 1]
            continue

        # 2) If many candidates remain, pick the *best information* from the full guesses list
        if len(candidates) > FINISH_SWITCH:
            guess = solver.pick_best_from_guess_list(
                guesses, candidates, prefer_entropy=True
            )
        else:
            # 3) Finish: restrict to candidate answers and choose a strong finisher
            guess = solver.pick_best_hard_mode_guess(candidates, prefer_entropy=True)

        if not guess:
            return 7

    return 7


def main():
    # Load lists. If you have separate files (answers.txt vs guesses.txt), load them separately.
    try:
        with open("fives.txt", "r") as f:
            all_words = [w.strip().lower() for w in f if len(w.strip()) == 5]
    except FileNotFoundError:
        print(
            "Could not open 'fives.txt'. Please place it in this folder.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Using the same list for answers and guesses by default.
    answers = all_words
    guesses = all_words

    scores: list[int] = []
    unsolved: list[str] = []

    total = len(answers)
    for idx, answer in enumerate(answers, start=1):
        res = simulate_one(answer, answers, guesses, verbose=False)
        scores.append(res)
        if res == 7:
            unsolved.append(answer)

        if idx % SHOW_PROGRESS_EVERY == 0 or idx == total:
            solved = idx - len(unsolved)
            rate = solved / idx
            avg = sum(scores) / idx
            print(
                f"[{idx}/{total}] running solve rate={rate:.4f}, avg guesses={avg:.3f}, unsolved={len(unsolved)}"
            )

    solved = total - len(unsolved)
    solve_rate = solved / total if total else 0.0
    avg_score = sum(scores) / total if total else 0.0
    max_score = max(scores) if scores else 0
    hardest_idx = scores.index(max_score) if scores else -1
    hardest_word = answers[hardest_idx] if hardest_idx >= 0 else ""

    print("\n=== Final Results ===")
    print("Unsolved words:", len(unsolved))
    if unsolved:
        print(", ".join(unsolved))
    print(f"Solve rate: {solve_rate:.5f}")
    print(f"Average score: {avg_score:.5f}")
    print(f"Max score: {max_score}  ({hardest_word})")


if __name__ == "__main__":
    main()
