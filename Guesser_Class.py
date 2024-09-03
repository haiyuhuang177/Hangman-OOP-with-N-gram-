import string
import random
from collections import Counter, defaultdict

class Guesser:
    def __init__(self):
        pass

    def guess(self, masked_word, guessed):
        pass

class HumanGuesser(Guesser):
    def guess(self, masked_word, guessed):
        print('\nEnter your guess:')
        return input().lower().strip()

class RandomGuesser(Guesser):
    def __init__(self):
        self.name = "random"

    def guess(self, masked_word, guessed):
        available = list(set(string.ascii_lowercase) - guessed)
        return random.choice(available)


class UnigramGuesser(Guesser):
    def __init__(self, by_length = False):
        self.name = "unigram"
        self.map = {}               # mapping letter to frequencies
        self.map_len = {}           # mapping length to letter frequencies
        self.char_prob = {}         # likelihood of each letter
        self.corpus = []            # may change if recalibrate = True
        self.original_corpus = []   # reset to the original corpus if recalibrate is turned on
        self.by_length = by_length  # whether or not to condition on length

    def upload(self, corpus):
        ''' store the original corpus '''
        self.original_corpus = corpus
        self.adapt(corpus)

    def adapt(self, corpus):
        ''' training the model on corpus '''
        self.corpus = corpus
        self.map = Counter()
        self.map_len = defaultdict(Counter)
        for word in corpus:
            length = len(word)
            for char in word:
                self.map[char] += 1
                self.map_len[length][char] += 1

    def recalibrate(self, masked_word, guessed):
        ''' update the dictionary after each guess '''
        incorrect = guessed - set(masked_word)
        self.corpus = [word for word in self.corpus if not set(word).intersection(incorrect)] #and bool(re.fullmatch("".join(masked_word).replace('_', '.'), word))]
        self.adapt(self.corpus)

    def update_prob(self, masked_word, guessed):
        ''' update the likelihood of each letter '''
        self.char_prob = {x : 0 for x in string.ascii_lowercase}
        if not self.by_length or len(masked_word) not in self.map_len.keys():
            curr_dict = self.map
        else:
            curr_dict = self.map_len[len(masked_word)]
        total_count = 0
        for char in self.char_prob:
            if char not in guessed:
                self.char_prob[char] = curr_dict[char]
                total_count += curr_dict[char]
        if total_count > 0:
            self.char_prob = {x : self.char_prob[x] / total_count for x in self.char_prob}

    def guess(self, masked_word, guessed):
        ''' return the most probable letter as the guess '''
        self.update_prob(masked_word, guessed)
        # in case char_prob is identically zero because the guesser has guessed all letters
        # (of a specific length) in the corpus
        if list(self.char_prob.values()) == [0] * len(self.char_prob):
            filtered = {x : self.char_prob[x] for x in self.char_prob if x not in guessed}
            return max(filtered, key = filtered.get)
        return max(self.char_prob, key=self.char_prob.get)


class BigramGuesser(Guesser):
    def __init__(self, by_length = False):
        self.name = "bigram"
        self.map = {}
        self.map_len = {}
        self.char_prob = {}
        self.by_length = by_length

    def adapt(self, corpus):
        self.map = defaultdict(Counter)
        self.map_len = defaultdict(lambda: defaultdict(Counter))
        for word in corpus:
            length = len(word)
            for i in range(length - 1):
                self.map[word[i]][word[i + 1]] += 1
                self.map_len[length][word[i]][word[i + 1]] += 1

    def update_prob(self, masked_word, guessed):
        self.char_prob = {x : 0 for x in string.ascii_lowercase}
        if not self.by_length or len(masked_word) not in self.map_len.keys():
            curr_dict = self.map
        else:
            curr_dict = self.map_len[len(masked_word)]
        total_count = 0
        for i in range(len(masked_word) - 1):
            if masked_word[i] == '_' and masked_word[i + 1] != '_':
                for char in self.char_prob:
                    if char not in guessed:
                        self.char_prob[char] += curr_dict[char][masked_word[i + 1]]
                        total_count += curr_dict[char][masked_word[i + 1]]
            if masked_word[i] != '_' and masked_word[i + 1] == '_':
                for char in self.char_prob:
                    if char not in guessed:
                        self.char_prob[char] += curr_dict[masked_word[i]][char]
                        total_count += curr_dict[masked_word[i]][char]
        if total_count > 0:
            self.char_prob = {x : self.char_prob[x] / total_count for x in self.char_prob}

def nested_defaultdict(n):
    return defaultdict(lambda: nested_defaultdict(n - 1)) if n > 0 else Counter()

class NgramGuesser(Guesser):
    def __init__(self, n, by_length = False):
        self.n = n
        self.name = f"{n}-gram"
        self.map = {}
        self.map_len = {}
        self.char_prob = {}
        self.corpus = []
        self.by_length = by_length

    def adapt(self, corpus):
        self.map = nested_defaultdict(self.n - 1)
        self.map_len = nested_defaultdict(self.n)
        for word in corpus:
            length = len(word)
            for i in range(length - self.n + 1):
                ngram_map = self.map
                ngram_map_len = self.map_len[length]
                for k in range(i, i + self.n - 1):
                    ngram_map = ngram_map[word[k]]
                    ngram_map_len = ngram_map_len[word[k]]
                ngram_map[word[i + self.n - 1]] += 1
                ngram_map_len[word[i + self.n - 1]] += 1


    def update_prob(self, masked_word, guessed):
        self.char_prob = {x : 0 for x in string.ascii_lowercase}
        if not self.by_length or len(masked_word) not in self.map_len.keys():
            curr_dict = self.map
        else:
            curr_dict = self.map_len[len(masked_word)]
        total_count = 0
        for i in range(len(masked_word) - self.n + 1):
            if masked_word[i: i + self.n].count('_') == 1:
                idx = masked_word[i: i + self.n].index('_')
                for char in self.char_prob:
                    if char not in guessed:
                        to_add = curr_dict
                        for k in range(i, i + self.n):
                            if k == i + idx:
                                to_add = to_add[char]
                            else:
                                to_add = to_add[masked_word[k]]
                        self.char_prob[char] += to_add
                        total_count += to_add

        if total_count > 0:
            self.char_prob = {x : self.char_prob[x] / total_count for x in self.char_prob}

class CombinationGuesser(Guesser):
    def __init__(self, guesser_list, weights):
        self.name = ""
        self.char_prob = {}
        self.corpus = []
        self.original_corpus = []
        self.guesser_list = guesser_list
        self.update_weights(weights)

    def upload(self, corpus):
        self.original_corpus = corpus
        self.corpus = corpus
        self.adapt(corpus)

    def adapt(self, corpus):
        self.corpus = corpus
        for guesser in self.guesser_list:
            guesser.adapt(corpus)

    def recalibrate(self, masked_word, guessed):
        incorrect = guessed - set(masked_word)
        self.corpus = [word for word in self.corpus if not set(word).intersection(incorrect)]# and bool(re.fullmatch("".join(masked_word).replace('_', '.'), word))]
        self.adapt(self.corpus)

    def update_by_length(self, lengths):
        for k in range(len(self.guesser_list)):
            self.guesser_list[k].by_length = lengths[k]
        self.update_name()

    def update_name(self):
        self.name = []
        for k in range(len(self.guesser_list)):
            self.name.append(f'{self.weights[k]} * {self.guesser_list[k].name}')
            if self.guesser_list[k].by_length:
                self.name[-1] += "(len)"
        self.name = " + ".join(self.name)

    def update_weights(self, weights):
        self.weights = weights
        self.update_name()

    def update_prob(self, masked_word, guessed):
        self.char_prob = {x : 0 for x in string.ascii_lowercase}
        for guesser in self.guesser_list:
            guesser.update_prob(masked_word, guessed)

    def guess(self, masked_word, guessed):
        self.update_prob(masked_word, guessed)
        for char in self.char_prob:
            for k in range(len(self.guesser_list)):
                self.char_prob[char] += self.guesser_list[k].char_prob[char] * self.weights[k]
        return max(self.char_prob, key=self.char_prob.get)
