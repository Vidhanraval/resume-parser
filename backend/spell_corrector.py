from Levenshtein import distance

def correct_spelling(word, vocabulary, max_distance=1):
    best_match = None
    min_dist = max_distance + 1

    for vocab_word in vocabulary:
        d = distance(word, vocab_word)
        if d < min_dist:
            min_dist = d
            best_match = vocab_word

    if min_dist <= max_distance:
        return best_match

    return None
