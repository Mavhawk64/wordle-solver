# user-defined (only removed letters)
def not_removed(w):
    letters = "tyre"
    return all(letter not in w for letter in letters)


def found_letters(w):
    letters = "osin"
    return (
        all(letter in w for letter in letters)
        and w[3] not in ["o"]
        and w[4] == "s"
        and w[5] == "i"
        and w[6] not in ["n"]
    )


f = open("english3.txt", "r")
g = f.read().split("\n")
length = 8
g = [i for i in g if len(i) == length]
for i in g:
    if not_removed(i) and found_letters(i):
        print(i)
