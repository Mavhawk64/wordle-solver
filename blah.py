with open("combined_counts.csv", "r") as f:
    lines = f.read().splitlines()
    with open("fives.txt", "r") as g:
        word_list = g.read().splitlines()
    max_val = 0
    for line in lines:
        word, count = line.split(",")
        word = word.strip().lower()
        count = int(count) if word in word_list else 0
        if count > max_val:
            max_val = count
    with open("word_frequencies.csv", "w") as h:
        h.write("word,frequency\n")
        for line in lines:
            word, count = line.split(",")
            word = word.strip().lower()
            count = int(count) if word in word_list else 0
            if count == 0:
                continue
            normalized_count = count / max_val
            h.write(f"{word},{normalized_count:.12f}\n")
