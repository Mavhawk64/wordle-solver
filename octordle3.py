from itertools import combinations

def load_words(file_path):
    with open(file_path, "r") as f:
        return f.read().split('\n')

def has_one_vowel(word):
    vowels = set("aeiouy")
    return sum(1 for letter in word if letter in vowels) == 1

def find_combination(words, first_word):
    words_with_one_vowel = [word for word in words if has_one_vowel(word)]
    best_combo = None
    best_count = 0

    used_letters = set(first_word)
    remaining_words = [w for w in words_with_one_vowel if not set(w).intersection(used_letters)]

    for combo in combinations(remaining_words, 4):
        full_combo = (first_word, *combo)
        combined_set = set(''.join(full_combo))
        unique_count = len(combined_set)

        if unique_count > best_count:
            best_combo = full_combo
            best_count = unique_count
            missing_letters = sorted(set("abcdefghijklmnopqrstuvwxyz") - combined_set)
            print(f"{best_combo} {unique_count}; Missing: {missing_letters}")

        if unique_count == 25:
            return best_combo

    return best_combo

# Load words from file
original_words = load_words("uniques.txt")
words = list(original_words)[34:]
the_best_combo = ('abysm', 'flick', 'phlox', 'veldt', 'wrung')
ties = [('abysm', 'flick', 'phlox', 'veldt', 'wrung'), ('admix', 'bergs', 'flown', 'klutz', 'psych'), ('adoze', 'blyth', 'flick', 'jumps', 'wring')]
ties.reverse()
# Find the combination with 'slate' as the first word
for w in range(original_words.index('adoze')+1,len(original_words)):
    i = original_words[w]
    words.remove(i)
    print(i)
    combo = find_combination(words, i)
    # if combo's letters > best_combo's letters
    if the_best_combo == None or (combo != None and len(set(''.join(combo))) > len(set(''.join(the_best_combo)))):
        the_best_combo = combo
        ties = [the_best_combo]
        print('NEW',end=' ')
    elif combo != None and len(set(''.join(combo))) == len(set(''.join(the_best_combo))):
        ties.append(combo)
        print('TIE',end=' ')
    print('best combo:')
    print(f"{the_best_combo} {len(set(''.join(the_best_combo)))}; Missing: {sorted(set('abcdefghijklmnopqrstuvwxyz') - set(''.join(the_best_combo)))}")
    print('TIES:')
    print(ties)

# load from total.json the frequencies
import json
with open('total.json') as f:
    data = json.load(f)
    # rank the ties by frequency
    print(data['letters']['a'])
    ties.sort(key=lambda x: sum([data['letters'][i] for i in set(''.join(x))]),reverse=True)
    print(ties)
    f.close()

print('BEST COMBO:', ties[0])