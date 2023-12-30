from itertools import combinations

def load_words(file_path):
    with open(file_path, "r") as f:
        return f.read().split('\n')

def word_letter_sets(words):
    return {word: set(word) for word in words}

def find_combination(words):
    word_sets = word_letter_sets(words)
    best_combo = None
    first_word = 'crane'
    second_word = 'blyth'
    remaining_words = [w for w in words if not word_sets[w] & (word_sets[first_word] | word_sets[second_word])]
    for combo in combinations(remaining_words, 3):
        if best_combo == None or len(set(''.join((first_word, second_word,*combo)))) > len(set(''.join(best_combo))):
            best_combo = (first_word, second_word, *combo)
            alpha = [i for i in list('abcdefghijklmnopqrstuvwxyz') if i not in list(set(''.join((first_word, second_word,*combo))))]
            alpha.sort()
            print((first_word, second_word, *combo), len(set(''.join((first_word, second_word,*combo)))),'Missing:',alpha)
        combined_set = word_sets[first_word].union(*[word_sets[w] for w in combo])
        if len(combined_set) == 25:
            return (first_word, second_word, *combo)
    return None

# Load words from file
words = load_words("uniques.txt")

# Find the combination
combo = find_combination(words)
if combo:
    print("Found combination:", combo)
else:
    print("No combination found.")
