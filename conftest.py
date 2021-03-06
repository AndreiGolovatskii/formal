def rec_build(prefix, remainder_len, sigma, words):
    if remainder_len == 0:
        words.append("".join(prefix))
        return
    for letter in sigma:
        prefix.append(letter)
        rec_build(prefix, remainder_len - 1, sigma, words)
        prefix.pop()


def words_fixed_len_generator(word_len, sigma):
    words = []
    prefix = []
    rec_build(prefix, word_len, sigma, words)
    return words


def words_generator(max_len, sigma):
    words = []
    for cur_len in range(1, max_len + 1):
        words += words_fixed_len_generator(cur_len, sigma)
    return words


def assert_compare_fa(first, second, word_len):
    assert first.sigma == second.sigma
    for word in words_generator(word_len, first.sigma):
        assert first.accept(word) == second.accept(word)
