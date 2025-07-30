class Guess(object):
    def __init__(self, guess: str):
        self.guess = guess
        self.avg_score = 0.0
        self.score = 0

    def check_guess(self, word):
        c = [
            (
                0
                if list(self.guess)[i] not in word
                else (1 if list(self.guess)[i] != list(word)[i] else 2)
            )
            for i in range(5)
        ]

        letters_in = set(self.guess) & set(word)
        letters_out = set(self.guess) - letters_in

        return (
            c,
            "".join(list(letters_in)),
            "".join(list(letters_out)),
        )  # guess="arose", word="crane" -> ([1,2,0,0,2], 'are', 'os')

    def filter_words(self, word_list, x):
        return [word for word in word_list if self.not_removed(word, x)]

    def solvable_words(self, word_list, c, gy):
        return [word for word in word_list if self.found_letters(word, c, gy)]

    # user-defined (only removed letters)
    def not_removed(self, w, letters):
        return all(letter not in w for letter in letters)

    def found_letters(self, w, pos, letters):
        g = (
            (w[0] == self.guess[0] or pos[0] != 2)
            and (w[1] == self.guess[1] or pos[1] != 2)
            and (w[2] == self.guess[2] or pos[2] != 2)
            and (w[3] == self.guess[3] or pos[3] != 2)
            and (w[4] == self.guess[4] or pos[4] != 2)
        )
        y = (
            (w[0] != self.guess[0] or pos[0] != 1)
            and (w[1] != self.guess[1] or pos[1] != 1)
            and (w[2] != self.guess[2] or pos[2] != 1)
            and (w[3] != self.guess[3] or pos[3] != 1)
            and (w[4] != self.guess[4] or pos[4] != 1)
        )
        return all(letter in w for letter in letters) and g and y

    def get_solvable(self, word_list, guess):
        c, gy, x = self.check_guess(guess)
        filtered = self.filter_words(word_list, x)
        solvable = self.solvable_words(filtered, c, gy)
        return solvable

    def doit(self, word_list):
        for guess in word_list:
            self.score += len(self.get_solvable(word_list, guess))
        self.avg_score = self.score / len(word_list) if word_list else 0
        return self.avg_score


with open("fives.txt", "r") as f:
    word_list = [line.strip() for line in f.readlines()]
    guess_list = [Guess(word) for word in word_list]
    # in between:
    with open("output.txt", "r") as file_1:
        lines = file_1.read().splitlines()
        for idx, line in enumerate(lines):
            word, avg_score, score = line.split(",")
            guess_list[idx].guess = word
            guess_list[idx].avg_score = float(avg_score)
            guess_list[idx].score = int(score)
        file_1.close()
    for word in guess_list:
        if word.avg_score == 0.0 or word.score == 0:
            print(word.guess, word.doit(word_list), word.score)
        else:
            print(word.guess, word.avg_score, word.score)
        open("output.txt", "w").write(
            "\n".join(f"{a.guess},{a.avg_score},{a.score}" for a in guess_list)
        )

    sorted_guesses = sorted(guess_list, key=lambda x: x.score, reverse=False)
    for guess in sorted_guesses[:5]:  # Print top 5 guesses
        print(
            f"Guess: {guess.guess}, Score: {guess.score}, Avg Score: {guess.avg_score}"
        )
