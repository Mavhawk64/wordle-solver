class Wordle(object):
    """docstring for Wordle"""

    def __init__(self):
        self.generate_word()
        self.guesses = []

    def check(self, guess):
        # 0. check if guess == word -> return [2, 2, 2, 2, 2] else proceed to step 1
        # 1. check if x[i] == y[i] -> if so, assign 2 to z[i] and set y[i] = "#" and x[i] = "#"
        # 2. check if y[i] is in x and is not "#" -> if so, assign 1 to z[i] and set y[i] = "#"
        x = list(self.word)
        y = list(guess)
        z = [0, 0, 0, 0, 0]

        if self.word == guess:
            return [2, 2, 2, 2, 2]

        for i in range(0, len(x)):
            if x[i] == y[i]:
                x[i] = "#"
                y[i] = "#"
                z[i] = 2

        for i in range(0, len(y)):
            if y[i] in x and y[i] != "#":
                x[x.index(y[i])] = "#"
                y[i] = "#"
                z[i] = 1

        return z

    def new_guess(self, guess):
        self.guesses.append(guess)
        c = self.check(guess)
        if c == [2, 2, 2, 2, 2]:
            print("[" + "][".join(list(self.word)) + "]")
            return True

        if len(self.guesses) > 5:
            return False

        s = ''
        for i in range(0, len(c)):
            if c[i] == 0:
                s += '(' + guess[i] + ') '
            elif c[i] == 1:
                s += "*" + guess[i] + "* "
            else:
                s += "[" + guess[i] + "] "
        print(s)

        return None

    def generate_word(self):
        import random
        f = open("fives.txt", "r")
        self.word = random.choice(f.read().split('\n')).upper()
        f.close()

    def get_instructions(self):
        return "Welcome to Wordle!\nWordle is a 5-letter game, where you try to find out the word in as few guesses as possible.\nYou will be given a hint after each guess,\nsignified by\n\t(A) for a letter that is not in the word,\n\t*A* for a letter that is in the word but not in the correct position, and\n\t[A] for a letter that is in the correct position.\nYou have 5 guesses to find the word.\nGood luck!"


game = Wordle()
print(game.get_instructions())

while True:
    guess = input("Guess a word! ").upper()
    if len(guess) != 5 or not guess.isalpha():
        print("Please enter a valid word of length 5!")
        continue
    state = game.new_guess(guess)
    if state == True:
        print("CONGRATULATIONS!")
        break
    if state == False:
        print("Too bad... the correct word was " + game.word)
        break
