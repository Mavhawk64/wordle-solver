#!/usr/bin/env python3
"""
NAWS (New AWS) runner:
Simulate all Wordle games against the list in fives.txt using the advanced solver.

- Hard Mode enforced: each next guess is chosen from the current consistent set.
- Uses entropy-based selection (pick_best_hard_mode_guess).
- Starts from a fixed opener (default: 'arose'), but you can tweak FIRST_GUESS below.
- Tracks per-turn present counts to compute correct min-counts across turns.
- Tracks per-turn upper bounds when extra duplicate letters came back gray.
- Uses solver's feedback_pattern to generate exact per-position feedback.
"""

import sys
from collections import Counter

import new_advanced_solver as naws  # rename if your file/module name differs

FIRST_GUESS = "arose"
SHOW_PROGRESS_EVERY = 100  # print a heartbeat every N answers


def color_word(guess: str, answer: str) -> str:
    """ANSI-colored representation based on true feedback for debug/pretty printing."""
    pattern = naws.feedback_pattern(guess, answer)  # '2','1','0'
    pieces = []
    for ch, p in zip(guess, pattern):
        if p == "2":
            pieces.append(f"\033[92m{ch.upper()}\033[0m")  # green
        elif p == "1":
            pieces.append(f"\033[93m{ch.upper()}\033[0m")  # yellow
        else:
            pieces.append(f"\033[90m{ch.upper()}\033[0m")  # gray
    return "".join(pieces)


def simulate_one(answer: str, words: list[str], verbose: bool = False) -> int:
    """
    Play one full game against `answer`.
    Returns number of guesses taken (1..6) if solved, or 7 if unsolved (for scoring).
    """
    positions_list: list[tuple[str, int, bool]] = []  # (ch, idx, is_green)
    excluded_letters: str = ""  # 'x' letters not present in that turn
    present_counts_by_turn: list[
        Counter
    ] = []  # per-turn present counts (yellows+greens)
    upper_bounds_by_turn: list[
        dict[str, int]
    ] = []  # per-turn upper bounds {ch: max_count_this_turn}

    guess: str = FIRST_GUESS
    for turn in range(6):
        # Compute true feedback using solver's logic (handles duplicates)
        pattern = naws.feedback_pattern(guess, answer)  # string over {'0','1','2'}

        if verbose:
            print(
                f"Attempt {turn + 1}/6  Guess: {color_word(guess, answer)}  Pattern: {pattern}"
            )

        # If all green, solved
        if pattern == "22222":
            return turn + 1

        # Build this turn's annotations
        guess_counts = Counter(guess)  # total guessed per letter this turn
        turn_present_counter = Counter()  # letters with '1' or '2' this turn

        # First pass: collect present letters (positions with 1 or 2)
        for ch, p in zip(guess, pattern):
            if p in ("1", "2"):
                turn_present_counter[ch] += 1

        # Upper bounds this turn: if we guessed a letter more times than it was present,
        # the answer has at most 'present' copies this turn.
        ub_this_turn: dict[str, int] = {}
        for ch, gcount in guess_counts.items():
            pcnt = turn_present_counter[ch]
            if gcount > pcnt:
                ub_this_turn[ch] = pcnt
        upper_bounds_by_turn.append(ub_this_turn)

        # Second pass: update global constraint stores
        for idx, (ch, p) in enumerate(zip(guess, pattern)):
            if p == "2":
                positions_list.append((ch, idx, True))
            elif p == "1":
                positions_list.append((ch, idx, False))
            else:  # '0' gray
                # Add to excluded only if this letter wasn't present elsewhere this turn
                if ch not in turn_present_counter:
                    excluded_letters += ch

        present_counts_by_turn.append(turn_present_counter)

        # Recompute candidate set under all constraints so far
        candidates = naws.solvable_words(
            words,
            letters="",  # kept for compatibility with the signature
            positions=positions_list,
            excluded_letters_string=excluded_letters,
            present_counts_by_turn=present_counts_by_turn,
            upper_bounds_by_turn=upper_bounds_by_turn,  # <-- pass UBs
        )

        if not candidates:
            # Dead-end under constraints -> mark unsolved (score as 7)
            if verbose:
                print("No candidates remain; marking as unsolved.")
            return 7

        # Pick next guess from candidates by entropy
        guess = naws.pick_best_hard_mode_guess(candidates, prefer_entropy=True)
        if guess == "":
            # No valid guess could be picked -> mark unsolved (score as 7)
            if verbose:
                print("No valid guess could be picked; marking as unsolved.", answer)
            return 7

    # If we exit the loop without solving in 6, count as unsolved (7)
    return 7


def main():
    # Load the master word list
    try:
        with open("fives.txt", "r") as f:
            all_words = [w.strip().lower() for w in f if len(w.strip()) == 5]
    except FileNotFoundError:
        print(
            "Could not open 'fives.txt'. Please place a 5-letter word list in this folder.",
            file=sys.stderr,
        )
        sys.exit(1)

    scores: list[int] = []
    unsolved: list[str] = []

    total = len(all_words)
    for idx, answer in enumerate(all_words, start=1):
        # NOTE: For Hard Mode with answer list == guess list, candidates pool is the same.
        # If you maintain a separate "valid guesses" list, pass that instead.
        result = simulate_one(answer, all_words, verbose=False)
        scores.append(result)
        if result == 7:
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
    hardest_word = all_words[hardest_idx] if hardest_idx >= 0 else ""

    print("\n=== Final Results ===")
    print("Unsolved words:", len(unsolved))
    if unsolved:
        print(", ".join(unsolved))
    print(f"Solve rate: {solve_rate:.5f}")
    print(f"Average score: {avg_score:.5f}")
    print(f"Max score: {max_score}  ({hardest_word})")


if __name__ == "__main__":
    main()
