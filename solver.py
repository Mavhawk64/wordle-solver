f = open("fives.txt","r")
g = f.read().split('\n')
for i in g:
    if i[4] == 'e' and 's' in i and 'k' in i and 't' in i and 'o' in i:
        print(i)

# 