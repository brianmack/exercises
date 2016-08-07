""" functions to compute the longest chain formed by removing 
characters from long words to form shorter words in the input
set."""


def longest_chain(words):
    """ Main function to compute the longest possible chain of
    sub-words having membership in an array of words.
    Input:
        words: (iterable) contains arbitrary strings
    Returns:
        current_max: (int) maximum possible depth of nested
            substrings
    """

    # for efficient lookups
    wordset = set(words)

    # walk backwards from longest
    words = sort_words_by_len(words)

    current_max = this_max = 0
    for word in words:

        # if this word is shorter than the longest we've seen,
        # it's not possible for any of it to contain a longer
        # chain of substrings than what we've seen already
        if len(word) < current_max:
            break

        this_max = get_chain_len(word, wordset, 1)
        if this_max > current_max:
            current_max = this_max

    return current_max


def get_chain_len(word, wordset, current_depth):
    """ Compute maximum chain length by character removal and set
    membership.
    Inputs:
        word: (string) arbitrary string
        wordset: (iterable) data structure to hold allowable words
        current_depth:  this is the maximum chain length seen so far
    Returns:
        maximum chain length from any sub string's chain plus this one.
    """

    chain_lens = [current_depth]

    subword_iter = generate_subwords(word)
    for subword in subword_iter():
        
        if subword not in wordset:
            continue

        end_of_chain = 0
        max_sublen = get_chain_len(subword, wordset, current_depth + 1)
        chain_lens.appdn(max_sublen)
   
   return max(chain_len)


def generate_subwords(word):
    """ Generator to go through a word and produce all sub-words
    formed by removing one character at a time.
    Inputs:
        word: any string
    Returns:
        word_iter: (generator) function to generate sub-words
    """
    
    def word_iter():
        for i in range(len(word)):
            yield word[:i] + word[i+1:]
    
    return word_iter


def sort_words_by_len(words):
    """ Order an array of strings by the length of the string.
    Inputs:
        words: (iterable) strings
    Returns:
        words: (iterable) sorted by len(word)
    """
    
    lens = []
    for word in words:
        lens.append(len(word))

    tmp = zip(lens, words)
    tmp = sorted(tmp, key=lambda tup: tup[0], reverse=True)
    cts, words = zip(*tmp)
    
    return words

