import json
# Naive approach --> 10 words | max of 13 tries --> unacceptable
weight = 10
best_words = []
with open("uniques.txt", "r") as f:
    original_words = f.read().split('\n')
    words = list(original_words)
    available_letters = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','v','u','w','x','y','z']
    # we want to minimize the amount of words to span the entire alphabet
    # we have 6 json files; each letter position has a file: position#.json (1-5) which has a frequency list of all the letters that appear in that position; and total.json which has a frequency list of all the letters that appear in the entire word
    with open("position1.json", "r") as p1:
        position1 = json.loads(p1.read())
        with open("position2.json", "r") as p2:
            position2 = json.loads(p2.read())
            with open("position3.json", "r") as p3:
                position3 = json.loads(p3.read())
                with open("position4.json", "r") as p4:
                    position4 = json.loads(p4.read())
                    with open("position5.json", "r") as p5:
                        position5 = json.loads(p5.read())
                        with open("total.json", "r") as total:
                            total = json.loads(total.read())
                            y = 13
                            positions = [position1, position2, position3, position4, position5]
                            while len(available_letters) > 0:
                                if y == 0:
                                    break
                                y -= 1
                                # order the words by rank
                                # rank is determined by the weight*pos_frequency + total_frequency
                                # pos_frequency is the frequency of the letter in that position out of total amt letter occurrences
                                # total_frequency is the frequency of the letter in the entire word out of total amt letter occurrences
                                sorted_words = []
                                for word in words:
                                    rank = 0
                                    for i in range(0,5):
                                        if word[i] in available_letters:
                                            rank += weight*positions[i]["letters"][word[i]] / sum(positions[i]["letters"].values()) + total["letters"][word[i]] / sum(total["letters"].values())
                                    sorted_words.append((word,rank))
                                sorted_words.sort(key=lambda x: x[1], reverse=True)
                                print(available_letters)
                                if len(sorted_words) == 0 or len(sorted_words[0]) == 0:
                                    words = list(original_words)
                                    continue
                                rem_word = sorted_words[0][0]
                                print(rem_word)
                                best_words.append(rem_word)
                                # remove the letters from the available letters
                                for letter in rem_word:
                                    if letter in available_letters:
                                        available_letters.remove(letter)
                                # remove the word from the list of words
                                words.remove(rem_word)
                                # try removing all the words with the letters from rem_word
                                for word in list(words):
                                    if rem_word[0] in word or rem_word[1] in word or rem_word[2] in word or rem_word[3] in word or rem_word[4] in word:
                                        words.remove(word)
                                # remove the word letters from the position lists
                                for i in range(0,5):
                                    for letter in list(positions[i]["letters"].keys()):
                                        if letter in rem_word:
                                            positions[i]["letters"].pop(letter)
                                # remove the word letters from the total list
                                for letter in list(total["letters"].keys()):
                                    if letter in rem_word:
                                        total["letters"].pop(letter)

print("Length:\n",len(best_words),"\nList:\n",best_words)