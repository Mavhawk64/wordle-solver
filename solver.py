f = open("fives.txt", "r")
g = f.read().split("\n")
for i in g:
    if (
        "e" not in i
        and "r" not in i
        and "a" not in i
        and "n" not in i
        and i[0] == "c"
        and i[1] == "o"
        and "u" not in i
        and "b" not in i
        and "t" not in i
        and "i" not in i
        and "l" not in i
        and "s" not in i
    ):
        print(i)

#
