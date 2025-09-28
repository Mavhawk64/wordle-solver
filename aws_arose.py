"""This program uses the advanced_solver to simulate all possible Wordle games, taking the top 1 guess from the advanced_solver each turn."""

import advanced_solver as aws


def color_word(guess, answer):
    colored = []
    answer_chars = list(answer)
    guess_chars = list(guess)

    # First pass for correct positions (green)
    for i in range(5):
        if guess_chars[i] == answer_chars[i]:
            colored.append(f"\033[92m{guess_chars[i].upper()}\033[0m")  # Green
            answer_chars[i] = None  # Mark this character as used
        else:
            colored.append(None)  # Placeholder for now

    # Second pass for present but wrong position (yellow) and absent (gray)
    for i in range(5):
        if colored[i] is None:  # Only process if not already colored green
            if guess_chars[i] in answer_chars:
                colored[i] = f"\033[93m{guess_chars[i].upper()}\033[0m"  # Yellow
                answer_chars[answer_chars.index(guess_chars[i])] = None  # Mark as used
            else:
                colored[i] = f"\033[90m{guess_chars[i].upper()}\033[0m"  # Gray

    return "".join(colored)


if __name__ == "__main__":
    unsolved_words = []
    scores = []
    with open("fives.txt", "r") as f:
        global_words = f.read().splitlines()
    for answer in global_words:
        with open("fives.txt", "r") as f:
            words = f.read().splitlines()
        positions_list = []
        not_removed_letters = ""
        letters = ""
        user_input = "arose"
        for i in range(6):
            print(f"Attempt {i + 1}/6")
            print(f"Guessing word: {color_word(user_input, answer)}")

            cnt = 0
            for j, ch in enumerate(user_input):
                status = "y" if answer[j] == ch else ("n" if ch in answer else "x")
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
                scores.append(i + 1)
                # print("Congratulations! You've guessed the word!")
                break
            filtered_words = aws.filter_words(
                words, not_removed_letters=not_removed_letters
            )
            # print("Filtered words:", filtered_words)
            sorted_words = aws.sort_words(filtered_words)
            # print(sorted_words[:5])  # Get top 5 words based on frequency scores.
            solvable = aws.solvable_words(
                sorted_words, letters=letters, positions=positions_list
            )
            # print(
            #     "Solvable words:", solvable[: min(len(solvable), 5)]
            # )  # Get top 5 solvable words.
            if len(solvable) == 0 or i == 5:
                print("Adding to unsolved words:", answer)
                unsolved_words.append(answer)
                scores.append(6 + len(solvable))
                break
            user_input = solvable[0]
    print("Unsolved words:", unsolved_words, len(unsolved_words))
    print("Solve rate:", (len(global_words) - len(unsolved_words)) / len(global_words))
    print("Average score:", sum(scores) / len(scores))
    print("Max score:", max(scores), global_words[scores.index(max(scores))])
