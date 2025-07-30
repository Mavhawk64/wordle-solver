import json


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


def filter_words(word_list):
    return [word for word in word_list if not_removed(word)]


def solvable_words(word_list):
    return sort_words2([word for word in word_list if found_letters(word)])


# user-defined (only removed letters)
def not_removed(w):
    letters = "rscn"
    return all(letter not in w for letter in letters)


def found_letters(w):
    letters = "aoe"
    return (
        all(letter in w for letter in letters)
        and w[0] != "a"
        and w[2] != "o"
        and w[4] != "e"
        and w[0] == "o"
        and w[2] == "e"
        and w[3] != "a"
    )


if __name__ == "__main__":
    # Example usage
    with open("fives.txt", "r") as f:
        words = f.read().splitlines()
    filtered_words = filter_words(words)
    # print("Filtered words:", filtered_words)
    sorted_words = sort_words(filtered_words)
    print(sorted_words[:5])  # Get top 5 words based on frequency scores.
    solvable = solvable_words(sorted_words)
    print(
        "Solvable words:", solvable[: min(len(solvable), 5)]
    )  # Get top 5 solvable words.
