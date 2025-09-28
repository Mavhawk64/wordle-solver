import json
from typing import List, Tuple


def sort_words(word_list):
    x = json.load(open("total.json"))
    max_val = max(x["letters"].values())
    x["letters"] = {
        k: v / max_val for k, v in x["letters"].items()
    }  # Normalized letter frequencies.
    # print(x)
    return [
        s
        for s, _ in sorted(
            [score_word(word, x["letters"]) for word in word_list],
            key=lambda y: y[1],
            reverse=True,
        )
    ]


def sort_words2(word_list):
    x = json.load(open("total.json"))
    max_val = max(x["letters"].values())
    x["letters"] = {
        k: v / max_val for k, v in x["letters"].items()
    }  # Normalized letter frequencies.
    with open("word_frequencies.csv", "r") as f:
        lines = f.read().splitlines()
        x["words"] = {
            line.split(",")[0]: float(line.split(",")[1]) for line in lines[1:]
        }
    return [
        s
        for s, _ in sorted(
            [score_word2(word, x["letters"], x["words"]) for word in word_list],
            key=lambda y: y[1],
            reverse=True,
        )
    ]


def score_word(word, lfreq):
    return word, sum(lfreq.get(letter, 0) for letter in word) * (
        1 + 0.20 * (len(set(word)) == 5)
    )


def score_word2(word, lfreq, wfreq):
    return word, sum(lfreq.get(letter, 0) for letter in word) * (
        1 + 0.20 * (len(set(word)) == 5)
    ) + 1e2 * wfreq.get(word, 0)


def filter_words(word_list, not_removed_letters):
    return [word for word in word_list if not_removed(word, not_removed_letters)]


def solvable_words(word_list, letters, positions: List[Tuple[str, int, bool]]):
    return sort_words2(
        [word for word in word_list if found_letters(word, letters, positions)]
    )


def not_removed(w, letters):
    return all(letter not in w for letter in letters)


def found_letters(w, letters, positions: List[Tuple[str, int, bool]]):
    return all(letter in w for letter in letters) and all(
        w[positions[i][1]] == positions[i][0]
        if positions[i][2]
        else w[positions[i][1]] != positions[i][0]
        for i in range(len(positions))
    )


if __name__ != "__main__":
    # Example usage
    with open("fives.txt", "r") as f:
        words = f.read().splitlines()
    filtered_words = filter_words(words, not_removed_letters="ars")
    # print("Filtered words:", filtered_words)
    sorted_words = sort_words(filtered_words)
    print(sorted_words[:5])  # Get top 5 words based on frequency scores.
    solvable = solvable_words(
        sorted_words, letters="oe", positions=[("o", 2, True), ("e", 4, False)]
    )
    print(
        "Solvable words:", solvable[: min(len(solvable), 5)]
    )  # Get top 5 solvable words.

if __name__ == "__main__":
    with open("fives.txt", "r") as f:
        words = f.read().splitlines()
    positions_list = []
    not_removed_letters = ""
    letters = ""
    for i in range(6):
        print(f"Attempt {i + 1}/6")
        user_input = input("Enter your word: ").strip().lower()

        cnt = 0
        for j, ch in enumerate(user_input):
            status = (
                input(
                    f"Is the letter '{ch}' in the correct position {j + 1}? (y/n) or 'x' if not in word: "
                )
                .strip()
                .lower()
            )
            if status == "y":
                letters += ch
                positions_list.append((ch, j, True))
                cnt += 1
            elif status == "n":
                letters += ch
                positions_list.append((ch, j, False))
            elif status == "x":
                not_removed_letters += ch
        if cnt == 5:
            print("Congratulations! You've guessed the word!")
            break
        filtered_words = filter_words(words, not_removed_letters=not_removed_letters)
        # print("Filtered words:", filtered_words)
        sorted_words = sort_words(filtered_words)
        print(sorted_words[:5])  # Get top 5 words based on frequency scores.
        solvable = solvable_words(
            sorted_words, letters=letters, positions=positions_list
        )
        print(
            "Solvable words:", solvable[: min(len(solvable), 5)]
        )  # Get top 5 solvable words.
