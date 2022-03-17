def get_top_five(x):
	return get_top(x,5)

def get_top(x,n):
	names = list(x.keys())
	values = list(x.values())
	stillGoing = True

	while stillGoing:
		stillGoing = False
		for i in range(1,len(values)):
			if values[i-1] < values[i]:
				temp = values[i-1]
				values[i-1] = values[i]
				values[i] = temp
				temp = names[i-1]
				names[i-1] = names[i]
				names[i] = temp
				stillGoing = True
				break
	d = dict()
	for i in range(0,min(n,len(values))):
		d[names[i]] = values[i]
	return d

def sort(x):
	names = list(x.keys())
	values = list(x.values())
	stillGoing = True

	while stillGoing:
		stillGoing = False
		for i in range(1,len(values)):
			if values[i-1] < values[i]:
				temp = values[i-1]
				values[i-1] = values[i]
				values[i] = temp
				temp = names[i-1]
				names[i-1] = names[i]
				names[i] = temp
				stillGoing = True
				break
	d = dict()
	for i in range(0,len(values)):
		d[names[i]] = values[i]
	return d

def sort_names(names,values):
	stillGoing = True
	while stillGoing:
		stillGoing = False
		for i in range(1, len(values)):
			if values[i-1] < values[i]:
				temp = values[i-1]
				values[i-1] = values[i]
				values[i] = temp
				temp = names[i-1]
				names[i-1] = names[i]
				names[i] = temp
				stillGoing = True
				break
	return names


import matplotlib.pyplot as plt

# f = open("english3.txt","r").read().split('\n')
# g = open("fives.txt","w")
# for word in f:
# 	if len(word) == 5:
# 		g.write(word + "\n")


# f = open("fives.txt","r").read().split('\n')
# g = open("uniques.txt","w")
# for i in f:
# 	letters = []
# 	for j in i:
# 		if j not in letters:
# 			letters.append(j)
# 		else:
# 			break
# 	if ''.join(letters) == i:
# 		g.write(i + "\n")


# Generated some useful files - english3.txt has all words in dictionary, fives.txt has all 5-lettered words, and uniques.txt has all 5-lettered words that don't repeat the same letter (each letter used once)

# Analyze the counts and positions of each letter from fives.txt
dictionaries = [dict(),dict(),dict(),dict(),dict()]
totals = dict()
for i in range(97,97+26):
	dictionaries[0][chr(i)] = 0
	dictionaries[1][chr(i)] = 0
	dictionaries[2][chr(i)] = 0
	dictionaries[3][chr(i)] = 0
	dictionaries[4][chr(i)] = 0
	totals[chr(i)] = 0
# This is a set of dictionaries representing the frequencies of each positional letter

f = open("fives.txt","r").read().split('\n')[:-1]

for word in f:
	for i in range(0,5):
		dictionaries[i][word[i]] += 1
		totals[word[i]] += 1
# print(get_top_five(totals))

# for i in dictionaries:
	# print(get_top_five(i))

# print(sort(totals))

index = 1
for letters in dictionaries:
	names = list(letters.keys())
	values = list(letters.values())
	plt.figure()
	plt.title(f"Position {index}")
	plt.bar(range(len(letters)), values, tick_label=names)
	index += 1

names = list(totals.keys())
values = list(totals.values())
plt.figure()
plt.title("Total Frequency")
plt.bar(range(len(totals)), values, tick_label=names)


# positional_letters = []
# for i in dictionaries:
# 	t = get_top_five(i)
# 	for l in t:
# 		if l not in positional_letters:
# 			positional_letters.append(l)
# print(positional_letters)

# pos_words = []

# for word in f:
# 	count = 0
# 	used = []
# 	for letter in word:
# 		if letter in positional_letters and letter not in used:
# 			count += 1
# 			used.append(letter)
# 	if count == 5:
# 		pos_words.append(word)
# print(len(pos_words)) # 1196 words


# Only allow adjacent swap between position 2 and position 3 - closer distribution
pos2d = []
n = 4 # 4 gives 42 words, 5 gives 135 words
for i in dictionaries:
	t = get_top(i,n)
	pos2d.append([])
	for l in t:
		pos2d[-1].append(l)
# print(pos2d)

pos_word_list = []

u = open("uniques.txt","r").read().split('\n')

for word in u:
	if word[0] in pos2d[0] and (word[1] in pos2d[1] or word[1] in pos2d[2]) and (word[2] in pos2d[1] or word[2] in pos2d[2]) and word[3] in pos2d[3] and word[4] in pos2d[4]:
		pos_word_list.append(word)
# print(pos_word_list)
# print(len(pos_word_list)) # 4 gives 42 words, 5 gives 135 words


# apply ordering - sum up their counts in given position and sort - middle will be max(position 2, position 3)
sums = []
for word in pos_word_list:
	sums.append(dictionaries[0][word[0]] + max(dictionaries[1][word[1]],dictionaries[2][word[1]]) + max(dictionaries[1][word[2]],dictionaries[2][word[2]]) + dictionaries[3][word[3]] + dictionaries[4][word[4]])
# print(sums)
sorts = sort_names(pos_word_list,sums)
print(sorts)















plt.show(block=False)
plt.pause(10)
plt.close()