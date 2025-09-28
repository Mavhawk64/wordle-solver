#!/usr/bin/env python3
"""
Hard-Mode Wordle Assistant with Entropy-Based Guess Picker
- Interactive loop (y/n/x) per letter
- Tracks greens, "yellow-not-here" positions, and minimum letter counts
- min_counts per letter = MAX across turns (not sum)
- NEW: upper_bounds_by_turn gives max allowed counts for letters when extra copies are gray.
- Picks next guess by maximizing entropy.
"""

import math
import sys
from collections import Counter, defaultdict
from typing import Dict, List, Set, Tuple

# ----------------------------
# Feedback / Information theory
# ----------------------------


def feedback_pattern(guess: str, answer: str) -> str:
    n = len(guess)
    res = ["0"] * n
    remaining = Counter()
    for i, (g, a) in enumerate(zip(guess, answer)):
        if g == a:
            res[i] = "2"
        else:
            remaining[a] += 1
    for i, g in enumerate(guess):
        if res[i] == "2":
            continue
        if remaining[g] > 0:
            res[i] = "1"
            remaining[g] -= 1
    return "".join(res)


def pattern_counts_for_guess(guess: str, candidates: List[str]) -> Dict[str, int]:
    counts = defaultdict(int)
    for ans in candidates:
        counts[feedback_pattern(guess, ans)] += 1
    return counts


def entropy_of_guess(guess: str, candidates: List[str]) -> float:
    counts = pattern_counts_for_guess(guess, candidates)
    n = max(len(candidates), 1)
    ent = 0.0
    for c in counts.values():
        p = c / n
        if p > 0:
            ent -= p * math.log2(p)
    return ent


def expected_remaining_of_guess(guess: str, candidates: List[str]) -> float:
    counts = pattern_counts_for_guess(guess, candidates)
    n = max(len(candidates), 1)
    return sum(c * c for c in counts.values()) / n


def coverage_score(guess: str, candidates: List[str]) -> float:
    joined = "".join(candidates)
    freqs = Counter(joined)
    return sum(freqs[ch] for ch in set(guess))


def pick_best_hard_mode_guess(cands: List[str], prefer_entropy: bool = True) -> str:
    if not cands:
        return ""
    best = ""
    if prefer_entropy:
        best_ent, best_cov = -1.0, -1.0
        for w in cands:
            ent = entropy_of_guess(w, cands)
            cov = coverage_score(w, cands)
            if ent > best_ent or (math.isclose(ent, best_ent) and cov > best_cov):
                best, best_ent, best_cov = w, ent, cov
    else:
        best_er, best_ent = float("inf"), -1.0
        for w in cands:
            er = expected_remaining_of_guess(w, cands)
            ent = entropy_of_guess(w, cands)
            if er < best_er or (math.isclose(er, best_er) and ent > best_ent):
                best, best_er, best_ent = w, er, ent
    return best


def rank_candidates_by_entropy(cands: List[str]) -> List[Tuple[str, float, float]]:
    scored = [(w, entropy_of_guess(w, cands), coverage_score(w, cands)) for w in cands]
    return sorted(scored, key=lambda t: (-t[1], -t[2], t[0]))


def pick_best_from_guess_list(
    guess_list: List[str], candidates: List[str], prefer_entropy: bool = True
) -> str:
    """
    NORMAL MODE: pick the best next guess from an arbitrary guess_list (can include non-answers),
    scoring by how well it partitions the *current candidates*.
    """
    if not guess_list or not candidates:
        return ""
    best = ""
    if prefer_entropy:
        best_ent, best_cov = -1.0, -1.0
        for w in guess_list:
            ent = entropy_of_guess(w, candidates)
            cov = coverage_score(
                w, candidates
            )  # tie-breaker favors unique, high-coverage letters
            if ent > best_ent or (math.isclose(ent, best_ent) and cov > best_cov):
                best, best_ent, best_cov = w, ent, cov
        return best
    else:
        # minimize expected remaining (good when candidates are already fairly small)
        best_er, best_ent = float("inf"), -1.0
        for w in guess_list:
            er = expected_remaining_of_guess(w, candidates)
            ent = entropy_of_guess(w, candidates)
            if er < best_er or (math.isclose(er, best_er) and ent > best_ent):
                best, best_er, best_ent = w, er, ent
        return best


def rank_from_guess_list(
    guess_list: List[str], candidates: List[str]
) -> List[Tuple[str, float, float]]:
    """
    NORMAL MODE: (word, entropy, coverage) ranked over an arbitrary guess_list against the same candidates.
    """
    scored = []
    for w in guess_list:
        ent = entropy_of_guess(w, candidates)
        cov = coverage_score(w, candidates)
        scored.append((w, ent, cov))
    scored.sort(key=lambda t: (-t[1], -t[2], t[0]))
    return scored


# ----------------------------
# Constraint building & filtering
# ----------------------------


def build_constraints(
    positions_list: List[Tuple[str, int, bool]],
    excluded_letters_string: str,
    present_counts_by_turn: List[Counter],
    upper_bounds_by_turn: List[Dict[str, int]],
) -> Tuple[Dict[int, str], Dict[str, Set[int]], Counter, Dict[str, int], Set[str]]:
    greens: Dict[int, str] = {}
    yellows_not_here: Dict[str, Set[int]] = defaultdict(set)
    present_letters: Set[str] = set()
    for ch, j, is_green in positions_list:
        if is_green:
            greens[j] = ch
        else:
            yellows_not_here[ch].add(j)
        present_letters.add(ch)
    min_counts: Counter = Counter()
    for t in present_counts_by_turn:
        for ch, c in t.items():
            if c > min_counts[ch]:
                min_counts[ch] = c
    max_counts: Dict[str, int] = {}
    for ub in upper_bounds_by_turn:
        for ch, ub_val in ub.items():
            if ch in max_counts:
                max_counts[ch] = min(max_counts[ch], ub_val)
            else:
                max_counts[ch] = ub_val
    for ch, mn in min_counts.items():
        if ch in max_counts and max_counts[ch] < mn:
            max_counts[ch] = mn
    globally_excluded = {
        ch for ch in excluded_letters_string if ch not in present_letters
    }
    return greens, yellows_not_here, min_counts, max_counts, globally_excluded


def candidate_ok(
    word: str,
    greens: Dict[int, str],
    yellows_not_here: Dict[str, Set[int]],
    min_counts: Counter,
    max_counts: Dict[str, int],
    globally_excluded: Set[str],
) -> bool:
    if any(ch in globally_excluded for ch in word):
        return False
    for pos, ch in greens.items():
        if word[pos] != ch:
            return False
    wcount = Counter(word)
    for ch, needed in min_counts.items():
        if wcount[ch] < needed:
            return False
    for ch, ub in max_counts.items():
        if wcount[ch] > ub:
            return False
    for ch, bad_positions in yellows_not_here.items():
        for bp in bad_positions:
            if word[bp] == ch:
                return False
    return True


def filter_candidates(
    words: List[str],
    greens: Dict[int, str],
    yellows_not_here: Dict[str, Set[int]],
    min_counts: Counter,
    max_counts: Dict[str, int],
    globally_excluded: Set[str],
) -> List[str]:
    return [
        w
        for w in words
        if candidate_ok(
            w, greens, yellows_not_here, min_counts, max_counts, globally_excluded
        )
    ]


def sort_words(words: List[str]) -> List[str]:
    if not words:
        return []
    pos_freq = [Counter(w[i] for w in words) for i in range(5)]
    global_freq = Counter("".join(words))

    def score_word(w: str) -> float:
        uniq = len(set(w))
        pos_score = sum(pos_freq[i][ch] for i, ch in enumerate(w))
        letter_score = sum(global_freq[ch] for ch in set(w))
        repeat_penalty = 0.15 * (5 - uniq)
        return pos_score + letter_score - repeat_penalty

    return sorted(words, key=score_word, reverse=True)


def solvable_words(
    words: List[str],
    letters: str,
    positions: List[Tuple[str, int, bool]],
    excluded_letters_string: str = "",
    present_counts_by_turn: List[Counter] | None = None,
    upper_bounds_by_turn: List[Dict[str, int]] | None = None,
) -> List[str]:
    if present_counts_by_turn is None:
        present_counts_by_turn = []
    if upper_bounds_by_turn is None:
        upper_bounds_by_turn = []
    greens, yellows_not_here, min_counts, max_counts, globally_excluded = (
        build_constraints(
            positions,
            excluded_letters_string,
            present_counts_by_turn,
            upper_bounds_by_turn,
        )
    )
    return filter_candidates(
        words, greens, yellows_not_here, min_counts, max_counts, globally_excluded
    )


# --------------------------------
# Interactive loop
# --------------------------------


def main():
    try:
        with open("fives.txt", "r") as f:
            words = [w.strip().lower() for w in f if len(w.strip()) == 5]
    except FileNotFoundError:
        print("Could not open 'fives.txt'.", file=sys.stderr)
        sys.exit(1)

    positions_list: List[Tuple[str, int, bool]] = []
    excluded_letters = ""
    present_counts_by_turn: List[Counter] = []
    upper_bounds_by_turn: List[Dict[str, int]] = []

    print("Hard-Mode Wordle Assistant (entropy picker).")
    print("Enter your guess, then for each letter respond:")
    print("  y = green (correct letter & position)")
    print("  n = yellow (letter present, wrong position)")
    print("  x = gray (letter not in word, unless seen present elsewhere this turn)")
    print("-" * 60)

    for attempt in range(6):
        print(f"\nAttempt {attempt + 1}/6")
        while True:
            guess = input("Enter your 5-letter word: ").strip().lower()
            if len(guess) == 5 and guess.isalpha():
                break
            print("Please enter exactly 5 letters.")

        per_letter_marks = []
        guess_counts = Counter(guess)
        turn_present = Counter()
        greens_this_turn = 0

        # PRETTY INPUT PROMPTS
        for j, ch in enumerate(guess):
            while True:
                status = (
                    input(
                        f"Is '{ch}' correct at position {j + 1}? (y=green / n=yellow / x=gray): "
                    )
                    .strip()
                    .lower()
                )
                if status in {"y", "n", "x"}:
                    break
                print("Please respond with 'y', 'n', or 'x'.")
            per_letter_marks.append((ch, j, status))
            if status in {"y", "n"}:
                turn_present[ch] += 1
            if status == "y":
                greens_this_turn += 1

        present_counts_by_turn.append(turn_present)
        ub_this_turn = {
            ch: turn_present[ch]
            for ch, gcount in guess_counts.items()
            if gcount > turn_present[ch]
        }
        upper_bounds_by_turn.append(ub_this_turn)

        turn_present_letters = set(turn_present.keys())
        for ch, j, status in per_letter_marks:
            if status == "y":
                positions_list.append((ch, j, True))
            elif status == "n":
                positions_list.append((ch, j, False))
            else:
                positions_list.append((ch, j, False))
                if ch not in turn_present_letters:
                    excluded_letters += ch

        if greens_this_turn == 5:
            print("Congratulations! You've guessed the word!")
            return

        candidates = solvable_words(
            words,
            letters="",
            positions=positions_list,
            excluded_letters_string=excluded_letters,
            present_counts_by_turn=present_counts_by_turn,
            upper_bounds_by_turn=upper_bounds_by_turn,
        )
        if not candidates:
            print("\nNo candidates remain.")
            return

        print(f"\nCandidates remaining: {len(candidates)}")
        if len(candidates) <= 25:
            print(", ".join(sorted(candidates)))

        freq_top = sort_words(candidates)[:5]
        print("\nTop 5 by frequency:", freq_top)
        best = pick_best_hard_mode_guess(candidates, prefer_entropy=True)
        ranked = rank_candidates_by_entropy(candidates)[:5]
        pretty_ranked = [f"{w} (H={ent:.3f})" for w, ent, _ in ranked]

        print("\nBest next guess:", best)
        print("Top 5 by entropy:", pretty_ranked)

        if len(candidates) == 1:
            print("\nOnly one candidate remains. Play:", candidates[0])

    print("\nOut of attempts!")


if __name__ == "__main__":
    main()
