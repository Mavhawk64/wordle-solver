with open("uniques.txt","r") as f:
    f = f.read().split('\n')
    # remove all words with more than one vowel
    f = [w for w in f if len([c for c in w if c in 'aeiouy']) == 1]
    # write to single_vowel.txt
    with open("single_vowel.txt","w") as g:
        g.write('\n'.join(f))